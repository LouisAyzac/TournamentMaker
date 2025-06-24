import requests
from TournamentMaker.models import City

def geocode_city(city):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': city.name,
        'format': 'json',
        'limit': 1,
        'countrycodes': 'fr',
    }
    response = requests.get(url, params=params, headers={'User-Agent': 'TournoiApp/1.0'})
    data = response.json()

    if data:
        city.latitude = data[0]['lat']
        city.longitude = data[0]['lon']
        city.save()
        print(f"[✔] {city.name} → {city.latitude}, {city.longitude}")
    else:
        print(f"[⚠] {city.name} non trouvée")

def run():
    cities = City.objects.filter(latitude__isnull=True)
    for city in cities:
        geocode_city(city)
