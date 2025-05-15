from django.contrib import admin
from .models import Tournament, Team, Player, Match, Ranking  # importe tous les modèles

# Enregistre-les pour qu'ils apparaissent dans le panneau d'administration
admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Ranking)