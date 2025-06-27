from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Team, Player, Address, City
from faker import Faker
import random

class Command(BaseCommand):
    help = "Crée 5 tournois à élimination directe avec 2 à 8 équipes (1 tournoi par nombre d'équipes)."

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')
        players_per_team = 6

        real_addresses = []
        for _ in range(10):
            city_name = fake.city()
            postcode = fake.postcode()
            department = postcode[:2]
            street_name = f"{fake.building_number()} {fake.street_name()}"
            full_street = f"{street_name}, {postcode} {city_name}, France"

            city_obj, _ = City.objects.get_or_create(
                name=city_name,
                defaults={
                    'department': department,
                    'latitude': fake.latitude(),
                    'longitude': fake.longitude()
                }
            )

            address_obj = Address.objects.create(
                street=full_street,  # <- adresse complète formatée
                zipcode=postcode,
                city=city_obj,
                latitude=city_obj.latitude,
                longitude=city_obj.longitude
            )

            real_addresses.append({
                "address": address_obj,
                "department": department
            })

        for num_teams in range(2, 9):  # 2 à 8 équipes
            tournament_name = f"Tournoi DE {num_teams} équipes - {fake.city()}"
            tournament_slug = f"de-{num_teams}-{random.randint(1000, 9999)}"

            real_address = random.choice(real_addresses)

            tournament = Tournament.objects.create(
                name=tournament_name,
                slug=tournament_slug,
                type_tournament='DE',
                department=real_address["department"],
                address=real_address["address"],
                is_indoor=random.choice([True, False]),
                start_date=fake.date_this_year(before_today=True, after_today=False),
                end_date=fake.date_this_year(before_today=False, after_today=True),
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
