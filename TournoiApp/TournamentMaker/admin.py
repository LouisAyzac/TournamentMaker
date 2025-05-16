from django.contrib import admin
from .models import Tournament, Team, Player, Match, Ranking, Pool # importe tous les modèles

# Enregistre-les pour qu'ils apparaissent dans le panneau d'administration
admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Match)
admin.site.register(Ranking)

@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ('name',)  # affiche le nom de la pool dans la liste admin
    filter_horizontal = ('teams',)  # permet de gérer les équipes dans la pool facilement
    def current_team_count(self, obj):
        return obj.teams.count()
    current_team_count.short_description = "Nombre d'équipes"