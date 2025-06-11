from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Pool, Team, Player, UserProfile
from django.contrib.auth.models import User
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Génère des tournois, équipes, joueurs et capitaines (avec User et UserProfile)'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        sports = [choice[0] for choice in Tournament.SPORT_CHOICES]
        levels = [choice[0] for choice in Player.LEVEL_CHOICES]

        for _ in range(10):  # Générer 10 tournois
            type_tournament = random.choice(['KO', 'RR'])
            number_of_pools = random.randint(1, 5) if type_tournament == 'RR' else 0

            # Création d'un tournoi
            tournament = Tournament.objects.create(
                name=fake.company() + ' Cup',
                city=fake.city(),
                address=fake.address(),
                is_indoor=random.choice([True, False]),
                start_date=fake.date_this_year(),
                end_date=fake.date_this_year(),
                sport=random.choice(sports),
                max_teams=random.randint(5, 10),
                players_per_team=random.randint(5, 12),
                number_of_pools=number_of_pools,
                type_tournament=type_tournament,
                nb_sets_to_win=random.randint(2, 5),
                points_per_set=random.randint(15, 25),
            )

            if type_tournament == 'KO':
                self.stdout.write(self.style.SUCCESS(f"Tournoi {tournament.name} est une élimination directe."))
                continue

            # Récupérer les pools automatiquement créées
            pools = list(Pool.objects.filter(tournament=tournament))
            if not pools:
                self.stdout.write(self.style.ERROR(f"❌ Aucun pool trouvé pour le tournoi {tournament.name}."))
                continue

            # Création des équipes et des joueurs
            for i in range(tournament.max_teams):
                # Assigner une pool avec le moins d'équipes
                pool = min(pools, key=lambda p: p.teams.count())

                # Création de l'équipe
                team = Team.objects.create(
                    name=fake.company() + f" Team {i + 1}",
                    tournament=tournament,
                    pool=pool,
                )

                # Création du capitaine
                captain_email = fake.email()
                captain_user = User.objects.create_user(
                    username=f"{captain_email.split('@')[0]}_{team.id}",
                    email=captain_email,
                    password='defaultpassword123'  # Mot de passe par défaut
                )

                captain_profile = UserProfile.objects.create(
                    user=captain_user,
                    level=random.choice(levels),
                    team=team
                )

                team.captain = captain_profile
                team.save()

                # Création des autres joueurs
                num_players = random.randint(
                    int(tournament.players_per_team * 0.5), tournament.players_per_team
                )

                for _ in range(num_players - 1):  # Le capitaine est déjà créé
                    Player.objects.create(
                        first_name=fake.first_name(),
                        last_name=fake.last_name(),
                        birth_date=fake.date_of_birth(minimum_age=10, maximum_age=40),
                        level=random.choice(levels),
                        email=fake.email(),
                        team=team,
                    )

        self.stdout.write(self.style.SUCCESS('✅ Tournois, équipes, joueurs et capitaines créés avec succès.'))
