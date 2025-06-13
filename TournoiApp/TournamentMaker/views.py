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
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.core.paginator import Paginator
from .models import Tournament

from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator
from django.utils.timezone import now
from .models import Tournament

def home(request):
    # Gestion sélection tournoi → stocker en session
    if 'tournament_id' in request.GET:
        selected_id = request.GET.get('tournament_id')
        tournoi = get_object_or_404(Tournament, id=selected_id)
        request.session['selected_tournament_id'] = tournoi.id
        request.session['selected_tournament_name'] = tournoi.name
        request.session['type_tournament'] = tournoi.type_tournament
        request.session['selected_tournament_end'] = str(tournoi.end_date)  # 👈 ajoute ceci
        return redirect('dashboard', tournament_id=selected_id)  # ✅ redirection avec ID

    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:
            tournoi = get_object_or_404(Tournament, id=selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            request.session['type_tournament'] = tournoi.type_tournament
            return redirect('dashboard', tournament_id=selected_id)  # ✅ redirection avec ID

    # Gestion affichage
    today = now().date()
    category = request.GET.get('category', 'all')

    if category == 'ongoing':
        tournois = Tournament.objects.filter(start_date__lte=today, end_date__gte=today)
    elif category == 'upcoming':
        tournois = Tournament.objects.filter(start_date__gt=today)
    elif category == 'past':
        tournois = Tournament.objects.filter(end_date__lt=today)
    elif category == 'all':
        tournois = Tournament.objects.all()
    else:
        tournois = Tournament.objects.all()

    # Filtres sport + département
    sports = Tournament.SPORT_CHOICES
    selected_sport = request.GET.get('sport')
    selected_department = request.GET.get('department')

    if selected_sport:
        tournois = tournois.filter(sport=selected_sport)
    if selected_department:
        tournois = tournois.filter(department__icontains=selected_department)

    # Pagination
    paginator = Paginator(tournois, 6)  # 6 tournois par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context
    context = {
        'tournois': page_obj,  # paginé
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'category': category,
        'sports': sports,
        'selected_sport': selected_sport,
        'selected_department': selected_department,
    }

    return render(request, 'home.html', context)



def index(request):
    num_Player = Player.objects.count()
    return render(request, 'index.html', {'num_Player': num_Player})

def landing(request):
    request.session.pop("selected_tournament", None)
    return render(request, 'landing.html')

from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect
from .models import Tournament

def dashboard(request, tournament_id):
    tournoi = get_object_or_404(Tournament, id=tournament_id)
    today = now().date()

    if tournoi.start_date > today:
        statut = "À venir"
    elif tournoi.end_date < today:
        statut = "Terminé"
    else:
        statut = "En cours"

    # 🔁 Stocker les infos nécessaires en session pour la barre de navigation
    request.session['selected_tournament_id'] = tournoi.id
    request.session['selected_tournament_name'] = tournoi.name
    request.session['type_tournament'] = tournoi.type_tournament
    request.session['teams_count'] = tournoi.teams.count()
    request.session['max_teams'] = tournoi.max_teams
    request.session['tournament_statut'] = statut

    return render(request, 'dashboard.html', {
        'tournoi': tournoi,
        'statut': statut
    })



# === Joueurs, équipes, tournois ===
def players(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('home')

    all_players = Player.objects.filter(team__tournament_id=tournament_id)
    return render(request, 'players.html', {'players': all_players})

def teams(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('home')

    all_teams = Team.objects.filter(tournament_id=tournament_id)

    # 🔥 On enrichit chaque team avec ses wins / losses
    for team in all_teams:
        team.wins = Match.objects.filter(
            Q(team_a=team, winner_side='A') | Q(team_b=team, winner_side='B')
        ).count()

        team.losses = Match.objects.filter(
            Q(team_a=team, winner_side='B') | Q(team_b=team, winner_side='A')
        ).count()

        # 🔥 On peut aussi passer le player_count facilement
        team.player_count = team.players.count()

         # 🔥 On va chercher le Ranking si dispo
        ranking = Ranking.objects.filter(team=team).first()
        team.rank = ranking.rank if ranking else None  # None si pas de classement

    return render(request, 'teams.html', {'teams': all_teams})

from django.shortcuts import render, get_object_or_404
from TournamentMaker.models import Player, Team


def player_detail(request, pk):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('home')

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
        return redirect('home')

    # Récupérer l'équipe et son tournoi
    team = get_object_or_404(Team, pk=pk, tournament_id=tournament_id)
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Récupérer le classement de cette équipe (Ranking)
    ranking = Ranking.objects.filter(team=team).first()

    # Calcul des victoires
    team.wins = Match.objects.filter(
        Q(team_a=team, winner_side='A') | Q(team_b=team, winner_side='B')
    ).count()

    # Calcul des défaites
    team.losses = Match.objects.filter(
        Q(team_a=team, winner_side='B') | Q(team_b=team, winner_side='A')
    ).count()

    # On passe tout au template
    return render(request, 'teams_detail.html', {
        'team': team,
        'ranking': ranking,
    })




from django.shortcuts import render
from .models import Pool

from django.shortcuts import render, get_object_or_404
from .models import Pool



# === Pools & Classements ===
def pool_list(request):
    return render(request, 'pools.html', {'pools': Pool.objects.all()})


def pool_detail(request, pk):
    pool = get_object_or_404(Pool, pk=pk)
    return render(request, 'pools_detail.html', {'pool': pool})

def rankings_list(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('home')

    pool_rankings = []
    for pool in Pool.objects.all():
        teams = pool.teams.all()
        rankings = Ranking.objects.filter(team__in=teams).select_related('team').order_by('rank')
        pool_rankings.append({'pool': pool, 'rankings': rankings})

    # === Ajout pour récupérer vainqueur et finaliste ===
    winner = None
    finalist = None
    try:
        final_match = Match.objects.filter(
            tournament_id=tournament_id,
            phase='final',
            team_a__isnull=False,
            team_b__isnull=False
        ).first()

        if final_match and final_match.winner_side:
            winner = final_match.team_a if final_match.winner_side == 'A' else final_match.team_b
            finalist = final_match.team_b if final_match.winner_side == 'A' else final_match.team_a

    except Exception as e:
        print(f"[ERROR] rankings_list winner/finalist: {str(e)}")

    return render(request, 'rankings.html', {
        'pool_rankings': pool_rankings,
        'winner': winner,
        'finalist': finalist,
    })



# === Scores (par joueur connecté) ===
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


# === Sélection du tournoi ===
from django.shortcuts import render, redirect, get_object_or_404

'''def select_tournament(request):
    # Si on a cliqué sur un lien avec ?tournament_id=XX
    if 'tournament_id' in request.GET:
        selected_id = request.GET.get('tournament_id')
        tournoi = get_object_or_404(Tournament, id=selected_id)
        request.session['selected_tournament_id'] = tournoi.id
        request.session['selected_tournament_name'] = tournoi.name
        return redirect('dashboard')

    # Si c'est un POST normal (formulaire)
    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:
            tournoi = get_object_or_404(Tournament, id=selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            return redirect('dashboard')

    # Sinon afficher le formulaire
    tournois = Tournament.objects.all()
    return render(request, 'select_tournament.html', {'tournois': tournois})
'''
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

from django.db import transaction
from django.shortcuts import render, redirect
from .models import Team, Tournament, Player, UserProfile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import IntegrityError
from django.utils.dateparse import parse_date

LEVEL_MAP = {
    'debutant': 1,
    'intermediaire': 2,
    'avance': 3,
    'expert': 4,
}

from django.shortcuts import render

def tournament_full(request):
    return render(request, 'tournament_full.html')


def signup(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('home')

    try:
        tournament = Tournament.objects.get(pk=tournament_id)
    except Tournament.DoesNotExist:
        return redirect('home')

    max_teams = tournament.max_teams
    current_teams_count = Team.objects.filter(tournament=tournament).count()

    if current_teams_count >= max_teams:
        return redirect('tournament_full')

    players_per_team = tournament.players_per_team
    total_players = range(players_per_team + 2)

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if not team_name:
            return render(request, 'signup.html', {
                'error': 'Le nom de l’équipe est requis.',
                'players_per_team': players_per_team,
                'total_players': total_players
            })

        team_score = 0
        players_data = []

        for i in total_players:
            index = i + 1
            first_name = request.POST.get(f'first_name_{index}')
            last_name = request.POST.get(f'last_name_{index}')
            birthdate_str = request.POST.get(f'birthdate_{index}')
            email = request.POST.get(f'email_{index}')
            level_str = request.POST.get(f'level_{index}')

            if first_name and last_name:
                birthdate = parse_date(birthdate_str) if birthdate_str else None
                level = int(LEVEL_MAP.get(level_str.lower(), 1)) if level_str else 1

                players_data.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'birth_date': birthdate,
                    'email': email,
                    'level': level
                })

                team_score += level

        # Création de l’équipe
        team = Team.objects.create(name=team_name, tournament=tournament)

        # Si le tournoi est en round robin (RR), on attribue une pool
        if tournament.type_tournament == 'RR':
            pools = Pool.objects.filter(tournament=tournament)
            if not pools.exists():
                team.delete()
                return render(request, 'signup.html', {
                    'error': 'Aucune poule disponible pour ce tournoi.',
                    'players_per_team': players_per_team,
                    'total_players': total_players
                })

            pool_strength = []
            for pool in pools:
                teams_in_pool = pool.teams.all()
                total_score = sum(
                    sum(int(player.level) for player in team.players.all() if player.level)
                    for team in teams_in_pool
                )
                team_count = teams_in_pool.count()
                avg_score = total_score / team_count if team_count > 0 else 0
                pool_strength.append((pool, avg_score, team_count))

            pool_strength.sort(key=lambda x: (x[2], abs(x[1] - team_score)))
            pool_to_assign = pool_strength[0][0]
            team.pool = pool_to_assign
            team.save()

        capitaine_valide = False
        for i, player_data in enumerate(players_data):
            player = Player.objects.create(
                first_name=player_data['first_name'],
                last_name=player_data['last_name'],
                birth_date=player_data['birth_date'],
                level=player_data['level'],
                email=player_data['email'] or '',
                team=team
            )

            if i == 0 and player_data['email']:
                email = player_data['email']
                username = f"{email}_{team.id}"
                user = User.objects.create_user(username=username, email=email)
                user_profile = UserProfile.objects.create(
                    user=user,
                    level=player_data['level'],
                    team=team
                )
                team.captain = user_profile
                team.save()

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                domain = '127.0.0.1:8000'
                link = f"http://{domain}/accounts/reset/{uid}/{token}/"

                subject = f"Bienvenue capitaine de l'équipe {team.name} !"
                message = f"""
Bonjour {player_data['first_name']},

Vous avez été inscrit comme capitaine de l'équipe {team.name}.
Veuillez cliquer sur le lien suivant pour définir ou modifier votre mot de passe :

{link}

Merci,
L'équipe du tournoi
"""
                send_mail(subject, message, 'projetE3match@gmail.com', [email], fail_silently=False)
                capitaine_valide = True

        if not capitaine_valide:
            team.delete()
            return render(request, 'signup.html', {
                'error': 'Le capitaine est obligatoire (joueur 1 avec une adresse email).',
                'players_per_team': players_per_team,
                'total_players': total_players
            })

        return redirect('signup_success')

    return render(request, 'signup.html', {
        'players_per_team': players_per_team,
        'total_players': total_players
    })

 
def signup_success(request):
    print("Page de succès atteinte.")
    return render(request, 'signup_success.html')


# === 🆕 Matchs ===

# Choix entre les phases
from django.shortcuts import render
from .models import Tournament

from django.shortcuts import render, get_object_or_404
from .models import Tournament

def match_choice(request):
    # Récupérer l'ID du tournoi de l'URL ou de la session
    tournament_id = request.GET.get('tournament_id') or request.session.get('selected_tournament_id')

    if not tournament_id:
        # Si aucun ID de tournoi n'est trouvé, afficher une erreur
        return render(request, 'matchs_choice.html', {'error': 'Aucun tournoi sélectionné'})

    try:
        # Récupérer le tournoi de la base de données
        tournament = get_object_or_404(Tournament, id=tournament_id)

        # Rendre le template avec le tournoi
        return render(request, 'matchs_choice.html', {'tournament': tournament})

    except Exception as e:
        # En cas d'erreur, afficher un message d'erreur
        return render(request, 'matchs_choice.html', {'error': f'Erreur: {str(e)}'})



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



from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Pool, Match, Tournament

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Pool, Match, Tournament

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Tournament, Pool, Match

def matchs_poules(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    pools_data = []

    # On récupère les pools du tournoi
    pools = Pool.objects.filter(tournament=tournament)

    for pool in pools.prefetch_related('teams'):
        stats = []

        for team in pool.teams.all():
            # On récupère les matchs joués de cette équipe dans cette pool
            matchs_joues = Match.objects.filter(pool=pool, phase='pool')\
                .filter(Q(team_a=team) | Q(team_b=team))\
                .exclude(statut='ND')  # On ne prend pas les matchs "non débuté"

            total_joues = matchs_joues.count()

            victoires = 0
            defaites = 0
            diff_sets = 0
            diff_points = 0

            for match in matchs_joues:
                # Victoire/défaite
                if match.winner_side == 'A' and match.team_a == team:
                    victoires += 1
                elif match.winner_side == 'B' and match.team_b == team:
                    victoires += 1
                elif match.winner_side is not None:
                    defaites += 1

                # Calculs goal average
                for i in range(1, 6):  # max 5 sets
                    score_a = getattr(match, f'set{i}_team_a', None)
                    score_b = getattr(match, f'set{i}_team_b', None)

                    if score_a is None or score_b is None:
                        break

                    if match.team_a == team:
                        diff_sets += score_a - score_b
                        diff_points += score_a - score_b
                    elif match.team_b == team:
                        diff_sets += score_b - score_a
                        diff_points += score_b - score_a

            # Calcul des points (3 points par victoire en volley)
            points = victoires * 3

            stats.append({
                'team': team,
                'matchs_joues': total_joues,
                'victoires': victoires,
                'defaites': defaites,
                'diff_sets': diff_sets,
                'diff_points': diff_points,
            })

        # Tri : victoires -> diff sets -> diff points
        stats.sort(
            key=lambda x: (
                x['victoires'],
                x['diff_sets'],
                x['diff_points']
            ),
            reverse=True
        )

        # Attribution du rang
        for index, team_data in enumerate(stats, start=1):
            team_data['rank'] = index

        # On ajoute cette pool au résultat
        pools_data.append({'pool': pool, 'stats': stats})

    # On passe les données au template
    return render(request, 'matchs_poules.html', {
        'pools_data': pools_data,
        'tournament': tournament
    })

 
# Détail d'une poule
from django.shortcuts import render, get_object_or_404
from .models import Pool, Match

def detail_poule(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    tournament = pool.tournament

    # Matchs joués et créés dans la poule (phase 'pool')
    matchs = Match.objects.filter(pool=pool, phase='pool').select_related('team_a', 'team_b')

    # On prépare les scores par sets (comme tu le fais déjà)
    for match in matchs:
        match.score_sets = []
        for i in range(1, 6):
            sa = getattr(match, f"set{i}_team_a", None)
            sb = getattr(match, f"set{i}_team_b", None)
            if sa is not None and sb is not None and (sa != 0 or sb != 0):
                match.score_sets.append({
                    'set_number': i,
                    'team_a_score': sa,
                    'team_b_score': sb
                })

    return render(request, 'detail_poule.html', {
        'pool': pool,
        'matchs': matchs,
        'tournament': tournament,
    })


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
from .models import Match, Pool, Ranking ,Organisateur


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


from django.shortcuts import render, redirect
from .models import Tournament
from django.contrib import messages
from django.utils.dateparse import parse_date

from django.utils.dateparse import parse_date
from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Tournament

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.dateparse import parse_date
from .models import Tournament

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tournament, Pool
from django.utils.dateparse import parse_date

from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').date()
 
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail


'''def create_tournament(request):

    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        department = request.POST.get('department')
        address = request.POST.get('address')
        is_indoor = request.POST.get('is_indoor') == 'on'
        start_date = parse_date(request.POST.get('start_date'))
        end_date = parse_date(request.POST.get('end_date'))
        sport = request.POST.get('sport')
        type_tournament = request.POST.get('type_tournament')

        # Additional fields
        nb_teams = request.POST.get('nb_teams')
        players_per_team = request.POST.get('players_per_team')
        nb_pools = request.POST.get('nb_pools', 0)
        nb_sets_to_win = request.POST.get('nb_sets_to_win')
        points_per_set = request.POST.get('points_per_set')
        email = request.POST.get('email')  # récupère l'email de l'organisateur

        # Basic validation
        if not all([name, department, start_date, end_date, sport, nb_teams, players_per_team, nb_sets_to_win, points_per_set, email]):
            messages.error(request, "Tous les champs requis ne sont pas remplis.")
            return redirect('create_tournament')

        # Conversion and validation
        try:
            nb_teams = int(nb_teams)
            players_per_team = int(players_per_team)
            nb_sets_to_win = int(nb_sets_to_win)
            points_per_set = int(points_per_set)

            if type_tournament == 'RR':
                if not nb_pools:
                    raise ValueError("Le nombre de pools est requis pour un tournoi à la ronde.")
                nb_pools = int(nb_pools)
            else:
                nb_pools = 0  # No pools needed for direct elimination
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('create_tournament')

        # Create the tournament
        tournoi = Tournament.objects.create(
            name=name,
            department=department,
            address=address,
            is_indoor=is_indoor,
            start_date=start_date,
            end_date=end_date,
            sport=sport,
            max_teams=nb_teams,
            players_per_team=players_per_team,
            number_of_pools=nb_pools,
            type_tournament=type_tournament,
            nb_sets_to_win=nb_sets_to_win,
            points_per_set=points_per_set,
        )

        # Create pools for this tournament if it's a round-robin tournament
        if type_tournament == 'RR':
            if not Pool.objects.filter(tournament=tournoi).exists():
                for i in range(1, nb_pools + 1):
                    pool_name = f"Pool {i}"
                    Pool.objects.create(name=pool_name, tournament=tournoi)

        # === Créer un utilisateur pour l'organisateur ===
        # === Créer un utilisateur pour l'organisateur ===
        try:
            username = f"{email}_{tournoi.id}"
            user = User.objects.create_user(username=username, email=email)
            
            # Créer l'Organisateur
            organisateur = Organisateur.objects.create(
                user=user
            )

            # Associer l'organisateur au tournoi
            tournoi.organizer = organisateur
            tournoi.save()

            # Envoyer le mail
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = '127.0.0.1:8000'
            link = f"http://{domain}/accounts/reset/{uid}/{token}/"

            subject = f"Bienvenue organisateur du tournoi {tournoi.name} !"
            message = f"""
        Bonjour,

        Vous avez été inscrit comme organisateur du tournoi "{tournoi.name}".
        Veuillez cliquer sur le lien suivant pour définir votre mot de passe :

        {link}

        Merci,
        L'équipe du tournoi
        """
            send_mail(subject, message, 'projetE3match@gmail.com', [email], fail_silently=False)

        except Exception as e:
            messages.error(request, f"Erreur lors de la création de l'utilisateur organisateur : {str(e)}")
            tournoi.delete()  # rollback si problème
            return redirect('create_tournament')

        # Save tournament details in session
        request.session['tournament_created_id'] = tournoi.id
        request.session['type_tournament'] = type_tournament
        request.session['nb_teams'] = nb_teams
        request.session['players_per_team'] = players_per_team
        request.session['nb_pools'] = nb_pools

        messages.success(request, f"Tournoi '{name}' créé avec succès.")
        return redirect('home')

    return render(request, 'create_tournament.html')
 
'''
def create_tournament_step1(request):
    if request.method == 'POST':
        # Enregistre les infos dans la session
        request.session['step1'] = {
            'name': request.POST.get('name'),
            'department': request.POST.get('department'),
            'address': request.POST.get('address'),
            'is_indoor': request.POST.get('is_indoor') == 'on',
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'sport': request.POST.get('sport'),
            'type_tournament': request.POST.get('type_tournament'),
            'nb_pools': request.POST.get('nb_pools'),
            'email': request.POST.get('email'),  # <<< ici tu ajoutes l'email
        }

        return redirect('create_tournament_step2')
    
    return render(request, 'create_tournament_step1.html')

def create_tournament_step2(request):
    print("🎯 create_tournament_step2 appelée :", request.method)
    if request.method == 'POST':
        print("📥 POST reçu :", request.POST)

    step1 = request.session.get('step1')
    if not step1:
        return redirect('create_tournament_step1')

    sport = step1['sport']
    type_tournament = step1['type_tournament']

    if request.method == 'POST':
        try:
            # Champs communs
            common_data = {
                'name': step1['name'],
                'department': step1['department'],
                'address': step1['address'],
                'is_indoor': step1['is_indoor'],
                'start_date': parse_date(step1['start_date']),
                'end_date': parse_date(step1['end_date']),
                'sport': sport,
                'type_tournament': type_tournament,
                'number_of_pools': int(step1.get('nb_pools') or 0),
                'max_teams': int(request.POST.get('nb_teams')),
                'players_per_team': int(request.POST.get('players_per_team')),
            }

            # Champs spécifiques par sport
            if sport == 'volleyball':
                common_data.update({
                    'nb_sets_to_win': int(request.POST.get('nb_sets_to_win')),
                    'points_per_set': int(request.POST.get('points_per_set')),
                })

            elif sport == 'football':
                common_data.update({
                    'match_duration': int(request.POST.get('match_duration')),
                    'extra_time': request.POST.get('extra_time') == 'on',
                    'penalty_shootout': request.POST.get('penalty_shootout') == 'on',
                    # Par défaut pour compatibilité avec le modèle :
                    'nb_sets_to_win': 1,
                    'points_per_set': 1,
                })

            elif sport == 'rugby':
                common_data.update({
                    'match_duration': int(request.POST.get('match_duration')),
                    'half_time_duration': int(request.POST.get('half_time_duration')),
                    'nb_sets_to_win': 1,
                    'points_per_set': 1,
                })

            elif sport == 'basketball':
                common_data.update({
                    'quarter_duration': int(request.POST.get('quarter_duration')),
                    'number_of_quarters': int(request.POST.get('number_of_quarters')),
                    'nb_sets_to_win': 1,
                    'points_per_set': 1,
                })

            # Email de l'organisateur
            email = step1.get('email')
            if not email:
                messages.error(request, "L'email de l'organisateur est requis.")
                return redirect('create_tournament_step1')

            # Créer le tournoi
            tournoi = Tournament.objects.create(**common_data)

            # Créer les pools si nécessaire
            if type_tournament == 'RR' and tournoi.number_of_pools > 0:
                if not Pool.objects.filter(tournament=tournoi).exists():
                    for i in range(1, tournoi.number_of_pools + 1):
                        pool_name = f"Pool {i}"
                        Pool.objects.create(name=pool_name, tournament=tournoi)

            # Créer l'utilisateur organisateur
            try:
                username = f"{email}_{tournoi.id}"
                user = User.objects.create_user(username=username, email=email)

                organisateur = Organisateur.objects.create(user=user)

                tournoi.organizer = organisateur
                tournoi.save()

                # Envoyer le mail
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                domain = '127.0.0.1:8000'
                link = f"http://{domain}/accounts/reset/{uid}/{token}/"

                subject = f"Bienvenue organisateur du tournoi {tournoi.name} !"
                message = f"""
Bonjour,

Vous avez été inscrit comme organisateur du tournoi "{tournoi.name}".
Veuillez cliquer sur le lien suivant pour définir votre mot de passe :

{link}

Merci,
L'équipe du tournoi
"""
                send_mail(subject, message, 'projetE3match@gmail.com', [email], fail_silently=False)

            except Exception as e:
                messages.error(request, f"Erreur lors de la création de l'utilisateur organisateur : {str(e)}")
                tournoi.delete()
                return redirect('create_tournament_step2')

            # Mettre le tournoi sélectionné en session
            request.session['selected_tournament_id'] = tournoi.id

            messages.success(request, f"Tournoi '{tournoi.name}' créé avec succès et sélectionné.")
            return redirect(f"{reverse('home')}?tournament_id={tournoi.id}")

        
        except Exception as e:
            import traceback
            print("ERREUR création tournoi:")
            traceback.print_exc()
            messages.error(request, f"Erreur lors de la création du tournoi : {str(e)}")
            return redirect('create_tournament_step2')


    return render(request, 'create_tournament_step2.html', {'sport': sport})

 
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest

def create_team(request, tournament_id):
    tournoi = get_object_or_404(Tournament, id=tournament_id)

    if tournoi.teams.count() >= tournoi.max_teams:
        return HttpResponseBadRequest("Nombre maximum d'équipes atteint pour ce tournoi.")

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        if team_name:
            Team.objects.create(name=team_name, tournament=tournoi)
            messages.success(request, f"Équipe '{team_name}' créée avec succès.")
            return redirect('some_view')  # adapter selon ta navigation

    return render(request, 'create_team.html', {'tournament': tournoi})

from django.views.generic import ListView
from .models import Tournament

class TournamentListView(ListView):
    model = Tournament
    template_name = 'tournament_list.html'
    context_object_name = 'tournois'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par sport
        sport = self.request.GET.get('sport')
        if sport:
            queryset = queryset.filter(sport=sport)
        
        # Filtrage par département
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        return queryset.order_by('start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sports'] = Tournament.SPORT_CHOICES
        context['selected_sport'] = self.request.GET.get('sport', '')
        context['selected_department'] = self.request.GET.get('department', '')
        return context
    
from django.views.generic import DetailView
from .models import Tournament

class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'tournament_detail.html'
    context_object_name = 'tournoi'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_navbar'] = True  # ✅ cacher la navbar sur cette page
        return context
    

    from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import Tournament, Team

from django.shortcuts import render, get_object_or_404, redirect
from .models import Tournament, Team

from django.shortcuts import render, get_object_or_404, redirect
from .models import Tournament, Team

def direct_elimination(request):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('home')

    tournament = get_object_or_404(Tournament, id=tournament_id)

    if tournament.type_tournament != 'DE':
        return redirect('home')

    teams = list(Team.objects.filter(tournament=tournament).order_by('id'))

    # Récupérer tous les matchs existants
    matches = Match.objects.filter(team_a__tournament=tournament, phase='quarter')
    match_lookup = {
        (m.team_a.id, m.team_b.id): m for m in matches
    }

    # Construire les paires avec match existant ou non
    matchups = []
    for i in range(0, len(teams), 2):
        team1 = teams[i]
        team2 = teams[i + 1] if i + 1 < len(teams) else None
        match = match_lookup.get((team1.id, team2.id)) if team2 else None
        matchups.append((team1, team2, match))

    return render(request, 'direct_elimination.html', {
        'tournament': tournament,
        'matchups': matchups,
    })




from .models import Match, Team, Tournament
def create_elimination_match(request):
    if request.method == 'POST':
        team_a_id = request.POST.get('team_a_id')
        team_b_id = request.POST.get('team_b_id')
        tournament_id = request.session.get('selected_tournament_id')

        if not (team_a_id and team_b_id and tournament_id):
            return redirect('direct_elimination')

        try:
            team_a = Team.objects.get(id=team_a_id)
            team_b = Team.objects.get(id=team_b_id)
            tournament = Tournament.objects.get(id=tournament_id)
        except (Team.DoesNotExist, Tournament.DoesNotExist):
            return redirect('direct_elimination')

        # Vérifie si un match identique existe déjà
        match = Match.objects.filter(
            team_a=team_a,
            team_b=team_b,
            phase='quarter'  # adapte si tu veux gérer les phases dynamiquement
        ).first()

        if not match:
            match = Match.objects.create(
                team_a=team_a,
                team_b=team_b,
                phase='quarter',
            )

        return redirect('score_match', match_id=match.id)

    return redirect('direct_elimination')

    



from django.shortcuts import render, get_object_or_404, redirect
from .models import Match

from django.shortcuts import render, get_object_or_404, redirect
from .models import Match

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Match, UserProfile
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import urlencode


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Match, UserProfile


def get_next_phase(current_phase):
    return {
        'eighth': 'quarter',
        'quarter': 'semi',
        'semi': 'final',
        'final': None,
    }.get(current_phase)


def advance_elimination_bracket(match):
    winner = match.winner_team
    if not winner or match.bracket_position is None:
        return

    current_phase = match.phase
    next_phase = get_next_phase(current_phase)
    if not next_phase:
        return

    tournament = match.tournament
    next_position = match.bracket_position // 2

    # Crée ou récupère le match de la phase suivante à la bonne position
    next_match, created = Match.objects.get_or_create(
        tournament=tournament,
        phase=next_phase,
        bracket_position=next_position,
        defaults={'team_a': None, 'team_b': None}
    )

    # Affecte le vainqueur à la bonne place dans le match suivant
    if match.bracket_position % 2 == 0:
        if not next_match.team_a:
            next_match.team_a = winner
    else:
        if not next_match.team_b:
            next_match.team_b = winner

    next_match.save()

    # Cas spécial : si l'autre match n’existe pas (adversaire manquant), auto-passage
    expected_opponent_bracket_pos = match.bracket_position ^ 1  # pair/impair
    opponent_exists = Match.objects.filter(
        tournament=tournament,
        phase=current_phase,
        bracket_position=expected_opponent_bracket_pos
    ).exists()

    if not opponent_exists:
        # L'équipe passe seule → victoire automatique
        next_match.winner_side = 'A' if next_match.team_a == winner else 'B'
        next_match.statut = 'T'
        next_match.save()
        # On fait avancer encore ce match vers la suite
        advance_elimination_bracket(next_match)


from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Match, UserProfile


def get_next_phase(current_phase):
    return {
        'eighth': 'quarter',
        'quarter': 'semi',
        'semi': 'final',
        'final': None,
    }.get(current_phase)


def advance_elimination_bracket(match):
    winner = match.winner_team
    if not winner or match.bracket_position is None:
        return

    current_phase = match.phase
    next_phase = get_next_phase(current_phase)
    if not next_phase:
        return

    tournament = match.tournament
    next_position = match.bracket_position // 2

    # Crée ou récupère le match de la phase suivante à la bonne position
    next_match, created = Match.objects.get_or_create(
        tournament=tournament,
        phase=next_phase,
        bracket_position=next_position,
        defaults={'team_a': None, 'team_b': None}
    )

    # Affecte le vainqueur à la bonne place dans le match suivant
    if match.bracket_position % 2 == 0:
        if not next_match.team_a:
            next_match.team_a = winner
    else:
        if not next_match.team_b:
            next_match.team_b = winner

    next_match.save()

    # Cas spécial : si l'autre match n’existe pas (adversaire manquant), auto-passage
    expected_opponent_bracket_pos = match.bracket_position ^ 1  # pair/impair
    opponent_exists = Match.objects.filter(
        tournament=tournament,
        phase=current_phase,
        bracket_position=expected_opponent_bracket_pos
    ).exists()

    if not opponent_exists:
        # L'équipe passe seule → victoire automatique
        next_match.winner_side = 'A' if next_match.team_a == winner else 'B'
        next_match.statut = 'T'
        next_match.save()
        # On fait avancer encore ce match vers la suite
        advance_elimination_bracket(next_match)


@login_required
def score_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    user = request.user

    if user.is_superuser:
        authorized = True
    else:
        try:
            user_profile = user.userprofile
            user_team = user_profile.team

            if user_team == match.team_a and match.team_a.captain == user_profile:
                authorized = True
            elif user_team == match.team_b and match.team_b.captain == user_profile:
                authorized = True
            else:
                authorized = False
        except UserProfile.DoesNotExist:
            authorized = False

    # 🔥 On regarde si on a été appelé avec ?from=phase_finale
    from_param = request.GET.get('from')

    if not authorized:
        tournament_id = None
        if match.pool:
            tournament_id = match.pool.tournament.id
        elif match.team_a and match.team_a.tournament:
            tournament_id = match.team_a.tournament.id

        return render(request, 'no_team.html', {
            'error': "Vous n’avez pas le droit de modifier ce match.",
            'pool_id': match.pool.id if match.pool else None,
            'from_param': from_param,
            'tournament_id': tournament_id,
        })

    tournament = match.pool.tournament if match.pool else match.team_a.tournament

    nb_sets_display = min(2 * tournament.nb_sets_to_win - 1, 5)
    set_numbers = list(range(1, nb_sets_display + 1))

    score_fields = {}
    for set_number in set_numbers:
        score_fields[f'set{set_number}_team_a'] = getattr(match, f'set{set_number}_team_a')
        score_fields[f'set{set_number}_team_b'] = getattr(match, f'set{set_number}_team_b')

    if request.method == 'POST':
        for set_number in set_numbers:
            a_field = f'set{set_number}_team_a'
            b_field = f'set{set_number}_team_b'
            value_a = request.POST.get(a_field, '')
            value_b = request.POST.get(b_field, '')
            setattr(match, a_field, int(value_a) if value_a.isdigit() else 0)
            setattr(match, b_field, int(value_b) if value_b.isdigit() else 0)

        winner = match.get_auto_winner(tournament.nb_sets_to_win)
        match.winner_side = 'A' if winner == match.team_a else 'B' if winner == match.team_b else None

        if winner:
            match.statut = 'T'
        elif any(getattr(match, f'set{i}_team_a', 0) != 0 or getattr(match, f'set{i}_team_b', 0) != 0 for i in set_numbers):
            match.statut = 'EC'
        else:
            match.statut = 'ND'

        match.save()

        if match.phase == 'pool' and match.pool:
            match.pool.calculate_rankings()
        else:
            advance_elimination_bracket(match)

        # 🔥 Après POST → redirection adaptée
        if match.phase == 'pool' and match.pool:
            return redirect('detail_poule', pool_id=match.pool.id)
        elif from_param == 'phase_finale':
            url = reverse('liste_matchs_phase_finale')
            params = urlencode({'tournament_id': match.tournament.id})
            full_url = f"{url}?{params}"
            return HttpResponseRedirect(full_url)
        else:
            return redirect('direct_elimination')

    # 🔥 Back url pour le bouton "Retour"
    if match.phase == 'pool' and match.pool:
        back_url = reverse('detail_poule', args=[match.pool.id])
    elif from_param == 'phase_finale':
        back_url = reverse('liste_matchs_phase_finale') + f'?tournament_id={match.tournament.id}'
    else:
        back_url = reverse('direct_elimination')

    return render(request, 'score_match.html', {
        'match': match,
        'back_url': back_url,
        'set_numbers': set_numbers,
        'score_fields': score_fields,
    })


def home_landing(request):
    return render(request, 'home_landing.html', {'hide_navbar': True})
 

from django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pool, Ranking, Tournament, Match, Team

def afficher_deux_premiers(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Vérifie si les matchs ont déjà été créés pour la phase finale
    matchs_existent = Match.objects.filter(tournament=tournament, phase='quarter').exists()

    pools = Pool.objects.filter(tournament=tournament)
    data = []
    qualified_teams = []

    for pool in pools:
        pool.calculate_rankings()
        top_rankings = Ranking.objects.filter(team__pool=pool).order_by('rank')[:2]
        data.append({
            'pool': pool,
            'rankings': top_rankings
        })
        qualified_teams.extend([ranking.team for ranking in top_rankings])

    nb_matches = len(qualified_teams) // 2
    match_range = range(nb_matches)

    if request.method == 'POST' and not matchs_existent:
        created_match_ids = []

        for i in match_range:
            team_a_id = request.POST.get(f'team_a_{i}')
            team_b_id = request.POST.get(f'team_b_{i}')

            if team_a_id and team_b_id and team_a_id != team_b_id:
                match = Match.objects.create(
                    team_a_id=team_a_id,
                    team_b_id=team_b_id,
                    tournament=tournament,
                    phase='quarter',
                    statut='ND',
                    bracket_position=i  # 🔥 ceci est la clé pour enchaîner les phases

                )
                created_match_ids.append(match.id)

        request.session['created_match_ids'] = created_match_ids
        return redirect('matchs_choice')

    return render(request, 'matchs_finale.html', {
        'data': data,
        'tournament': tournament,
        'qualified_teams': qualified_teams,
        'match_range': match_range,
        'matchs_existent': matchs_existent,  # ← on passe cette info au template
    })



from django.shortcuts import render
from .models import Match

from django.shortcuts import render
from .models import Match

from django.shortcuts import render, get_object_or_404
from .models import Match, Tournament

def liste_matchs_phase_finale(request):
    tournament_id = request.GET.get('tournament_id')
    if not tournament_id:
        return render(request, 'liste_matchs_phase_finale.html', {
            'match_groups': [],
            'message': "Aucun tournoi spécifié."
        })

    tournament = get_object_or_404(Tournament, id=tournament_id)

    # Toutes les phases dans l’ordre logique
    phase_order = ['eighth', 'quarter', 'semi', 'final', 'third_place']

    # Libellés dynamiques si besoin
    phase_labels_default = {
        'eighth': "Huitièmes de finale",
        'quarter': "Quarts de finale",
        'semi': "Demi-finales",
        'final': "Finale",
        'third_place': "Petite finale"
    }

    match_groups = []

    for phase in phase_order:
        matchs = Match.objects.filter(
            tournament=tournament,
            phase=phase,
            team_a__isnull=False,
            team_b__isnull=False
        ).order_by('id')

        if matchs.exists():
            count = matchs.count()
            # Adapter dynamiquement le nom pour la première phase si besoin
            if phase == 'quarter' and count == 2:
                label = "Demi-finales"
            elif phase == 'quarter' and count == 1:
                label = "Finale"
            elif phase == 'quarter' and count == 4:
                label = "Quarts de finale"
            elif phase == 'quarter' and count == 8:
                label = "Huitièmes de finale"
            else:
                label = phase_labels_default.get(phase, phase)

            match_groups.append({
                'label': label,
                'matchs': matchs
            })

    message = (
        "Matchs de phase finale pour ce tournoi." if match_groups
        else "Aucun match n’a été créé pour ce tournoi."
    )

    return render(request, 'liste_matchs_phase_finale.html', {
        'match_groups': match_groups,
        'message': message
    })
