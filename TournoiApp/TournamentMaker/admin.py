from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Tournament, Team, Player, Match, Ranking, Pool, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import SimpleListFilter

admin.site.register(Team)

@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_team_count', 'list_teams')
    filter_horizontal = ('teams',)
    readonly_fields = ('display_teams',)
    actions = ['generate_matches']

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

    def generate_matches(self, request, queryset):
        for pool in queryset:
            teams = list(pool.teams.all())
            n = len(teams)
            if n < 2:
                self.message_user(request, f"La pool '{pool.name}' doit contenir au moins 2 équipes.")
                continue

            Match.objects.filter(pool=pool, phase='pool').delete()

            created_count = 0
            for i in range(n):
                for j in range(i + 1, n):
                    team_a = teams[i]
                    team_b = teams[j]
                    Match.objects.create(pool=pool, team_a=team_a, team_b=team_b, phase='pool')
                    created_count += 1

            self.message_user(request, f"{created_count} matchs créés pour la pool '{pool.name}'.")
    generate_matches.short_description = "Générer tous les matchs round robin pour chaque pool"


class MatchForm(forms.ModelForm):
    WINNER_CHOICES = [
        ('', '---------'),
        ('A', 'Team A'),
        ('B', 'Team B'),
    ]

    winner_choice = forms.ChoiceField(
        choices=WINNER_CHOICES,
        required=False,
        label="Vainqueur",
        help_text="Choisir Team A ou Team B"
    )

    class Meta:
        model = Match
        exclude = ['winner_side']  # Masque le champ technique dans le formulaire admin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')

        # Initialise le choix vainqueur selon la valeur en base
        if instance and instance.team_a and instance.team_b:
            if instance.winner_side == 'A':
                self.fields['winner_choice'].initial = 'A'
            elif instance.winner_side == 'B':
                self.fields['winner_choice'].initial = 'B'

        # Restreint les équipes aux équipes de la pool
        pool = instance.pool if instance and instance.pk else None
        if not pool:
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

            if not instance.pk and len(teams_qs) >= 2:
                team_a, team_b = random.sample(list(teams_qs), 2)
                self.fields['team_a'].initial = team_a.pk
                self.fields['team_b'].initial = team_b.pk

    def clean(self):
        cleaned_data = super().clean()
        team_a = cleaned_data.get('team_a')
        team_b = cleaned_data.get('team_b')
        choice = cleaned_data.get('winner_choice')

        # Équipes différentes
        if team_a and team_b and team_a == team_b:
            raise ValidationError("Les équipes doivent être différentes.")

        # Stocke le vainqueur dans winner_side
        if choice == 'A':
            self.instance.winner_side = 'A'
        elif choice == 'B':
            self.instance.winner_side = 'B'
        else:
            self.instance.winner_side = None

        return cleaned_data




