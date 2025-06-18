from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Team, Player
from TournamentMaker.views import generate_elimination_bracket
from faker import Faker
import random

class Command(BaseCommand):
<<<<<<< HEAD
    help = "Génère des tournois à élimination directe avec équipes et joueurs factices."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1, help="Nombre de tournois à générer")
        parser.add_argument('--teams', type=int, default=16, help="Nombre d'équipes par tournoi (max 32)")
        parser.add_argument('--players', type=int, default=6, help="Nombre de joueurs par équipe")

    def handle(self, *args, **options):
=======

    help = 'Génère 2 tournois pour chaque configuration de 2 à 8 poules avec 2 équipes par pool'
 
    def handle(self, *args, **kwargs):
>>>>>>> 727fdea0be79a0f1ebe347526df5effb8497def7
        fake = Faker('fr_FR')
        count = options['count']
        num_teams = min(options['teams'], 32)
        players_per_team = options['players']

<<<<<<< HEAD
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
                sport='volleyball',  # ou random.choice(...)
                max_teams=num_teams,
                players_per_team=players_per_team,
                number_of_pools=0,
                nb_sets_to_win=2,
                points_per_set=25
            )

            for t_index in range(num_teams):
                team = Team.objects.create(
                    name=fake.unique.company(),
                    tournament=tournament
                )

                for _ in range(players_per_team):
                    Player.objects.create(
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        birth_date=fake.date_of_birth(minimum_age=16, maximum_age=40),
                        level='MOY',
                        email=fake.email(),
                        team=team
                    )

            generate_elimination_bracket(tournament)
            self.stdout.write(self.style.SUCCESS(
                f"✅ {tournament.name} (slug: {tournament.slug}) – {num_teams} équipes – bracket généré"
            ))

        self.stdout.write(self.style.SUCCESS("🎯 Génération des tournois DE terminée."))
=======
        sports = [choice[0] for choice in Tournament.SPORT_CHOICES]
        levels = [choice[0] for choice in Player.LEVEL_CHOICES]
 
        tournament_count = 1
        for num_pools in range(2, 9):  # de 2 à 8 poules
            for _ in range(2):  # deux tournois par config
                tournament = Tournament.objects.create(
                    name=f"Tournament {tournament_count}",
                    department=str(fake.random_int(min=1, max=95)).zfill(2),
                    address=fake.address(),
                    is_indoor=random.choice([True, False]),
                    start_date=fake.date_this_year(),
                    end_date=fake.date_this_year(),
                    sport=random.choice(sports),
                    max_teams=num_pools * 2,
                    players_per_team=1,
                    number_of_pools=num_pools,
                    type_tournament='RR',
                    nb_sets_to_win=1,
                    points_per_set=25
                )

                # Supprimer toute pool auto
                Pool.objects.filter(tournament=tournament).delete()

                for p_index in range(num_pools):
                    pool = Pool.objects.create(
                        name=f"Pool {p_index}",
                        tournament=tournament,
                        max_size=2
                    )

                    for t_index in range(1, 3):  # 2 équipes
                        team_name = f"{p_index}.{t_index}"
                        team = Team.objects.create(
                            name=team_name,
                            tournament=tournament,
                            pool=pool
                        )
 
                        Player.objects.create(
                            first_name=fake.first_name(),
                            last_name=fake.last_name(),
                            birth_date=fake.date_of_birth(minimum_age=16, maximum_age=40),
                            level=random.choice(levels),
                            team=team,
                            email=fake.email()
                        )
 
                # Calcul des classements
                for pool in Pool.objects.filter(tournament=tournament):
                    pool.calculate_rankings()

                # Extraction des qualifiés
                qualified_teams = []
                for pool in Pool.objects.filter(tournament=tournament):
                    top2 = Ranking.objects.filter(team__pool=pool).order_by('rank')[:2]
                    qualified_teams.extend([r.team for r in top2])

                self.stdout.write(self.style.SUCCESS(
                    f"✅ {tournament.name} avec {num_pools} pools généré ({len(qualified_teams)} équipes qualifiées)"
                ))
                tournament_count += 1

        self.stdout.write(self.style.SUCCESS("🎯 Tous les tournois ont été générés avec succès."))
 
>>>>>>> 727fdea0be79a0f1ebe347526df5effb8497def7
