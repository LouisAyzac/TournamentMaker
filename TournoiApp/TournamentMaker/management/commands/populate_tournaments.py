from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Team, Player, City, Address
from django.utils.text import slugify
from faker import Faker
import random

CITY_ZONES = {
    "Paris": [
        {"zipcode": "75001", "lat": 48.8625, "lon": 2.3361, "area": "Louvre"},
        {"zipcode": "75011", "lat": 48.8566, "lon": 2.3789, "area": "Bastille"},
        {"zipcode": "75018", "lat": 48.8924, "lon": 2.3449, "area": "Montmartre"},
        {"zipcode": "75020", "lat": 48.8690, "lon": 2.4058, "area": "Belleville"},
    ],
    "Lyon": [
        {"zipcode": "69001", "lat": 45.7673, "lon": 4.8340, "area": "Croix-Rousse"},
        {"zipcode": "69003", "lat": 45.7574, "lon": 4.8595, "area": "Part-Dieu"},
        {"zipcode": "69007", "lat": 45.7427, "lon": 4.8445, "area": "Jean Macé"},
    ],
    "Marseille": [
        {"zipcode": "13001", "lat": 43.2965, "lon": 5.3700, "area": "Vieux-Port"},
        {"zipcode": "13006", "lat": 43.2840, "lon": 5.3810, "area": "Castellane"},
        {"zipcode": "13008", "lat": 43.2600, "lon": 5.3900, "area": "Prado"},
    ],
    "Bordeaux": [
        {"zipcode": "33000", "lat": 44.8378, "lon": -0.5792, "area": "Centre"},
        {"zipcode": "33100", "lat": 44.8570, "lon": -0.5400, "area": "Bastide"},
    ],
    "Lille": [
        {"zipcode": "59000", "lat": 50.6326, "lon": 3.0626, "area": "Centre"},
        {"zipcode": "59800", "lat": 50.6381, "lon": 3.0594, "area": "Wazemmes"},
    ],
}

class Command(BaseCommand):
    help = "Crée plusieurs tournois de volley avec quartiers variés."

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')
        players_per_team = 6
        teams_per_tournament = 8

        for city_name, zones in CITY_ZONES.items():
            for zone in zones:
                zipcode = zone["zipcode"]
                lat = zone["lat"] + random.uniform(-0.002, 0.002)
                lon = zone["lon"] + random.uniform(-0.002, 0.002)
                area = zone["area"]

                city, _ = City.objects.get_or_create(name=city_name)

                number = random.randint(1, 200)
                street = fake.street_name()
                suffix = fake.street_suffix()
                extra = random.choice(["Bâtiment A", "Bâtiment B", "Étage 2", "Hall Ouest", "Escalier C"])

                street_address = f"{number} {street} {suffix} – {area}, {extra}"

                address = Address.objects.create(
                    street=street_address,
                    city=city,
                    zipcode=zipcode,
                    latitude=lat,
                    longitude=lon
                )

                tournament_name = f"Volley - {city_name} ({area})"
                slug = slugify(tournament_name + "-" + str(random.randint(1000, 9999)))

                tournament = Tournament.objects.create(
                    name=tournament_name,
                    slug=slug,
                    type_tournament='DE',
                    department=zipcode[:2],
                    address=address,
                    is_indoor=random.choice([True, False]),
                    start_date=fake.date_this_year(),
                    end_date=fake.date_this_year(),
                    sport='volleyball',
                    max_teams=teams_per_tournament,
                    players_per_team=players_per_team,
                    number_of_pools=0,
                    nb_sets_to_win=3,
                    points_per_set=25
                )

                for _ in range(teams_per_tournament):
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
                    f"✅ {tournament.name} créé à {street_address} ({zipcode})"
                ))
