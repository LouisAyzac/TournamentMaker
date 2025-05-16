import random
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
    


class Match(models.Model):
    pool = models.ForeignKey('Pool', on_delete=models.CASCADE, related_name='matches', null=True, blank=True)
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_a')
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team_b')

    # Scores des sets (5 sets max, sets 4 et 5 optionnels)
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
        """
        Calcule le vainqueur en comptant les sets gagnés par chaque équipe.
        Renvoie team_a, team_b ou None si égalité/incomplet.
        """
        sets = [
            (self.set1_team_a, self.set1_team_b),
            (self.set2_team_a, self.set2_team_b),
            (self.set3_team_a, self.set3_team_b),
        ]

        # Ajouter sets 4 et 5 seulement s'ils ne sont pas None
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
    

