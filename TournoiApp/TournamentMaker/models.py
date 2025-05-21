import random
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name

    def player_count(self):
        return self.players.count()

class Player(models.Model):
    LEVEL_CHOICES = [
        ('D', 'Débutant'),
        ('I', 'Intermédiaire'),
        ('A', 'Avancé'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Pool(models.Model):
    name = models.CharField(max_length=50)
    max_size = models.PositiveIntegerField(default=4)
    teams = models.ManyToManyField('Team', blank=True, related_name='pools')

    def __str__(self):
        return self.name

    def add_teams_randomly(self, teams_to_add):
        assigned_team_ids = set(
            Team.objects.filter(pools__isnull=False)
            .exclude(pools=self)
            .values_list('id', flat=True)
        )

        filtered_teams = [team for team in teams_to_add if team.id not in assigned_team_ids]

        teams_list = list(filtered_teams)
        random.shuffle(teams_list)
        for team in teams_list:
            self.teams.add(team)
        self.save()

    def list_teams(self):
        return self.teams.all()

    def all_matches_played(self):
        for match in self.matches.all():
            if match.winner() is None:
                return False
        return True

    def calculate_rankings(self):
        stats = {}
        for team in self.teams.all():
            stats[team.id] = {
                "team": team,
                "wins": 0,
                "sets_won": 0,
                "sets_lost": 0,
            }

        for match in self.matches.all():
            winner = match.winner()
            if not winner:
                continue

            loser = match.team_a if winner == match.team_b else match.team_b
            stats[winner.id]["wins"] += 1

            for i in range(1, 6):
                a_score = getattr(match, f"set{i}_team_a", None)
                b_score = getattr(match, f"set{i}_team_b", None)
                if a_score is not None and b_score is not None:
                    stats[match.team_a.id]["sets_won"] += a_score
                    stats[match.team_a.id]["sets_lost"] += b_score
                    stats[match.team_b.id]["sets_won"] += b_score
                    stats[match.team_b.id]["sets_lost"] += a_score

        sorted_teams = sorted(
            stats.values(),
            key=lambda x: (x["wins"], x["sets_won"] - x["sets_lost"]),
            reverse=True
        )

        for i, stat in enumerate(sorted_teams, start=1):
            Ranking.objects.update_or_create(
                team=stat["team"],
                defaults={"rank": i}
            )

class Match(models.Model):
    pool = models.ForeignKey('Pool', on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')

    en_cours = models.BooleanField(default=False)  # ✅ NOUVEAU CHAMP

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

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} (Pool: {self.pool.name if self.pool else 'No Pool'})"

    def winner(self):
        sets = [
            (self.set1_team_a, self.set1_team_b),
            (self.set2_team_a, self.set2_team_b),
            (self.set3_team_a, self.set3_team_b),
        ]

        if self.set4_team_a is not None and self.set4_team_b is not None:
            sets.append((self.set4_team_a, self.set4_team_b))
        if self.set5_team_a is not None and self.set5_team_b is not None:
            sets.append((self.set5_team_a, self.set5_team_b))

        score_a = 0
        score_b = 0

        for a, b in sets:
            if a > b:
                score_a += 1
            elif b > a:
                score_b += 1

        if score_a > score_b:
            return self.team_a
        elif score_b > score_a:
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
    pool = instance.pool
    if pool and pool.all_matches_played():
        pool.calculate_rankings()
