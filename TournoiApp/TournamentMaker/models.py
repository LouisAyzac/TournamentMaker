# models.py  (version mise à jour)

import random
from datetime import date
from itertools import combinations

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


# ------------------------------------------------------------------
#  TOURNOI – Équipes – Joueurs
# ------------------------------------------------------------------

class Tournament(models.Model):
    SPORT_CHOICES = [
        ('football', 'Football'),
        ('volleyball', 'Volleyball'),
        ('basketball', 'Basketball'),
        ('rugby', 'Rugby'),
    ]
    TOURNAMENT_TYPE_CHOICES = [
        ('RR', 'Round Robin'),
        ('DE', 'Direct Elimination'),
    ]

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_indoor = models.BooleanField(default=True)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    sport = models.CharField(max_length=50, choices=SPORT_CHOICES, default='football')
    max_teams = models.PositiveIntegerField(default=8)
    players_per_team = models.PositiveIntegerField(default=5)
    number_of_pools = models.IntegerField(default=0)
    type_tournament = models.CharField(max_length=2, choices=TOURNAMENT_TYPE_CHOICES, default='RR')

    nb_sets_to_win = models.PositiveIntegerField(default=3, help_text="Nombre de sets nécessaires pour gagner un match")
    points_per_set = models.PositiveIntegerField(default=25, help_text="Nombre de points nécessaires pour gagner un set")

    def __str__(self):
        return self.name


class Pool(models.Model):
    name       = models.CharField(max_length=50)
    max_size   = models.PositiveIntegerField(default=4)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='pools')

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"

    # --- utilitaires ------------------------------------------------
    def all_matches_played(self):
        """True si toutes les rencontres de la poule ont un vainqueur."""
        return all(m.get_auto_winner() for m in self.matches.all())

    def calculate_rankings(self):
        """Met à jour/insère les lignes Ranking pour cette poule."""
        stats = {
            t.id: {"team": t, "wins": 0, "sets_won": 0, "sets_lost": 0}
            for t in self.teams.all()
        }
        for match in self.matches.all():
            winner = match.get_auto_winner()
            if not winner:
                continue
            loser = match.team_a if winner == match.team_b else match.team_b
            stats[winner.id]["wins"] += 1

            for i in range(1, 6):
                a = getattr(match, f"set{i}_team_a")
                b = getattr(match, f"set{i}_team_b")
                if a is not None and b is not None:
                    stats[match.team_a.id]["sets_won"]  += a
                    stats[match.team_a.id]["sets_lost"] += b
                    stats[match.team_b.id]["sets_won"]  += b
                    stats[match.team_b.id]["sets_lost"] += a

        ordered = sorted(
            stats.values(),
            key=lambda x: (x["wins"], x["sets_won"] - x["sets_lost"]),
            reverse=True,
        )
        for pos, stat in enumerate(ordered, start=1):
            Ranking.objects.update_or_create(
                team=stat["team"], defaults={"rank": pos}
            )


class Team(models.Model):
    name        = models.CharField(max_length=100)
    tournament  = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    captain     = models.OneToOneField('UserProfile', on_delete=models.CASCADE,
                                       related_name='captained_team', null=True, blank=True)
    pool        = models.ForeignKey(Pool, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='teams')

    def __str__(self):
        return self.name

    # ────────────────  UTILITAIRES  ────────────────
    def player_count(self):
        """Nombre de joueurs inscrits dans l’équipe (utilisé par l’admin)."""
        return self.players.count()
    player_count.short_description = "Joueurs"

class Player(models.Model):
    LEVEL_CHOICES = [(i, label) for i, label in enumerate(
        ('Débutant', 'Intermédiaire', 'Avancé', 'Expert', 'Maître'), start=1)]

    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    level      = models.IntegerField(choices=LEVEL_CHOICES)
    team       = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    email      = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ------------------------------------------------------------------
#  MATCHES
# ------------------------------------------------------------------

