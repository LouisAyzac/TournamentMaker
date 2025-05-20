from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
import random
from .models import Tournament, Team, Player, Match, Ranking, Pool


# Enregistre les modèles standards
admin.site.register(Tournament)

admin.site.register(Team)




@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_team_count', 'list_teams')
    filter_horizontal = ('teams',)
    readonly_fields = ('display_teams',)

    def get_form(self, request, obj=None, **kwargs):
        self.instance = obj
        return super().get_form(request, obj, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "teams":
            assigned_team_ids = Pool.objects.exclude(
                id=getattr(self, 'instance', None).id if self.instance else None
            ).values_list('teams__id', flat=True)
            kwargs["queryset"] = Team.objects.exclude(id__in=assigned_team_ids)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def current_team_count(self, obj):
        return obj.teams.count()
    current_team_count.short_description = "Nombre d'équipes"

    def list_teams(self, obj):
        return ", ".join([team.name for team in obj.teams.all()])
    list_teams.short_description = "Équipes"

    def display_teams(self, obj):
        return "\n".join(f"- {team.name}" for team in obj.teams.all())
    display_teams.short_description = "Équipes dans cette pool"

    actions = ['generate_matches']

    def generate_matches(self, request, queryset):
        for pool in queryset:
            teams = list(pool.teams.all())
            n = len(teams)
            if n < 2:
                self.message_user(request, f"La pool '{pool.name}' doit contenir au moins 2 équipes.")
                continue

            created_count = 0
            for i in range(n):
                for j in range(i + 1, n):
                    team_a = teams[i]
                    team_b = teams[j]
                    match_exists = Match.objects.filter(
                        pool=pool,
                        team_a=team_a,
                        team_b=team_b
                    ).exists() or Match.objects.filter(
                        pool=pool,
                        team_a=team_b,
                        team_b=team_a
                    ).exists()

                    if not match_exists:
                        Match.objects.create(pool=pool, team_a=team_a, team_b=team_b)
                        created_count += 1

            self.message_user(request, f"{created_count} matchs créés pour la pool '{pool.name}'.")
    generate_matches.short_description = "Générer tous les matchs round robin pour chaque pool"


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pool = None
        if self.instance and self.instance.pk:
            pool = self.instance.pool
        else:
            pool_id = self.data.get('pool') or (self.initial.get('pool') if self.initial else None)
            if pool_id:
                try:
                    pool = Pool.objects.get(pk=pool_id)
                except Pool.DoesNotExist:
                    pool = None

        if pool:
            teams_qs = pool.teams.all()
            self.fields['team_a'].queryset = teams_qs
            self.fields['team_b'].queryset = teams_qs

            if not self.instance.pk:
                teams_list = list(teams_qs)
                if len(teams_list) >= 2:
                    team_a, team_b = random.sample(teams_list, 2)
                    self.fields['team_a'].initial = team_a.pk
                    self.fields['team_b'].initial = team_b.pk

    def clean(self):
        cleaned_data = super().clean()
        pool = cleaned_data.get('pool')
        team_a = cleaned_data.get('team_a')
        team_b = cleaned_data.get('team_b')

        if pool and (team_a not in pool.teams.all() or team_b not in pool.teams.all()):
            raise ValidationError("Les équipes doivent appartenir à la pool sélectionnée.")
        if team_a == team_b:
            raise ValidationError("Les équipes doivent être différentes.")

        return cleaned_data


# Filtre personnalisé pour la Pool
from django.contrib.admin import SimpleListFilter

class PoolFilter(SimpleListFilter):
    title = 'Pool'
    parameter_name = 'pool'
    

    def lookups(self, request, model_admin):
        return [(pool.id, pool.name) for pool in Pool.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(pool__id=self.value())
        return queryset


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    form = MatchForm
    list_display = (
        'pool', 'team_a', 'team_b',
        'set1_team_a', 'set1_team_b',
        'set2_team_a', 'set2_team_b',
        'set3_team_a', 'set3_team_b',
        'set4_team_a', 'set4_team_b',
        'set5_team_a', 'set5_team_b',
    )
    list_editable = (
        'set1_team_a', 'set1_team_b',
        'set2_team_a', 'set2_team_b',
        'set3_team_a', 'set3_team_b',
        'set4_team_a', 'set4_team_b',
        'set5_team_a', 'set5_team_b',
    )
    list_filter = (PoolFilter,)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'team__name']

@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('team', 'rank', 'pools_names')
    list_filter = ['team__pools', 'team__tournament']  # filtre sur les pools des teams et tournoi

    def pools_names(self, obj):
        # Récupère toutes les pools de l’équipe et renvoie leurs noms séparés par une virgule
        return ", ".join(pool.name for pool in obj.team.pools.all())
    pools_names.short_description = "Pool(s)"


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'player_count')
    search_fields = ('name', 'tournament__name')