class PoolFilter(SimpleListFilter):
    title = 'Pool'
    parameter_name = 'pool'

    def lookups(self, request, model_admin):
        return [(pool.id, pool.name) for pool in Pool.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(pool__id=self.value())
        return queryset


class PhaseFilter(SimpleListFilter):
    title = 'Phase'
    parameter_name = 'phase'

    def lookups(self, request, model_admin):
        return (
            ('pool', 'Phase de poules'),
            ('quarter', 'Quarts de finale'),
            ('semi', 'Demi-finales'),
            ('final', 'Finale'),
            ('third_place', 'Petite finale'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(phase=self.value())
        return queryset


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    form = MatchForm
    list_display = (
        'phase', 'pool', 'team_a', 'team_b', 'statut',
        'start_time', 'end_time', 'terrain_number','winner_team',
        'set1_team_a', 'set1_team_b',
        'set2_team_a', 'set2_team_b',
        'set3_team_a', 'set3_team_b',
        'set4_team_a', 'set4_team_b',
        'set5_team_a', 'set5_team_b',
    )
    list_editable = (
        'statut', 'start_time', 'end_time', 'terrain_number',
        'set1_team_a', 'set1_team_b',
        'set2_team_a', 'set2_team_b',
        'set3_team_a', 'set3_team_b',
        'set4_team_a', 'set4_team_b',
        'set5_team_a', 'set5_team_b',
    )
    list_filter = (PoolFilter, PhaseFilter)




@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    search_fields = ['first_name', 'last_name', 'team__name']


@admin.register(Ranking)
class RankingAdmin(admin.ModelAdmin):
    list_display = ('team', 'rank', 'pools_names')
    list_filter = ['team__pools', 'team__tournament']

    def pools_names(self, obj):
        return ", ".join(pool.name for pool in obj.team.pools.all())
    pools_names.short_description = "Pool(s)"


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'player_count')
    search_fields = ('name', 'tournament__name')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


def is_match_finished(match):
    score_a = 0
    score_b = 0
    for i in range(1, 6):
        sa = getattr(match, f'set{i}_team_a')
        sb = getattr(match, f'set{i}_team_b')
        if sa is None or sb is None:
            continue
        if sa > sb:
            score_a += 1
        elif sb > sa:
            score_b += 1
    return score_a >= 3 or score_b >= 3


def get_winner(match):
    score_a = 0
    score_b = 0
    for i in range(1, 6):
        sa = getattr(match, f'set{i}_team_a')
        sb = getattr(match, f'set{i}_team_b')
        if sa is not None and sb is not None:
            if sa > sb:
                score_a += 1
            elif sb > sa:
                score_b += 1
    if score_a > score_b:
        return match.team_a
    elif score_b > score_a:
        return match.team_b
    else:
        return None


@receiver(post_save, sender=Match)
def auto_generate_quarters(sender, instance, **kwargs):
    if instance.phase != 'pool':
        return

    pool = instance.pool
    if not pool:
        return

    unfinished = Match.objects.filter(pool=pool, phase='pool', en_cours=True).exists()
    if unfinished:
        return

    required_pool_names = ['A', 'B', 'C', 'D']
    pools = Pool.objects.filter(name__in=required_pool_names).order_by('name')
    if pools.count() != 4:
        return

    pool_teams = {}
    for p in pools:
        rankings = Ranking.objects.filter(team__pools=p).order_by('rank')[:2]
        if rankings.count() < 2:
            return
        pool_teams[p.name] = [rankings[0].team, rankings[1].team]

    Match.objects.filter(phase='quarter').delete()

    matchups = [
        (pool_teams['A'][0], pool_teams['B'][1]),
        (pool_teams['A'][1], pool_teams['B'][0]),
        (pool_teams['C'][0], pool_teams['D'][1]),
        (pool_teams['C'][1], pool_teams['D'][0]),
    ]

    for team_a, team_b in matchups:
        Match.objects.create(pool=None, team_a=team_a, team_b=team_b, phase='quarter')


@receiver(post_save, sender=Match)
def auto_generate_semi_finals(sender, instance, **kwargs):
    if instance.phase != 'quarter':
        return

    quarter_finals = Match.objects.filter(phase='quarter').order_by('id')
    if quarter_finals.count() != 4:
        return

    for match in quarter_finals:
        if not is_match_finished(match):
            return

    winners = []
    for match in quarter_finals:
        winner = get_winner(match)
        if not winner:
            return
        winners.append(winner)

    Match.objects.filter(phase='semi').delete()

    Match.objects.create(pool=None, team_a=winners[0], team_b=winners[1], phase='semi')
    Match.objects.create(pool=None, team_a=winners[2], team_b=winners[3], phase='semi')


@receiver(post_save, sender=Match)
def auto_generate_final(sender, instance, **kwargs):
    if instance.phase != 'semi':
        return

    semi_finals = Match.objects.filter(phase='semi').order_by('id')
    if semi_finals.count() != 2:
        return

    for match in semi_finals:
        if not is_match_finished(match):
            return

    winners = []
    losers = []
    for match in semi_finals:
        winner = get_winner(match)
        if not winner:
            return
        winners.append(winner)
        loser = match.team_a if match.team_b == winner else match.team_b
        losers.append(loser)

    Match.objects.filter(phase='final').delete()
    Match.objects.filter(phase='third_place').delete()

    Match.objects.create(pool=None, team_a=winners[0], team_b=winners[1], phase='final')
    Match.objects.create(pool=None, team_a=losers[0], team_b=losers[1], phase='third_place')

from django.db import models
from django.contrib import admin
from .models import Ranking, Team, Match  # à adapter selon ton projet

class FinalRankingProxy(Ranking):
    class Meta:
        proxy = True
        verbose_name = "Ranking Final"
        verbose_name_plural = "Ranking Final"

@admin.register(FinalRankingProxy)
class FinalRankingAdmin(admin.ModelAdmin):
    list_display = ('team', 'final_rank_display', 'wins_display', 'pool_wins_display')

    def get_queryset(self, request):
        return super().get_queryset(request)

    def final_rank_display(self, obj):
        final_ranking = self.get_final_ranking()
        return final_ranking.get(obj.team.id, {}).get('rank', obj.rank)
    final_rank_display.short_description = "Rang final"
    

    def wins_display(self, obj):
        final_ranking = self.get_final_ranking()
        return final_ranking.get(obj.team.id, {}).get('wins', 0)
    wins_display.short_description = "Points totaux"

    def pool_wins_display(self, obj):
        final_ranking = self.get_final_ranking()
        return final_ranking.get(obj.team.id, {}).get('pool_wins', 0)
    pool_wins_display.short_description = "Victoires en poule"

    def get_final_ranking(self):
        teams = Team.objects.all()
        points = {team.id: 0 for team in teams}
        pool_wins = {team.id: 0 for team in teams}

        matches = Match.objects.all()
        for match in matches:
            winner = self.get_winner(match)
            loser = None
            if winner:
                loser = match.team_a if winner == match.team_b else match.team_b

            phase = match.phase
            if phase == 'final':
                if winner:
                    points[winner.id] += 100
                if loser:
                    points[loser.id] += 90
            elif phase == 'third_place':
                if winner:
                    points[winner.id] += 80
                if loser:
                    points[loser.id] += 70
            elif phase == 'semi':
                if winner:
                    points[winner.id] += 60
                if loser:
                    points[loser.id] += 50
            elif phase == 'quarter':
                if winner:
                    points[winner.id] += 40
                if loser:
                    points[loser.id] += 30
            elif phase == 'pool':
                if winner:
                    points[winner.id] += 3
                    pool_wins[winner.id] += 1

        sorted_teams = sorted(teams, key=lambda t: points[t.id], reverse=True)

        final_ranking = {}
        rank = 1
        for team in sorted_teams:
            final_ranking[team.id] = {
                'rank': rank,
                'wins': points[team.id],
                'pool_wins': pool_wins[team.id],
            }
            rank += 1

        return final_ranking

    def get_winner(self, match):
        score_a = 0
        score_b = 0
        for i in range(1, 6):
            sa = getattr(match, f'set{i}_team_a')
            sb = getattr(match, f'set{i}_team_b')
            if sa is not None and sb is not None:
                if sa > sb:
                    score_a += 1
                elif sb > sa:
                    score_b += 1
        if score_a > score_b:
            return match.team_a
        elif score_b > score_a:
            return match.team_b
        else:
            return None
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'team')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'address', 'is_indoor', 'start_date', 'end_date', 'sport')
    list_filter = ('sport', 'is_indoor', 'start_date', 'end_date')
    search_fields = ('name', 'department', 'address')