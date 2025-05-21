from django.shortcuts import render

# Create your views here.
from TournamentMaker.models import Player, Team

def home(request):
    request.session.flush()
    return render(request, 'home.html')





def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_Player = Player.objects.all().count()

    # Available books (status = 'a'

    context = {
        'num_Player': num_Player,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

from django.shortcuts import render

def players(request):
    all_players = Player.objects.all()  # récupère tous les joueurs
    return render(request, 'players.html', {'players': all_players})

def teams(request):
    all_teams = Team.objects.all()

    return render(request, 'teams.html', {'teams': all_teams})

def scores(request):
    
    return render(request, 'scores.html')


from django.shortcuts import render, get_object_or_404
from TournamentMaker.models import Player, Team

def player_detail(request, pk):
    player = get_object_or_404(Player, pk=pk)
    return render(request, 'players_detail.html', {'player': player})

from TournamentMaker.models import Team, Ranking

from TournamentMaker.models import Team, Ranking
from django.shortcuts import get_object_or_404, render

def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    ranking = Ranking.objects.filter(team=team).first()  # Pas .ranking, mais .filter()

    return render(request, 'teams_detail.html', {
        'team': team,
        'ranking': ranking  # clé correcte ici
    })



from django.shortcuts import render
from .models import Pool

from django.shortcuts import render, get_object_or_404
from .models import Pool

def pool_list(request):
    pools = Pool.objects.all()
    return render(request, 'pools.html', {'pools': pools})

def pool_detail(request, pk):
    pool = get_object_or_404(Pool, pk=pk)
    return render(request, 'pools_detail.html', {'pool': pool})

from django.shortcuts import render
from .models import Ranking
    
from django.shortcuts import render
from .models import Pool, Ranking

from django.shortcuts import render
from .models import Pool, Ranking

def rankings_list(request):
    pool_rankings = []

    for pool in Pool.objects.all():
        # Récupère les rankings des équipes de cette pool
        teams_in_pool = pool.teams.all()
        rankings = Ranking.objects.filter(team__in=teams_in_pool).select_related('team').order_by('rank')
        
        pool_rankings.append({
            'pool': pool,
            'rankings': rankings
        })

    return render(request, 'rankings.html', {'pool_rankings': pool_rankings})

from django.shortcuts import render, redirect
from .models import Match
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def scores(request):
    if request.method == "POST":
        # Pour chaque match, on met à jour les scores depuis le formulaire
        for key, value in request.POST.items():
            # Exemple de key: "match_5_set1_team_a"
            if key.startswith("match_"):
                parts = key.split("_")
                # parts = ['match', match_id, 'set1', 'team', 'a']
                match_id = parts[1]
                set_field = "_".join(parts[2:])  # ex: set1_team_a
                
                try:
                    match = Match.objects.get(pk=match_id)
                    setattr(match, set_field, int(value))
                    match.save()
                except Match.DoesNotExist:
                    pass

        return redirect('scores')  # Redirige pour éviter resoumission

    # GET : afficher les matchs
    matches = Match.objects.all()

    return render(request, "scores.html", {"matches": matches})





from .models import Tournament




from django.shortcuts import render, redirect, get_object_or_404

def select_tournament(request):
    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:

            tournoi = get_object_or_404(Tournament, id= selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            return redirect('dashboard')  # Redirige vers dashboard où le menu s’adapte

    tournois = Tournament.objects.all()
    return render(request, 'select_tournament.html', {'tournois': tournois})


def player_list(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    players = Player.objects.filter(team__tournament_id=tournament_id)
    return render(request, 'players.html', {'players': players})

def landing(request):
    request.session.pop("selected_tournament", None)
    return render(request, 'landing.html')

def dashboard(request):
    selected_id = request.session.get('selected_tournament_id')
    print("Selected tournament ID:", selected_id)  # juste pour debug dans la console
    tournoi_name = request.session.get('selected_tournament_name', 'Aucun tournoi sélectionné')
    return render(request, 'dashboard.html', {'tournoi_name': tournoi_name})
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Match, UserProfile

@login_required
def scores(request):
    try:
        team = request.user.userprofile.team
    except UserProfile.DoesNotExist:
        return render(request, 'no_team.html')

    if not team:
        return render(request, 'no_team.html')

    # Filtrer les matchs de l'équipe du user
    matches = Match.objects.filter(Q(team_a=team) | Q(team_b=team))

    if request.method == 'POST':
        for match in matches:
            for i in range(1, 4):  # gère sets 1 à 3 (tu peux ajouter 4 et 5 ensuite)
                setattr(match, f'set{i}_team_a', int(request.POST.get(f'match_{match.id}_set{i}_team_a', 0)))
                setattr(match, f'set{i}_team_b', int(request.POST.get(f'match_{match.id}_set{i}_team_b', 0)))
            match.save()
        return redirect('scores')  # évite les resoumissions de formulaire

    return render(request, 'scores.html', {'matches': matches})

from django.shortcuts import render
from .models import Team, UserProfile
from django.db import transaction

from django.shortcuts import render, redirect
from .models import Team, UserProfile
from .models import Tournament  # si nécessaire
from django.utils.dateparse import parse_date

LEVEL_MAP = {
    'debutant': 1,
    'intermediaire': 2,
    'avance': 3,
    'expert': 4,
}

def signup(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if not team_name:
            return render(request, 'signup.html', {'error': 'Le nom de l’équipe est requis.'})

        # (Facultatif) Associer à un tournoi si nécessaire
        tournament = Tournament.objects.first()  # à adapter selon ton projet
        team = Team.objects.create(name=team_name, tournament=tournament)

        # Créer les joueurs (au moins le premier)
        for i in range(1, 6):
            first_name = request.POST.get(f'first_name_{i}')
            last_name = request.POST.get(f'last_name_{i}')
            birthdate_str = request.POST.get(f'birthdate_{i}')
            email = request.POST.get(f'email_{i}')
            level_str = request.POST.get(f'level_{i}')

            # Ne créer un profil que si prénom et nom sont fournis
            if first_name and last_name:
                if not (birthdate_str and email and level_str):
                    continue  # skip si champs manquants

                birthdate = parse_date(birthdate_str)
                level = LEVEL_MAP.get(level_str.lower(), 1)

                UserProfile.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=birthdate,
                    level=level,
                    email=email,
                    team=team
                )

        return redirect('signup_success')  # Redirige vers la page de confirmation

    return render(request, 'signup.html')

def signup_success(request):
    return render(request, 'signup_success.html')

