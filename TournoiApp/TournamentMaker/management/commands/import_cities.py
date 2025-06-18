import requests
from django.core.management.base import BaseCommand
from TournamentMaker.models import City

class Command(BaseCommand):
    help = 'Importe toutes les villes françaises depuis Geo API Gouv'

    def handle(self, *args, **options):
        url = 'https://geo.api.gouv.fr/communes?fields=nom,centre&format=json&limit=10000'

        try:
            response = requests.get(url)
            response.raise_for_status()  # Lève une exception pour les erreurs HTTP
            cities = response.json()

            city_objects = []
            for city in cities:
                name = city['nom']
                latitude = city['centre']['coordinates'][1] if city['centre'] else None
                longitude = city['centre']['coordinates'][0] if city['centre'] else None

                city_objects.append(
                    City(name=name, latitude=latitude, longitude=longitude)
                )

            # Utilisation de bulk_create pour optimiser les insertions
            created_cities = City.objects.bulk_create(city_objects)
            count = len(created_cities)

            self.stdout.write(self.style.SUCCESS(f"{count} villes importées."))

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la récupération des données: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Une erreur inattendue est survenue: {e}"))
