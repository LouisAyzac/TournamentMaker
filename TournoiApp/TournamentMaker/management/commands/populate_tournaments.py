from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Pool, Team, Player, Ranking
from faker import Faker
import random

class Command(BaseCommand):

    help = 'Génère 2 tournois pour chaque configuration de 2 à 8 poules avec 2 équipes par pool'
 
    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        sports = ['football', 'volleyball', 'basketball']
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
                    
                    for t_index in range(1, 5):  # 2 équipes
                        
                        team_name = f"{p_index}.{t_index}"
                    for t_index in range(1, 3):  # 2 équipes par poule
                        team_name = f"{pool.name} - Équipe {t_index}"
                    for t_index in range(1, 3):  # 2 équipes par poule
                        team_name = f"{pool.name} - Équipe {t_index}"
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
 
