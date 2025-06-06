from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Player, Team, Match, Pool, Ranking, Tournament, UserProfile
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date

LEVEL_MAP = {
    'débutant': 1,
    'intermédiaire': 2,
    'avancé': 3,
    'expert': 4,
    'maître': 5,
}

# === Page d'accueil et généralités ===
def home(request):
    request.session.flush()
    return render(request, 'home.html')

def index(request):
    num_Player = Player.objects.count()
    return render(request, 'index.html', {'num_Player': num_Player})

def landing(request):
    request.session.pop("selected_tournament", None)
    return render(request, 'landing.html')

def dashboard(request):
    tournoi_name = request.session.get('selected_tournament_name', 'Aucun tournoi sélectionné')
    return render(request, 'dashboard.html', {'tournoi_name': tournoi_name})


# === Joueurs, équipes, tournois ===
def players(request):
    return render(request, 'players.html', {'players': Player.objects.all()})

def teams(request):
    return render(request, 'teams.html', {'teams': Team.objects.all()})

def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    return render(request, 'players_detail.html', {'player': player})

def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    ranking = Ranking.objects.filter(team=team).first()
    return render(request, 'teams_detail.html', {'team': team, 'ranking': ranking})


# === Pools & Classements ===
def pool_list(request):
    return render(request, 'pools.html', {'pools': Pool.objects.all()})

def pool_detail(request, pk):
    pool = get_object_or_404(Pool, pk=pk)
    return render(request, 'pools_detail.html', {'pool': pool})

def rankings_list(request):
    pool_rankings = []
    for pool in Pool.objects.all():
        teams = pool.teams.all()
        rankings = Ranking.objects.filter(team__in=teams).select_related('team').order_by('rank')
        pool_rankings.append({'pool': pool, 'rankings': rankings})
    return render(request, 'rankings.html', {'pool_rankings': pool_rankings})


# === Scores (par joueur connecté) ===
@login_required 
def scores(request):
    try:
        team = request.user.userprofile.team
    except UserProfile.DoesNotExist:
        return render(request, 'no_team.html')

    if not team:
        return render(request, 'no_team.html')

    matches = Match.objects.filter(Q(team_a=team) | Q(team_b=team))

    if request.method == 'POST':
        for match in matches:
            for i in range(1, 6):
                setattr(match, f'set{i}_team_a', int(request.POST.get(f'match_{match.id}_set{i}_team_a', 0)))
                setattr(match, f'set{i}_team_b', int(request.POST.get(f'match_{match.id}_set{i}_team_b', 0)))
            match.save()
        return redirect('scores')

    return render(request, 'scores.html', {'matches': matches})


