from django.core.management.base import BaseCommand
from TournamentMaker.models import Tournament, Team, Player, City, Address, Pool
from django.utils.text import slugify
from faker import Faker
import random

CITY_ZONES = {
    "Paris": [
        {"zipcode": "75011", "lat": 48.8566, "lon": 2.3789, "area": "Bastille"},
        {"zipcode": "75018", "lat": 48.8924, "lon": 2.3449, "area": "Montmartre"},
    ],
    "Lyon": [
        {"zipcode": "69003", "lat": 45.7574, "lon": 4.8595, "area": "Part-Dieu"},
        {"zipcode": "69007", "lat": 45.7427, "lon": 4.8445, "area": "Jean Macé"},
    ],
}

class Command(BaseCommand):
    help = "Crée 2 tournois RR avec 4 poules et 4 équipes par poule (avec affectation explicite des équipes aux pools)."

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')
        players_per_team = 6
        teams_per_tournament = 16  # 4 poules × 4 équipes

        # Sélectionner aléatoirement 2 quartiers
        all_zones = [(city, zone) for city, zones in CITY_ZONES.items() for zone in zones]
        selected = random.sample(all_zones, 2)

        for city_name, zone in selected:
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

            tournament_name = f"Volley RR - {city_name} ({area})"
            slug = slugify(f"{tournament_name}-{random.randint(1000, 9999)}")

            tournament = Tournament.objects.create(
                name=tournament_name,
                slug=slug,
                type_tournament='RR',
                department=zipcode[:2],
                address=address,
                is_indoor=random.choice([True, False]),
                start_date=fake.date_this_year(),
                end_date=fake.date_this_year(),
                sport='volleyball',
                max_teams=teams_per_tournament,
                players_per_team=players_per_team,
                number_of_pools=4,
                nb_sets_to_win=3,
                points_per_set=25
            )

            # Récupérer les poules générées automatiquement
            pools = list(Pool.objects.filter(tournament=tournament).order_by("id"))
            if len(pools) != 4:
                self.stdout.write(self.style.WARNING(
                    f"⚠️ Tournoi {tournament.name} : {len(pools)} poules détectées (attendu 4)"
                ))

            # Répartir les 16 équipes dans les 4 poules (4 équipes/poule)
            team_index = 0
            for pool in pools:
                for _ in range(4):  # 4 équipes par poule
                    team = Team.objects.create(
                        name=fake.unique.company(),
                        tournament=tournament,
                        pool=pool
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
                    team_index += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ {tournament.name} créé à {street_address} ({zipcode}) avec 4 poules et 16 équipes."
            ))
