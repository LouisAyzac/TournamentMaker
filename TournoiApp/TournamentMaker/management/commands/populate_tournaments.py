from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Pool, Team, Player
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Génère 10 tournois avec 5 pools manuelles, chacune contenant 2 équipes nommées 1.1, 1.2, etc.'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        sports = [choice[0] for choice in Tournament.SPORT_CHOICES]
        levels = [choice[0] for choice in Player.LEVEL_CHOICES]

        for t_index in range(1, 11):  # Crée 10 tournois
            tournament = Tournament.objects.create(
                name=f"Tournament {t_index}",
                department=str(fake.random_int(min=1, max=95)).zfill(2),
                address=fake.address(),
                is_indoor=random.choice([True, False]),
                start_date=fake.date_this_year(),
                end_date=fake.date_this_year(),
                sport=random.choice(sports),
                max_teams=10,
                players_per_team=6,
                number_of_pools=6,  # mais on va les créer nous-mêmes
                type_tournament='RR',
                nb_sets_to_win=1,
                points_per_set=25
            )

            # Supprime les pools auto si créées par signal
            Pool.objects.filter(tournament=tournament).delete()

            for p_index in range(1, 7):
                pool = Pool.objects.create(
                    name=f"Pool {p_index}",
                    tournament=tournament,
                    max_size=2
                )

                # Créer 2 équipes nommées X.1 et X.2
                for team_num in range(1, 3):
                    team_name = f"{p_index}.{team_num}"
                    team = Team.objects.create(
                        name=team_name,
                        tournament=tournament,
                        pool=pool
                    )

                    # Ajouter les joueurs
                    for _ in range(tournament.players_per_team):
                        Player.objects.create(
                            first_name=fake.first_name(),
                            last_name=fake.last_name(),
                            birth_date=fake.date_of_birth(minimum_age=16, maximum_age=40),
                            level=random.choice(levels),
                            team=team,
                            email=fake.email()
                        )

            self.stdout.write(self.style.SUCCESS(f"✅ Tournoi {tournament.name} avec 5 pools créées manuellement."))

        self.stdout.write(self.style.SUCCESS("🎯 Tous les tournois ont été générés sans duplication de pools."))
