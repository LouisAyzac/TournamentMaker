from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Pool, Team, Player, Ranking
from faker import Faker
import random

class Command(BaseCommand):

    help = 'Génère 12 tournois (4 sports × 3 configurations) avec 2 équipes par poule'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        sports = ['football', 'volleyball', 'basketball']
        levels = [choice[0] for choice in Player.LEVEL_CHOICES]

        tournament_count = 1

        # Pour chaque sport
        for sport in sports:
            # Pour chaque configuration de nombre de poules (2, 3, 4)
            for num_pools in [2, 3, 4]:
                # Un tournoi par configuration
                tournament = Tournament.objects.create(
                    name=f"{sport.title()} Tournament {tournament_count}",
                    department=str(fake.random_int(min=1, max=95)).zfill(2),
                    address=fake.address(),
                    is_indoor=random.choice([True, False]),
                    start_date=fake.date_this_year(),
                    end_date=fake.date_this_year(),
                    sport=sport,
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
                        name=f"Poule {chr(65 + p_index)}",  # A, B, C, etc.
                        tournament=tournament,
                    )

                    for t_index in range(1, 3):  # 2 équipes par poule
                        team_name = f"{pool.name} - Équipe {t_index}"
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

                # Extraction des qualifiés (top 2 de chaque pool)
                qualified_teams = []
                for pool in Pool.objects.filter(tournament=tournament):
                    top2 = Ranking.objects.filter(team__pool=pool).order_by('rank')[:2]
                    qualified_teams.extend([r.team for r in top2])

                self.stdout.write(self.style.SUCCESS(
                    f"✅ {tournament.name} avec {num_pools} poules généré ({len(qualified_teams)} qualifiés)"
                ))
                tournament_count += 1

        self.stdout.write(self.style.SUCCESS("🎯 12 tournois générés avec succès."))