class Match(models.Model):
    """Rencontre entre deux équipes."""

    # --- relations --------------------------------------------------
    pool   = models.ForeignKey(Pool, on_delete=models.CASCADE,
                               related_name='matches', null=True, blank=True)
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')

    # --- calendrier -------------------------------------------------
    round       = models.PositiveSmallIntegerField(default=1, help_text="Journée / tour")
    start_time  = models.TimeField(null=True, blank=True, verbose_name="Heure de début")
    end_time    = models.TimeField(null=True, blank=True, verbose_name="Heure de fin")

    # --- état -------------------------------------------------------
    class Status(models.TextChoices):
        NOT_STARTED = 'ND', 'Non débuté'
        LIVE        = 'EC', 'En cours'
        FINISHED    = 'T',  'Terminé'

    statut = models.CharField(max_length=2, choices=Status.choices,
                              default=Status.NOT_STARTED)

    TERRAIN_CHOICES = [(str(i), f'Terrain {i}') for i in range(1, 7)]
    terrain_number  = models.CharField(max_length=1, choices=TERRAIN_CHOICES,
                                       blank=True, null=True, verbose_name="Terrain")

    class Phase(models.TextChoices):
        GROUP        = 'pool',        'Phase de poule'
        QUARTERFINAL = 'quarter',     'Quart de finale'
        SEMIFINAL    = 'semi',        'Demi-finale'
        FINAL        = 'final',       'Finale'
        THIRD_PLACE  = 'third_place', 'Petite finale'

    phase = models.CharField(max_length=20, choices=Phase.choices,
                             default=Phase.GROUP)

    WINNER_CHOICES = [('A', 'Team A'), ('B', 'Team B')]
    winner_side    = models.CharField(max_length=1, choices=WINNER_CHOICES,
                                      blank=True, null=True, verbose_name='Vainqueur')

    @property
    def winner_team(self):
        return self.team_a if self.winner_side == 'A' else (
               self.team_b if self.winner_side == 'B' else None)

    # --- scores (set par set) ---------------------------------------
    set1_team_a = models.PositiveIntegerField(default=0)
    set1_team_b = models.PositiveIntegerField(default=0)
    set2_team_a = models.PositiveIntegerField(default=0)
    set2_team_b = models.PositiveIntegerField(default=0)
    set3_team_a = models.PositiveIntegerField(default=0)
    set3_team_b = models.PositiveIntegerField(default=0)
    set4_team_a = models.PositiveIntegerField(null=True, blank=True)
    set4_team_b = models.PositiveIntegerField(null=True, blank=True)
    set5_team_a = models.PositiveIntegerField(null=True, blank=True)
    set5_team_b = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('pool', 'team_a', 'team_b')  # évite les doublons dans une poule
        ordering = ('round', 'start_time', 'id')

    # ----------------------------------------------------------------
    #  Méthodes utilitaires
    # ----------------------------------------------------------------
    def __str__(self):
        pool_label = self.pool.name if self.pool else "hors poule"
        return f"{self.team_a} vs {self.team_b} – {pool_label}"

    def get_auto_winner(self):
        """Détermine le vainqueur en comptant le nombre de sets gagnés."""
        sets = [
            (self.set1_team_a, self.set1_team_b),
            (self.set2_team_a, self.set2_team_b),
            (self.set3_team_a, self.set3_team_b),
        ]
        if self.set4_team_a is not None and self.set4_team_b is not None:
            sets.append((self.set4_team_a, self.set4_team_b))
        if self.set5_team_a is not None and self.set5_team_b is not None:
            sets.append((self.set5_team_a, self.set5_team_b))

        score_a = sum(a > b for a, b in sets)
        score_b = sum(b > a for a, b in sets)

        if score_a > score_b:
            return self.team_a
        if score_b > score_a:
            return self.team_b
        return None

        if score_a >= nb_sets_to_win:
            return self.team_a
        elif score_b >= nb_sets_to_win:
            return self.team_b
        else:
            return None


class Ranking(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.team.name} - Rang {self.rank}"


@receiver(post_save, sender=Match)
def update_rankings_on_match_save(sender, instance, **kwargs):
    """Recalcule le classement de la poule lorsque tous les matches sont terminés."""
    if instance.pool and instance.pool.all_matches_played():
        instance.pool.calculate_rankings()


# ------------------------------------------------------------------
#  UTILISATEURS
# ------------------------------------------------------------------

class UserProfile(models.Model):
    LEVEL_CHOICES = [(i, label) for i, label in enumerate(
        ('Débutant', 'Intermédiaire', 'Avancé', 'Expert', 'Maître'), start=1)]

    user  = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL_CHOICES)

    # ➜ redeviens nullable
    team  = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members',
        null=True, blank=True,      #  ← ajoute ces deux attributs
    )

    def __str__(self):
        team_name = self.team.name if self.team else "Aucune équipe"
        return f"{self.user.username} - {self.get_level_display()} ({team_name})"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée un profil vide à la création d'un User (à compléter plus tard)."""
    if created:
        UserProfile.objects.create(user=instance, level=1, team=None)


# ------------------------------------------------------------------
#  VILLES (géolocalisation)
# ------------------------------------------------------------------

class City(models.Model):
    name       = models.CharField(max_length=100)
    department = models.CharField(max_length=100, default='')
    latitude   = models.FloatField(null=True, blank=True)
    longitude  = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


# ------------------------------------------------------------------
#  SIGNAUX : création automatique des poules
# ------------------------------------------------------------------

@receiver(post_save, sender=Tournament)
def create_pools_for_tournament(sender, instance, created, **kwargs):
    """Crée automatiquement les X poules définies sur le tournoi."""
    if created:
        for i in range(1, instance.number_of_pools + 1):
            Pool.objects.create(name=f"Pool {i}", tournament=instance)
