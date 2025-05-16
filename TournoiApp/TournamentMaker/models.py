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
    score_team_a = models.PositiveIntegerField(default=0)
    score_team_b = models.PositiveIntegerField(default=0)


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
    
import random
  

class Pool(models.Model):
    name = models.CharField(max_length=50)
    max_size = models.PositiveIntegerField(default=4)  # ou la valeur par défaut que tu veux

    teams = models.ManyToManyField('Team', blank=True, related_name='pools')

    def __str__(self):
        return self.name

    def add_teams_randomly(self, teams_to_add):
        """
        Ajoute une liste d'équipes à cette pool de façon aléatoire,
        uniquement si elles ne sont pas déjà dans une autre pool.
        """
        # Exclure les équipes déjà assignées à une pool différente
        assigned_team_ids = set(
            Team.objects.filter(pools__isnull=False)
            .exclude(pools=self)
            .values_list('id', flat=True)
        )
        
        # Filtrer pour garder que celles non assignées ailleurs
        filtered_teams = [team for team in teams_to_add if team.id not in assigned_team_ids]

        teams_list = list(filtered_teams)
        random.shuffle(teams_list)
        for team in teams_list:
            self.teams.add(team)
        self.save()

    def list_teams(self):
        """
        Retourne la liste des équipes dans cette pool.
        """
        return self.teams.all()