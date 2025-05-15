from django.db import models

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
        return self.players.count()  # related_name="players" dans Player


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


class Match(models.Model):
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')
    score_team_a = models.PositiveIntegerField()
    score_team_b = models.PositiveIntegerField()
    date_played = models.DateTimeField()

    def __str__(self):
        return f"{self.team_a} vs {self.team_b}"

    def winner(self):
        if self.score_team_a > self.score_team_b:
            return self.team_a
        elif self.score_team_b > self.score_team_a:
            return self.team_b
        return None  # match nul


class Ranking(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.team.name} - Rang {self.rank}"
