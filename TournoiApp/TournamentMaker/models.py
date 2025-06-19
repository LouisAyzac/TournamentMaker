import random
from datetime import date
from itertools import combinations

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.signals import request_finished
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import slugify

class Organisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Organisateur: {self.user.email}"

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
    department = models.CharField(max_length=100)
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
    organizer = models.OneToOneField(Organisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_tournament')
    match_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Durée d’un match (en minutes)")
    extra_time = models.BooleanField(null=True, blank=True, help_text="Prolongations possibles")
    penalty_shootout = models.BooleanField(null=True, blank=True, help_text="Tirs au but en cas d’égalité")
    half_time_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Durée de la mi-temps (en minutes)")
    quarter_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Durée d’un quart-temps (en minutes)")
    number_of_quarters = models.PositiveIntegerField(null=True, blank=True, help_text="Nombre de quart-temps")
    slug = models.SlugField(max_length=200, unique=False, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')
    captain = models.OneToOneField('UserProfile', on_delete=models.CASCADE, related_name='captained_team', null=True, blank=True)
    pool = models.ForeignKey('Pool', on_delete=models.SET_NULL, null=True, blank=True, related_name='teams')

    def __str__(self):
        return self.name

    def player_count(self):
        return self.players.count()

    def win_percentage(self):
        total_matches = self.matches_as_team_a.count() + self.matches_as_team_b.count()
        if total_matches == 0:
            return 0
        wins = 0
        for match in self.matches_as_team_a.all():
            if match.winner_team() == self:
                wins += 1
        for match in self.matches_as_team_b.all():
            if match.winner_team() == self:
                wins += 1
        return (wins / total_matches) * 100

    def get_last_results(self, n=5):
        matches = list(self.matches_as_team_a.all()) + list(self.matches_as_team_b.all())
        matches.sort(key=lambda x: x.id, reverse=True)
        results = []
        for match in matches[:n]:
            winner = match.get_match_winner()
            if winner == self:
                results.append('W')
            elif winner is None:
                results.append('D')
            else:
                results.append('L')
        return results


class Player(models.Model):
    LEVEL_CHOICES = [
        (1, 'Débutant'),
        (2, 'Intermédiaire'),
        (3, 'Avancé'),
        (4, 'Expert'),
        (5, 'Maître'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class Pool(models.Model):
    name = models.CharField(max_length=50)
    max_size = models.PositiveIntegerField(default=4)
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='pools',
        null=False,
        blank=False
    )

    def __str__(self):
        return f"{self.name} ({self.tournament.name})"


    def add_teams_randomly(self, teams_to_add):
        assigned_team_ids = set(
            Team.objects.filter(pools__isnull=False)
            .exclude(pools=self)
            .values_list('id', flat=True)
        )
        filtered_teams = [team for team in teams_to_add if team.id not in assigned_team_ids]
        teams_list = list(filtered_teams)
        random.shuffle(teams_list)
        available_slots = self.max_size - self.teams.count()
        for team in teams_list[:available_slots]:
            self.teams.add(team)
        self.save()

    def list_teams(self):
        return self.teams.all()

    def all_matches_played(self):
        nb_sets_to_win = self.tournament.nb_sets_to_win
        return all(match.get_match_winner() is not None for match in self.matches.all())
    
    def calculate_rankings(self):

        sport = self.tournament.sport
        stats = {
            team.id: {
                "team": team,
                "wins": 0,
                "sets_won": 0,
                "sets_lost": 0,
                "points_won": 0,
                "points_lost": 0,
                "draws": 0,
                "losses": 0,
                "sets_won": 0,
                "sets_lost": 0,
                "scored": 0,
                "conceded": 0,
            }
            for team in self.teams.all()
        }

        for match in self.matches.all():
            team_a = match.team_a
            team_b = match.team_b
            winner = match.get_match_winner()
            if not winner:
                continue

            # FOOT, RUGBY, BASKET
            if sport in ['football', 'rugby', 'basketball']:
                # Score total (additionne les quarts-temps ou mi-temps)
                score_a = sum([
                    match.set1_team_a or 0,
                    match.set2_team_a or 0,
                    match.set3_team_a or 0,
                    match.set4_team_a or 0,
                ])

                score_b = sum([
                    match.set1_team_b or 0,
                    match.set2_team_b or 0,
                    match.set3_team_b or 0,
                    match.set4_team_b or 0,
                ])

                stats[team_a.id]['scored'] += score_a
                stats[team_a.id]['conceded'] += score_b
                stats[team_b.id]['scored'] += score_b
                stats[team_b.id]['conceded'] += score_a

                if score_a > score_b:
                    stats[team_a.id]['wins'] += 1
                    stats[team_b.id]['losses'] += 1
                elif score_b > score_a:
                    stats[team_b.id]['wins'] += 1
                    stats[team_a.id]['losses'] += 1
                else:
                    stats[team_a.id]['draws'] += 1
                    stats[team_b.id]['draws'] += 1

            # VOLLEYBALL
            elif sport == 'volleyball':
                stats[winner.id]['wins'] += 1
                for i in range(1, 6):
                    a_score = getattr(match, f"set{i}_team_a", None)
                    b_score = getattr(match, f"set{i}_team_b", None)
                    if a_score is not None and b_score is not None:
                        stats[team_a.id]['sets_won'] += a_score
                        stats[team_a.id]['sets_lost'] += b_score
                        stats[team_b.id]['sets_won'] += b_score
                        stats[team_b.id]['sets_lost'] += a_score

            # Autres sports : gagne +1, pas de stats détaillées
            else:
                stats[winner.id]["wins"] += 1

        # Tri selon le sport
        if sport == 'volleyball':
            key_func = lambda x: (x["wins"], x["sets_won"] - x["sets_lost"], x["scored"] - x["conceded"])
        elif sport in ['football', 'rugby', 'basketball']:
            key_func = lambda x: (
                x["wins"] * 3 + x["draws"],  # Points (3 victoires, 1 nul)
                x["scored"] - x["conceded"],  # Différence de buts
                x["scored"]  # Buts marqués
            )
        else:
            key_func = lambda x: (x["wins"],)

        sorted_teams = sorted(stats.values(), key=key_func, reverse=True)

        for i, stat in enumerate(sorted_teams, start=1):
            Ranking.objects.update_or_create(
                team=stat["team"],
                defaults={"rank": i}
            )

class Match(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    pool = models.ForeignKey('Pool', on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a', null=True, blank=True)
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b', null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True, verbose_name="Heure de début")
    end_time = models.TimeField(null=True, blank=True, verbose_name="Heure de fin")
    bracket_position = models.PositiveIntegerField(null=True, blank=True)
    penalty_team_a = models.PositiveIntegerField(null=True, blank=True)
    penalty_team_b = models.PositiveIntegerField(null=True, blank=True)


    next_match = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_matches',
        help_text="Match suivant dans le bracket d'élimination"
    )

    STATUT_CHOICES = [
        ('ND', 'Non débuté'),
        ('EC', 'En cours'),
        ('T', 'Terminé'),
    ]
    statut = models.CharField(max_length=2, choices=STATUT_CHOICES, default='ND')

    TERRAIN_CHOICES = [(str(i), f'Terrain {i}') for i in range(1, 7)]
    terrain_number = models.CharField(max_length=1, choices=TERRAIN_CHOICES, blank=True, null=True, verbose_name="Terrain")

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

    PHASE_CHOICES = [
        ('pool', 'Phase de poule'),
        ('quarter', 'Quart de finale'),
        ('semi', 'Demi-finale'),
        ('final', 'Finale'),
        ('third_place', 'Petite finale'),
    ]
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default='pool')

    @property
    def winner_team(self):
        return self.get_match_winner()

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} (Pool: {self.pool.name if self.pool else 'No Pool'})"

    def is_match_complete(self):
        if not self.tournament:
            return False

        sport = self.tournament.sport

        if sport == 'volleyball':
            sets_to_win = self.tournament.nb_sets_to_win
            points_per_set = self.tournament.points_per_set
            sets_won_a = 0
            sets_won_b = 0

            for i in range(1, 6):
                sa = getattr(self, f"set{i}_team_a", None)
                sb = getattr(self, f"set{i}_team_b", None)

                if sa is None or sb is None:
                    continue

                if sa >= points_per_set and sa - sb >= 2:
                    sets_won_a += 1
                elif sb >= points_per_set and sb - sa >= 2:
                    sets_won_b += 1

            return sets_won_a >= sets_to_win or sets_won_b >= sets_to_win

        else:
            periods_filled = 0
            for i in range(1, 6):
                sa = getattr(self, f"set{i}_team_a", None)
                sb = getattr(self, f"set{i}_team_b", None)

                if sa is not None and sb is not None:
                    periods_filled += 1

            return periods_filled >= 2

    def get_match_winner(self):
        if not self.team_a or not self.team_b or not self.tournament:
            return None

        sport = self.tournament.sport

        if sport == 'volleyball':
            sets_to_win = self.tournament.nb_sets_to_win
            points_per_set = self.tournament.points_per_set

            sets_won_a = 0
            sets_won_b = 0

            for i in range(1, 6):
                sa = getattr(self, f"set{i}_team_a", None)
                sb = getattr(self, f"set{i}_team_b", None)

                if sa is None or sb is None or (sa == 0 and sb == 0):
                    continue

                if sa >= points_per_set and sa - sb >= 2:
                    sets_won_a += 1
                elif sb >= points_per_set and sb - sa >= 2:
                    sets_won_b += 1

            if sets_won_a >= sets_to_win:
                return self.team_a
            elif sets_won_b >= sets_to_win:
                return self.team_b
            else:
                return None

        elif sport == 'basketball':
            num_quarters = self.tournament.number_of_quarters or 4
            total_a, total_b = 0, 0
            for i in range(1, num_quarters + 1):
                sa = getattr(self, f"set{i}_team_a", None)
                sb = getattr(self, f"set{i}_team_b", None)
                if sa is not None and sb is not None:
                    total_a += sa
                    total_b += sb
                else:
                    return None
            return self.team_a if total_a > total_b else self.team_b if total_b > total_a else None

        total_a = 0
        total_b = 0

        for i in range(1, 6):
            sa = getattr(self, f"set{i}_team_a", None)
            sb = getattr(self, f"set{i}_team_b", None)

            if sa is not None and sb is not None:
                total_a += sa
                total_b += sb

        if total_a > total_b:
            return self.team_a
        elif total_b > total_a:
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
    if instance.pool and instance.pool.all_matches_played():
        instance.pool.calculate_rankings()


class UserProfile(models.Model):

    LEVEL_CHOICES = [
        (1, 'Débutant'),
        (2, 'Intermédiaire'),
        (3, 'Avancé'),
        (4, 'Expert'),
        (5, 'Maître'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    level = models.IntegerField(choices=LEVEL_CHOICES)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    def __str__(self):
        team_name = self.team.name if self.team else "Aucune équipe"  
        return f"{self.user.username} - {self.get_level_display()} (Équipe: {self.team.name})"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        pass



def generate_quarter_finals():
    pool_names = ['A', 'B', 'C', 'D']
    pools = {p.name: p for p in Pool.objects.filter(name__in=pool_names)}
    if len(pools) < 4 or not all(p.all_matches_played() for p in pools.values()):
        return
    if Match.objects.filter(phase='quarter').exists():
        return

    def top_two(pool): return Ranking.objects.filter(team__pools=pool).order_by('rank')[:2]
    r = {name: top_two(pools[name]) for name in pool_names}

    Match.objects.bulk_create([
        Match(pool=None, team_a=r['A'][0].team, team_b=r['D'][1].team, phase='quarter'),
        Match(pool=None, team_a=r['B'][0].team, team_b=r['C'][1].team, phase='quarter'),
        Match(pool=None, team_a=r['C'][0].team, team_b=r['B'][1].team, phase='quarter'),
        Match(pool=None, team_a=r['D'][0].team, team_b=r['A'][1].team, phase='quarter')
    ])


def assign_teams_to_pools(tournament):
    teams = list(tournament.teams.all())
    random.shuffle(teams)
    pool_names = ['A', 'B', 'C', 'D']
    pools = [Pool.objects.get_or_create(name=n, defaults={'max_size': 4})[0] for n in pool_names]
    for p in pools: p.teams.clear()
    for i, team in enumerate(teams):
        if i // 4 < len(pools):
            pools[i // 4].teams.add(team)
    for p in pools: p.save()


def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = Player.objects.filter(team=team)  # récupère les joueurs de cette équipe

    context = {
        'team': team,
        'players': players,
    }
    return render(request, 'team_detail.html', context)

class City(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100, default='')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=Tournament)
def create_pools_for_tournament(sender, instance, created, **kwargs):
    if created:
        print(f"Création de {instance.number_of_pools} pools pour le tournoi {instance.name}")
        for i in range(1, instance.number_of_pools + 1):
            pool_name = f"Pool {i}"
            pool = Pool.objects.create(name=pool_name, tournament=instance)
            print(f"Pool créée : {pool.name} pour le tournoi {instance.name}")


@receiver(post_save, sender=Team)
def auto_generate_pool_matches(sender, instance, **kwargs):
    pool = instance.pool
    if pool is None:
        return
    
    if instance.tournament.type_tournament != 'RR':
        return

    # Récupérer toutes les équipes de la pool
    teams = list(pool.teams.all())

    # Récupérer les matchs existants dans cette pool (phase 'pool')
    existing_matches = Match.objects.filter(pool=pool, phase='pool')
    existing_pairs = set()
    for m in existing_matches:
        pair = tuple(sorted([m.team_a.id, m.team_b.id]))
        existing_pairs.add(pair)

    # Pour chaque paire d’équipes
    for team_a, team_b in combinations(teams, 2):
        pair = tuple(sorted([team_a.id, team_b.id]))
        if pair not in existing_pairs:
            # Créer le match en base
            Match.objects.create(
                pool=pool,
                tournament=pool.tournament,
                team_a=team_a,
                team_b=team_b,
                phase='pool',
            )
            print(f"Match créé : {team_a.name} vs {team_b.name} dans {pool.name}")