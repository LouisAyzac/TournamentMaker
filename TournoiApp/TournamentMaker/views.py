from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (Player, Team, Match, Pool, Ranking, Tournament, UserProfile)
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.contrib import messages

LEVEL_MAP = {
    'débutant': 1,
    'intermédiaire': 2,
    'avancé': 3,
    'expert': 4,
    'maître': 5,
}

def home(request):
    request.session.flush()
    return render(request, 'home.html')

def index(request):
    num_Player = Player.objects.all().count()
    return render(request, 'index.html', {'num_Player': num_Player})

def players(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    all_players = Player.objects.filter(team__tournament_id=tournament_id)
    return render(request, 'players.html', {'players': all_players})


def teams(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    all_teams = Team.objects.filter(tournament_id=tournament_id)
    return render(request, 'teams.html', {'teams': all_teams})





from django.shortcuts import render, get_object_or_404
from TournamentMaker.models import Player, Team


def player_detail(request, pk):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    player = get_object_or_404(Player, pk=pk, team__tournament_id=tournament_id)
    return render(request, 'players_detail.html', {'player': player})


from TournamentMaker.models import Team, Ranking    

from TournamentMaker.models import Team, Ranking
from django.shortcuts import get_object_or_404, render

from django.shortcuts import get_object_or_404, render
from TournamentMaker.models import Team, Ranking, Match

def team_detail(request, pk):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    team = get_object_or_404(Team, pk=pk, tournament_id=tournament_id)
    ranking = Ranking.objects.filter(team=team).first()

    teams = Team.objects.filter(tournament_id=tournament_id)
    matches = Match.objects.filter(team_a__tournament_id=tournament_id)

    points = {t.id: 0 for t in teams}
    pool_wins = {t.id: 0 for t in teams}


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

    for match in matches:
        winner = get_winner(match)
        if winner:
            if match.phase == 'final':
                points[winner.id] += 100
            elif match.phase == 'third_place':
                points[winner.id] += 80
            elif match.phase == 'semi':
                points[winner.id] += 60
            elif match.phase == 'quarter':
                points[winner.id] += 40
            elif match.phase == 'pool':
                points[winner.id] += 3
                pool_wins[winner.id] += 1

    sorted_teams = sorted(teams, key=lambda t: points[t.id], reverse=True)

    final_ranking = {}
    rank = 1
    for t in sorted_teams:
        final_ranking[t.id] = rank
        rank += 1

    final_rank = final_ranking.get(team.id)

    return render(request, 'teams_detail.html', {
        'team': team,
        'ranking': ranking,
        'final_rank': final_rank,
    })




from django.shortcuts import render
from .models import Pool

from django.shortcuts import render, get_object_or_404
from .models import Pool


def pool_list(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    pools = Pool.objects.filter(teams__tournament_id=tournament_id).distinct()
    return render(request, 'pools.html', {'pools': pools})


def pool_detail(request, pk):
    pool = get_object_or_404(Pool, pk=pk)
    return render(request, 'pools_detail.html', {'pool': pool})

def rankings_list(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    pool_rankings = []
    for pool in Pool.objects.filter(teams__tournament_id=tournament_id).distinct():
        teams_in_pool = pool.teams.filter(tournament_id=tournament_id)
        rankings = Ranking.objects.filter(team__in=teams_in_pool).select_related('team').order_by('rank')
        pool_rankings.append({'pool': pool, 'rankings': rankings})
    return render(request, 'rankings.html', {'pool_rankings': pool_rankings})


def matchs_en_cours(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    matchs = Match.objects.filter(statut='En cours', team_a__tournament_id=tournament_id)

    for match in matchs:
        match.scores_a = []
        match.scores_b = []
        for i in range(1, 6):
            score_a = getattr(match, f'set{i}_team_a', None)
            score_b = getattr(match, f'set{i}_team_b', None)
            if score_a is not None and score_b is not None:
                match.scores_a.append(score_a)
                match.scores_b.append(score_b)

    return render(request, 'matchs_en_cours.html', {'matchs': matchs})

def matchs(request):
    statut = request.GET.get('statut')
    phase = request.GET.get('phase')

def matchs(request):
    statut = request.GET.get('statut')
    phase = request.GET.get('phase')

    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    matchs = Match.objects.filter(team_a__tournament_id=tournament_id)

    if statut:
        matchs = matchs.filter(statut=statut)

    if phase:
        if phase == "pool":
            matchs = matchs.filter(phase="pool")
        elif phase == "final":
            matchs = matchs.filter(phase__in=["quarter", "semi", "third_place", "final"])

    # Préparer les scores pour tous les matchs (pas seulement "en cours")
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

    statuts = [
        ('ND', 'Non débuté', 'btn-outline-secondary'),
        ('EC', 'En cours', 'btn-outline-warning'),
        ('T', 'Terminé', 'btn-outline-success'),
    ]

    phases = [
        ('pool', 'Phase de poule'),
        ('final', 'Phase finale'),
    ]

    return render(request, 'matchs.html', {
        'matchs': matchs,
        'statuts': statuts,
        'phases': phases,
        'selected_statut': statut,
        'selected_phase': phase
    })


@login_required 

def scores(request):
    try:
        team = request.user.userprofile.team
    except UserProfile.DoesNotExist:
        return render(request, 'no_team.html')

    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id or not team or team.tournament_id != tournament_id:
        return render(request, 'no_team.html')

    matches = Match.objects.filter(
        Q(team_a=team) | Q(team_b=team),
        team_a__tournament_id=tournament_id
    )

    if request.method == 'POST':
        for match in matches:
            for i in range(1, 6):
                score_a = request.POST.get(f'match_{match.id}_set{i}_team_a')
                score_b = request.POST.get(f'match_{match.id}_set{i}_team_b')
                if score_a is not None and score_a.isdigit():
                    setattr(match, f'set{i}_team_a', int(score_a))
                if score_b is not None and score_b.isdigit():
                    setattr(match, f'set{i}_team_b', int(score_b))
            match.save()
        return redirect('scores')

    return render(request, 'scores.html', {'matches': matches})

def select_tournament(request):
    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:
            tournoi = get_object_or_404(Tournament, id=selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            return redirect('dashboard')

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
from .models import Team, UserProfile
from django.db import transaction

from django.shortcuts import render, redirect
from .models import Team, Tournament, Player, UserProfile
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from django.contrib import messages

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import IntegrityError
from django.utils.dateparse import parse_date
from .models import Team, Player, Tournament, UserProfile

# Utilise exactement ton dictionnaire
LEVEL_MAP = {
    'débutant': 1,
    'intermédiaire': 2,
    'avancé': 3,
    'expert': 4,
    'maître': 5,
}

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .models import Tournament, Team, Player, UserProfile
from django.utils.dateparse import parse_date

from django.utils.dateparse import parse_date
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def signup(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        # Rediriger vers la sélection du tournoi si non défini
        return redirect('select_tournament')

    try:
        tournament = Tournament.objects.get(pk=tournament_id)
    except Tournament.DoesNotExist:
        return redirect('select_tournament')

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if not team_name:
            return render(request, 'signup.html', {'error': 'Le nom de l’équipe est requis.'})

        team = Team.objects.create(name=team_name, tournament=tournament)

        # Flag pour vérifier que le capitaine est bien renseigné
        capitaine_valide = False

        for i in range(1, 6):
            first_name = request.POST.get(f'first_name_{i}')
            last_name = request.POST.get(f'last_name_{i}')
            birthdate_str = request.POST.get(f'birthdate_{i}')
            email = request.POST.get(f'email_{i}')
            level_str = request.POST.get(f'level_{i}')

            # Le capitaine doit avoir prénom, nom et email obligatoires, les autres joueurs sont optionnels
            if i == 1:
                if not (first_name and last_name and email):
                    team.delete()  # On supprime l'équipe si capitaine non complet
                    return render(request, 'signup.html', {'error': 'Le capitaine doit avoir un prénom, nom et email.'})
                capitaine_valide = True

            # On crée le joueur seulement si prénom et nom sont fournis (au moins)
            if first_name and last_name:
                birthdate = parse_date(birthdate_str) if birthdate_str else None
                level = LEVEL_MAP.get(level_str.lower(), 1) if level_str else 1

                player = Player.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=birthdate,
                    level=level,
                    email=email if email else '',
                    team=team,
                )

                if i == 1:
                    # Création du user Django pour le capitaine
                    username = email
                    user = User.objects.create_user(username=username, email=email)
                    user_profile = UserProfile.objects.create(user=user, level=level, team=team)

                    # Associer le capitaine à l'équipe
                    team.captain = user_profile
                    team.save()

                    # Envoyer email pour définir mot de passe
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    domain = '127.0.0.1:8000'  # adapter selon le déploiement
                    link = f"http://{domain}/accounts/reset/{uid}/{token}/"

                    subject = f"Bienvenue capitaine de l'équipe {team.name} !"
                    message = f"""
Bonjour {first_name},

Vous avez été inscrit comme capitaine de l'équipe {team.name}.
Veuillez cliquer sur le lien suivant pour définir ou modifier votre mot de passe :

{link}

Merci,
L'équipe du tournoi
"""
                    send_mail(subject, message, 'projetE3match@gmail.com', [email], fail_silently=False)

        if not capitaine_valide:
            team.delete()
            return render(request, 'signup.html', {'error': 'Le capitaine est obligatoire.'})

        return redirect('signup_success')

    return render(request, 'signup.html')

def signup_success(request):
    print("Page de succès atteinte.")
    return render(request, 'signup_success.html')


from django.shortcuts import render
from .admin import FinalRankingAdmin
from .models import Ranking, Team
# views.py

from django.shortcuts import render
from .models import Pool, Ranking

from django.shortcuts import render
from .models import Team, Match

def classement_final_view(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    teams = Team.objects.filter(tournament_id=tournament_id)
    matches = Match.objects.filter(team_a__tournament_id=tournament_id)

    points = {team.id: 0 for team in teams}
    pool_wins = {team.id: 0 for team in teams}
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

    for match in matches:
        winner = get_winner(match)
        if winner:
            if match.phase == 'final':
                points[winner.id] += 100
            elif match.phase == 'third_place':
                points[winner.id] += 80
            elif match.phase == 'semi':
                points[winner.id] += 60
            elif match.phase == 'quarter':
                points[winner.id] += 40
            elif match.phase == 'pool':
                points[winner.id] += 3
                pool_wins[winner.id] += 1

    # Trier les équipes par points
    sorted_teams = sorted(teams, key=lambda t: points[t.id], reverse=True)

    final_ranking = []
    rank = 1
    for team in sorted_teams:
        final_ranking.append((team, {
            'rank': rank,
            'wins': points[team.id],
            'pool_wins': pool_wins[team.id],
        }))
        rank += 1

    context = {
        'final_ranking': final_ranking
    }

    return render(request, 'classement_final.html', context)

