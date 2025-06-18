from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Team, Player
from faker import Faker
import random

class Command(BaseCommand):
    help = "Génère des tournois à élimination directe avec équipes et joueurs (pas de matchs/brackets)."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=3, help="Nombre de tournois à générer")
        parser.add_argument('--teams', type=int, default=16, help="Nombre d'équipes par tournoi")
        parser.add_argument('--players', type=int, default=6, help="Nombre de joueurs par équipe")

    def handle(self, *args, **options):
        fake = Faker('fr_FR')
        count = options['count']
        num_teams = options['teams']
        players_per_team = options['players']

        for i in range(count):
            t_name = f"Tournoi DE {fake.city()}"
            t_slug = f"de-{random.randint(1000, 9999)}"

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
                    # Dans la boucle Player.objects.create(...)
                    Player.objects.create(
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        birth_date=fake.date_of_birth(minimum_age=16, maximum_age=40),
                        level=random.choice([choice[0] for choice in Player.LEVEL_CHOICES]),  # ✅ fix ici
                        email=fake.email(),
                        team=team
                    )


            self.stdout.write(self.style.SUCCESS(
                f"✅ {tournament.name} ({tournament.slug}) – {num_teams} équipes créées."
            ))

        self.stdout.write(self.style.SUCCESS("🎯 Génération terminée sans création de matchs."))
