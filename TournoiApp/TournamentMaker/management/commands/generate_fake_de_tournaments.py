from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Team, Player
from faker import Faker
import random

class Command(BaseCommand):
    help = "Crée 5 tournois à élimination directe avec 2 à 6 équipes (1 tournoi par nombre d'équipes)."

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')
        players_per_team = 6  # fixe, ajustable

        for num_teams in range(2,9):  # Génère pour 2, 3, 4, 5, 6 équipes
            t_name = f"Tournoi DE {num_teams} équipes - {fake.city()}"
            t_slug = f"de-{num_teams}-{random.randint(1000, 9999)}"

            tournament = Tournament.objects.create(
                name=t_name,
                slug=t_slug,
                type_tournament='DE',
                department=str(fake.random_int(min=1, max=95)).zfill(2),
                address=fake.address(),
                is_indoor=random.choice([True, False]),
                start_date=fake.date_this_year(),
                end_date=fake.date_this_year(),
                sport='volleyball',
                max_teams=num_teams,
                players_per_team=players_per_team,
                number_of_pools=0,
                nb_sets_to_win=1,
                points_per_set=1
            )

            for _ in range(num_teams):
                team = Team.objects.create(
                    name=fake.unique.company(),
                    tournament=tournament
                )

                for _ in range(players_per_team):
                    Player.objects.create(
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        birth_date=fake.date_of_birth(minimum_age=16, maximum_age=40),
                        level=random.choice([choice[0] for choice in Player.LEVEL_CHOICES]),
                        email=fake.unique.email(),
                        team=team
                    )

            self.stdout.write(self.style.SUCCESS(
                f"✅ Tournoi créé : {tournament.name} ({tournament.slug}) avec {num_teams} équipes."
            ))
