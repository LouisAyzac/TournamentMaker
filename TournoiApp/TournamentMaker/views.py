from django.shortcuts import render

# Create your views here.
from TournamentMaker.models import Player, Team

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

def team_detail(request, pk):
    team = get_object_or_404(Team, pk=pk)
    return render(request, 'teams_detail.html', {'team': team})