# === Sélection du tournoi ===
def select_tournament(request):
    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:
            tournoi = get_object_or_404(Tournament, id=selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            return redirect('dashboard')

    return render(request, 'select_tournament.html', {'tournois': Tournament.objects.all()})


# === Inscription ===
def signup(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if not team_name:
            return render(request, 'signup.html', {'error': 'Le nom de l’équipe est requis.'})

        tournament = Tournament.objects.first()
        team = Team.objects.create(name=team_name, tournament=tournament)

        for i in range(1, 6):
            first_name = request.POST.get(f'first_name_{i}')
            last_name = request.POST.get(f'last_name_{i}')
            birthdate_str = request.POST.get(f'birthdate_{i}')
            email = request.POST.get(f'email_{i}')
            level_str = request.POST.get(f'level_{i}')
            is_captain = request.POST.get('is_captain') == str(i)

            if first_name and last_name and birthdate_str and level_str:
                birthdate = parse_date(birthdate_str)
                level = LEVEL_MAP.get(level_str.lower(), 1)

                Player.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=birthdate,
                    level=level,
                    team=team
                )

                if is_captain and email:
                    username = request.POST.get('username')
                    password = request.POST.get('password')
                    if not username or not password:
                        return render(request, 'signup.html', {'error': 'Nom d’utilisateur et mot de passe requis pour le capitaine.'})
                    
                    user = User.objects.create_user(username=username, password=password)
                    UserProfile.objects.create(
                        user=user,
                        first_name=first_name,
                        last_name=last_name,
                        date_of_birth=birthdate,
                        level=level,
                        email=email,
                        team=team
                    )
        return redirect('signup_success')

    return render(request, 'signup.html')

def signup_success(request):
    return render(request, 'signup_success.html')


# === 🆕 Matchs ===

# Choix entre les phases
def match_choice(request):
    return render(request, 'matchs_choice.html')


# Matchs en cours
def matchs_en_cours(request):
    matchs = Match.objects.filter(statut='En cours')

    for match in matchs:
        match.scores_a = []
        match.scores_b = []
        for i in range(1, 6):
            sa = getattr(match, f'set{i}_team_a', None)
            sb = getattr(match, f'set{i}_team_b', None)
            if sa is not None and sb is not None:
                match.scores_a.append(sa)
                match.scores_b.append(sb)

    return render(request, 'matchs_en_cours.html', {'matchs': matchs})



def matchs_poules(request):
    pools_data = []

    for pool in Pool.objects.prefetch_related('teams'):
        stats = []

        for team in pool.teams.all():
            matchs_joues = Match.objects.filter(pool=pool, phase='pool')\
                .filter(Q(team_a=team) | Q(team_b=team))\
                .exclude(statut='ND')

            total_joues = matchs_joues.count()
            victoires = sum(1 for match in matchs_joues if match.winner_team == team)
            defaites = total_joues - victoires
            points = victoires * 3  # 3 points par victoire, 0 pour défaite

            stats.append({
                'team': team,
                'matchs_joues': total_joues,
                'victoires': victoires,
                'defaites': defaites,
                'points': points
            })

        # Classement selon les points
        stats.sort(key=lambda x: x['points'], reverse=True)
        for index, team_data in enumerate(stats, start=1):
            team_data['rank'] = index

        pools_data.append({'pool': pool, 'stats': stats})

    return render(request, 'matchs_poules.html', {'pools_data': pools_data})



# Détail d'une poule
def detail_poule(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    matchs = Match.objects.filter(pool=pool, phase='pool').select_related('team_a', 'team_b')

    for match in matchs:
        match.score_sets = []
        for i in range(1, 6):
            sa = getattr(match, f"set{i}_team_a", None)
            sb = getattr(match, f"set{i}_team_b", None)
            if sa is not None and sb is not None:
                match.score_sets.append({
                    'set_number': i,
                    'team_a_score': sa,
                    'team_b_score': sb
                })

    return render(request, 'detail_poule.html', {'pool': pool, 'matchs': matchs})


# Vue phase finale
def matchs_finale(request):
    phase_labels = {
        'quarter': 'Quarts de finale',
        'semi': 'Demi-finales',
        'final': 'Finale',
        'third_place': 'Petite finale'
    }

    phases = []
    quarter = Match.objects.filter(phase='quarter')
    semi = Match.objects.filter(phase='semi')
    final = Match.objects.filter(phase='final')
    third_place = Match.objects.filter(phase='third_place')

    for code, label in phase_labels.items():
        matchs = Match.objects.filter(phase=code)
        if matchs.exists():
            phases.append((code, label, matchs))

    return render(request, 'matchs_finale.html', {
        'phases': phases,
        'quarter': quarter,
        'semi': semi,
        'final': final,
        'third_place': third_place
    })


from django.contrib import messages
from .models import Match, Pool, Ranking


def generer_phase_finale(request):
    pool_names = ['A', 'B', 'C', 'D']
    pools = {p.name: p for p in Pool.objects.filter(name__in=pool_names)}
    
    # Vérification des données
    if len(pools) < 4 or not all(p.all_matches_played() for p in pools.values()):
        messages.error(request, "Les matchs de poules ne sont pas tous terminés ou des poules manquent.")
        return redirect('matchs')

    if Match.objects.filter(phase='quarter').exists():
        messages.warning(request, "Les matchs de phase finale ont déjà été générés.")
        return redirect('matchs')

    def top_two(pool): return Ranking.objects.filter(team__pools=pool).order_by('rank')[:2]
    r = {name: top_two(pools[name]) for name in pool_names}

    # Quarts de finale
    qf1 = Match.objects.create(team_a=r['A'][0].team, team_b=r['D'][1].team, phase='quarter')
    qf2 = Match.objects.create(team_a=r['B'][0].team, team_b=r['C'][1].team, phase='quarter')
    qf3 = Match.objects.create(team_a=r['C'][0].team, team_b=r['B'][1].team, phase='quarter')
    qf4 = Match.objects.create(team_a=r['D'][0].team, team_b=r['A'][1].team, phase='quarter')

    # Demi-finales (matchs vides)
    sf1 = Match.objects.create(phase='semi')  # Pour QF1 vs QF2
    sf2 = Match.objects.create(phase='semi')  # Pour QF3 vs QF4

    # Finale et petite finale
    Match.objects.create(phase='final')        # Pour SF1 vs SF2 (vainqueurs)
    Match.objects.create(phase='third_place')  # Pour SF1 vs SF2 (perdants)

    messages.success(request, "Les matchs de phase finale ont été générés avec succès.")
    return redirect('matchs')


from django.shortcuts import get_object_or_404, render

def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    return render(request, 'match_detail.html', {'match': match})
