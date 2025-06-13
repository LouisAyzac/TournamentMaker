from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Pool, Team, Player
from faker import Faker
import random

class Command(BaseCommand):
<<<<<<< HEAD
    help = 'Génère des tournois, équipes et joueurs avec choix entre élimination directe ou tournois avec pools'
=======
    help = 'Génère des tournois, équipes et joueurs sans recréer les pools automatiquement créées'
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        sports = [choice[0] for choice in Tournament.SPORT_CHOICES]
        levels = [choice[0] for choice in Player.LEVEL_CHOICES]

<<<<<<< HEAD
        for _ in range(20):  # Crée un seul tournoi pour test, tu peux remettre 20 ensuite
            # Choisir aléatoirement entre élimination directe et tournois avec pools
            type_tournament = random.choice(['KO', 'RR'])
            number_of_pools = random.randint(1, 5) if type_tournament == 'RR' else 0

=======
        for _ in range(20):  # 👈 Crée un seul tournoi pour test, tu peux remettre 20 ensuite
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938
            tournament = Tournament.objects.create(
                name=fake.company() + ' Cup',
                department=str(fake.random_int(min=1, max=95)).zfill(2),
                address=fake.address(),
                is_indoor=random.choice([True, False]),
                start_date=fake.date_this_year(),
                end_date=fake.date_this_year(),
                sport=random.choice(sports),
                max_teams=random.randint(5, 10),
                players_per_team=random.randint(5, 12),
<<<<<<< HEAD
                number_of_pools=number_of_pools,
                type_tournament=type_tournament,
=======
                number_of_pools=random.randint(1, 5),
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938
                nb_sets_to_win=random.randint(2, 5),
                points_per_set=random.randint(15, 25)
            )

<<<<<<< HEAD
            if type_tournament == 'KO':
                self.stdout.write(self.style.SUCCESS(f"Tournoi {tournament.name} est une élimination directe."))
                continue

            # Récupérer les pools automatiquement créées
=======
            # ✅ Récupérer les pools automatiquement créées
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938
            pools = list(Pool.objects.filter(tournament=tournament))
            if not pools:
                self.stdout.write(self.style.ERROR("❌ Aucune pool trouvée après création du tournoi."))
                continue

<<<<<<< HEAD
            # Création des équipes réparties équitablement
=======
            # ✅ Création des équipes réparties équitablement
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938
            teams = []
            for i in range(tournament.max_teams):
                pool = min(pools, key=lambda p: p.teams.count())
                team = Team.objects.create(
                    name=fake.company() + f" Team {i + 1}",
                    tournament=tournament,
                    pool=pool,
                    captain=None
                )
                teams.append(team)

<<<<<<< HEAD
            # Génération des joueurs
=======
            # ✅ Génération des joueurs
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938
            for team in teams:
                num_players = random.randint(
                    int(tournament.players_per_team * 0.5), tournament.players_per_team
                )
                for _ in range(num_players):
                    Player.objects.create(
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        birth_date=fake.date_of_birth(minimum_age=10, maximum_age=40),
                        level=random.choice(levels),
                        team=team,
                        email=fake.email()
                    )

<<<<<<< HEAD
        self.stdout.write(self.style.SUCCESS('✅ Tournois, équipes et joueurs créés.'))
=======
        self.stdout.write(self.style.SUCCESS('✅ Tournois, équipes et joueurs créés (sans duplicata de pools).'))
>>>>>>> 3221afa099d43d35c1d2caf1ae35ab690d0f7938
