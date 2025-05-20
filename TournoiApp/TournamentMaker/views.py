from django.shortcuts import render

# Create your views here.
from TournamentMaker.models import Player, Team

def index(request):
    num_Player = Player.objects.count()
    context = {'num_Player': num_Player}
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

