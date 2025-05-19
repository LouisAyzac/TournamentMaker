from django.shortcuts import render
from .models import Player, Team, Match, Ranking

def index(request):
    num_Player = Player.objects.count()
    context = {'num_Player': num_Player}
    return render(request, 'index.html', context=context)

def joueurs(request):
    joueurs = Player.objects.all()
    return render(request, 'TournamentMaker/joueurs.html', {'joueurs': joueurs})

def equipes(request):
    equipes = Team.objects.all()
    return render(request, 'TournamentMaker/equipes.html', {'equipes': equipes})

def matchs(request):
    matchs = Match.objects.order_by('date_played')
    return render(request, 'TournamentMaker/matchs.html', {'matchs': matchs})

def update_rankings():
    stats = {}
    for team in Team.objects.all():
        stats[team.id] = {'points': 0, 'played': 0, 'wins': 0, 'losses': 0}

    for match in Match.objects.all():
        stats[match.team_a.id]['played'] += 1
        stats[match.team_b.id]['played'] += 1
        if match.score_team_a > match.score_team_b:
            stats[match.team_a.id]['points'] += 3
            stats[match.team_a.id]['wins'] += 1
            stats[match.team_b.id]['losses'] += 1
        elif match.score_team_a < match.score_team_b:
            stats[match.team_b.id]['points'] += 3
            stats[match.team_b.id]['wins'] += 1
            stats[match.team_a.id]['losses'] += 1
        else:
            stats[match.team_a.id]['points'] += 1
            stats[match.team_b.id]['points'] += 1

    sorted_teams = sorted(stats.items(), key=lambda x: x[1]['points'], reverse=True)

    for rank, (team_id, data) in enumerate(sorted_teams, start=1):
        team = Team.objects.get(id=team_id)
        ranking, _ = Ranking.objects.get_or_create(team=team)
        ranking.rank = rank
        ranking.played = data['played']
        ranking.wins = data['wins']
        ranking.losses = data['losses']
        ranking.points = data['points']
        ranking.save()

def ranking(request):
    update_rankings()  # IMPORTANT : appelle la mise à jour avant de récupérer les données
    rankings = Ranking.objects.order_by('rank')
    return render(request, 'TournamentMaker/ranking.html', {'rankings': rankings})
