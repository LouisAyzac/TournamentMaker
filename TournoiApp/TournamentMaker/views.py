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

def home(request):
    # Gestion sélection tournoi → stocker en session
    if 'tournament_id' in request.GET:
        selected_id = request.GET.get('tournament_id')
        tournoi = get_object_or_404(Tournament, id=selected_id)
        request.session['selected_tournament_id'] = tournoi.id
        request.session['selected_tournament_name'] = tournoi.name
        return redirect('dashboard')

    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:
            tournoi = get_object_or_404(Tournament, id=selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            return redirect('dashboard')

    # Gestion affichage
    today = now().date()
    category = request.GET.get('category', 'all')

    if category == 'ongoing':
        tournois = Tournament.objects.filter(start_date__lte=today, end_date__gte=today)
    elif category == 'upcoming':
        tournois = Tournament.objects.filter(start_date__gt=today)
    elif category == 'past':
        tournois = Tournament.objects.filter(end_date__lt=today)
    elif category == 'all':  # 🆕 ici → pour afficher tous les tournois
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
        'hide_navbar': True,
    }

    return render(request, 'home.html', context)


def index(request):
    num_Player = Player.objects.count()
    return render(request, 'index.html', {'num_Player': num_Player})

def landing(request):
    request.session.pop("selected_tournament", None)
    return render(request, 'landing.html')

from django.utils.timezone import now
from django.shortcuts import get_object_or_404

def dashboard(request):
    selected_id = request.session.get('selected_tournament_id')
    if not selected_id:
        return redirect('home')

    tournoi = get_object_or_404(Tournament, id=selected_id)

    today = now().date()

    if tournoi.start_date > today:
        statut = "À venir"
    elif tournoi.end_date < today:
        statut = "Terminé"
    else:
        statut = "En cours"

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

    team = get_object_or_404(Team, pk=pk, tournament_id=tournament_id)
    tournament = get_object_or_404(Tournament, id=tournament_id)
    ranking = Ranking.objects.filter(team=team).first()

    teams = Team.objects.filter(tournament_id=tournament_id)
    matches = Match.objects.filter(team_a__tournament_id=tournament_id)

    points = {t.id: 0 for t in teams}
    pool_wins = {t.id: 0 for t in teams}

    def get_winner(match, sets_to_win):
        score_a, score_b = 0, 0
        max_sets = sets_to_win * 2 - 1

        for i in range(1, max_sets + 1):
            set_team_a = getattr(match, f'set{i}_team_a', None)
            set_team_b = getattr(match, f'set{i}_team_b', None)
            if set_team_a is None or set_team_b is None:
                break
            if set_team_a > set_team_b:
                score_a += 1
            elif set_team_b > set_team_a:
                score_b += 1

            if score_a == sets_to_win:
                return match.team_a
            if score_b == sets_to_win:
                return match.team_b

        return None

    for match in matches:
        winner = get_winner(match, sets_to_win)
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
    final_ranking = {t.id: rank + 1 for rank, t in enumerate(sorted_teams)}

    return points, final_ranking

def team_detail(request, pk):
    tournament_id = request.session.get('selected_tournament_id')
    if not tournament_id:
        return redirect('select_tournament')

    team = get_object_or_404(Team, pk=pk, tournament_id=tournament_id)
    tournament = get_object_or_404(Tournament, id=tournament_id)

    teams = Team.objects.filter(tournament_id=tournament_id)
    matches = Match.objects.filter(team_a__tournament_id=tournament_id).select_related('team_a', 'team_b')

    points, final_ranking = calculate_team_points_and_ranking(teams, matches, tournament.nb_sets_to_win)
    final_rank = final_ranking.get(team.id)

    return render(request, 'teams_detail.html', {
        'team': team,
        'ranking': points.get(team.id, 0),  # Points de l'équipe
        'final_rank': final_rank,           # Classement final
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
    return render(request, 'rankings.html', {'pool_rankings': pool_rankings})


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


        # Répartir l'équipe dans les pools disponibles du tournoi → avec têtes de séries
        pools = Pool.objects.filter(tournament=tournament)

        # 1️⃣ Calcul du "score" de l'équipe en cours d'inscription (somme des niveaux des joueurs)
        team_score = 0

        # On initialise l'équipe (vide) pour pouvoir lui affecter des joueurs ensuite
        team = Team.objects.create(name=team_name, tournament=tournament)

        # Pour savoir combien de joueurs vont être inscrits (on le passe à la boucle après)
        players_data = []

        # On lit les données du POST et on prépare les joueurs + score
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

                # On stocke les infos pour créer les joueurs plus tard
                players_data.append({
                    'first_name': first_name,
                    'last_name': last_name,
                    'birth_date': birthdate,
                    'email': email,
                    'level': level
                })

                # On incrémente le score de l'équipe
                team_score += level

        # 2️⃣ On calcule les forces actuelles des Pools
        pool_strength = []

        for pool in pools:
            teams_in_pool = pool.teams.all()
            total_score = 0
            team_count = teams_in_pool.count()

            # On calcule le score total des équipes de la Pool
            for t in teams_in_pool:
                team_players = t.players.all()
                score = sum(int(player.level) for player in team_players)
                total_score += score

            # On stocke le score moyen actuel de la Pool
            avg_score = total_score / team_count if team_count > 0 else 0
            pool_strength.append((pool, avg_score, team_count))

        # 3️⃣ On trie les Pools :
        # - on privilégie les Pools ayant le moins d'équipes
        # - en cas d'égalité, on choisit celle avec la force moyenne la plus adaptée

        # On trie par : (nb d'équipes, écart entre force moyenne et score de l'équipe)
        pool_strength.sort(key=lambda x: (x[2], abs(x[1] - team_score)))

        # 4️⃣ On choisit la Pool optimale
        if not pool_strength:
            return render(request, 'signup.html', {
                'error': 'Aucune poule disponible pour ce tournoi. Veuillez contacter l\'organisateur.',
                'players_per_team': players_per_team,
                'total_players': total_players
            })
        pool_to_assign = pool_strength[0][0]

        # 5️⃣ On assigne l'équipe à la Pool
        team.pool = pool_to_assign
        team.save()

        # 6️⃣ On crée les joueurs
        capitaine_valide = False

        for i, player_data in enumerate(players_data):
            player = Player.objects.create(
                first_name=player_data['first_name'],
                last_name=player_data['last_name'],
                birth_date=player_data['birth_date'],
                level=player_data['level'],
                email=player_data['email'] if player_data['email'] else '',
                team=team,
            )

            if i == 0:
                # Création du User pour le capitaine
                email = player_data['email']
                username = f"{email}_{team.id}"
                user = User.objects.create_user(username=username, email=email)
                user_profile = UserProfile.objects.create(user=user, level=player_data['level'], team=team)

                team.captain = user_profile
                team.save()

                # Générer le lien pour la réinitialisation du mot de passe
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

        # 7️⃣ En cas de problème → rollback de l'équipe
        if not capitaine_valide:
            team.delete()  # Supprimer l'équipe si pas de capitaine valide
            return render(request, 'signup.html', {
                'error': 'Le capitaine est obligatoire.',
                'players_per_team': players_per_team,
                'total_players': total_players
            })
        
        # ✅ Si tout s'est bien passé, rediriger vers la page de succès
        return redirect('signup_success')
    
        # Si on arrive ici (GET), afficher le formulaire
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

def match_choice(request):
    # Exemple : récupérer l'ID tournoi dans l'URL ou session
    tournament_id = request.GET.get('tournament_id') or request.session.get('selected_tournament_id')

    if not tournament_id:
        # Pas d'ID tournoi, rediriger ou erreur
        return render(request, 'matchs_choice.html', {'error': 'Aucun tournoi sélectionné'})

    try:
        tournament = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return render(request, 'matchs_choice.html', {'error': 'Tournoi introuvable'})

    return render(request, 'matchs_choice.html', {'tournament': tournament})


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

def matchs_poules(request, tournament_id): 
    tournament = get_object_or_404(Tournament, id=tournament_id)
    pools_data = []

    # 🔥 On filtre les pools du tournoi en question
    pools = Pool.objects.filter(tournament=tournament)
    print("Pools récupérées :", pools)  # Debugging, vérifier si on récupère bien des pools

    if not pools:
        print("Aucune pool trouvée pour ce tournoi.")  # Si aucune pool n'est trouvée

    for pool in pools.prefetch_related('teams'):
        stats = []

        for team in pool.teams.all():
            matchs_joues = Match.objects.filter(pool=pool, phase='pool')\
                .filter(Q(team_a=team) | Q(team_b=team))\
                .exclude(statut='ND')

            total_joues = matchs_joues.count()
            victoires = sum(1 for match in matchs_joues if match.winner_team == team)
            defaites = total_joues - victoires
            points = victoires * 3  # 3 points par victoire

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

    print("Pools data envoyées :", pools_data)  # Vérifier si les données sont bien envoyées

    return render(request, 'matchs_poules.html', {
        'pools_data': pools_data,
        'tournament': tournament
    })



# Détail d'une poule
def detail_poule(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    tournament = pool.tournament  # assuming your Pool model has a ForeignKey to Tournament

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

    return render(request, 'detail_poule.html', {
        'pool': pool,
        'matchs': matchs,
        'tournament': tournament,  # <-- Ajoute ça !
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

def create_tournament(request): 
    if request.method == 'POST':
        name = request.POST.get('name')
        department = request.POST.get('department')
        address = request.POST.get('address')
        is_indoor = request.POST.get('is_indoor') == 'on'
        start_date = parse_date(request.POST.get('start_date'))
        end_date = parse_date(request.POST.get('end_date'))
        sport = request.POST.get('sport')

        # Champs supplémentaires
        nb_teams = request.POST.get('nb_teams')
        players_per_team = request.POST.get('players_per_team')
        nb_pools = request.POST.get('nb_pools')
        nb_sets_to_win = request.POST.get('nb_sets_to_win')  # Nouveau champ
        points_per_set = request.POST.get('points_per_set')  # Nouveau champ

        # Validation basique
        if not all([name, department, start_date, end_date, sport, nb_teams, players_per_team, nb_sets_to_win, points_per_set]):
            messages.error(request, "Tous les champs requis ne sont pas remplis.")
            return redirect('create_tournament')

        # Vérification et conversion
        try:
            nb_teams = int(nb_teams)
            players_per_team = int(players_per_team)
            
            nb_pools = int(nb_pools)  # Assure-toi que nb_pools est un entier
        except ValueError:
            messages.error(request, "Le nombre d'équipes, de joueurs par équipe et de pools doivent être des entiers.")
            
            nb_sets_to_win = int(nb_sets_to_win)  # Conversion
            points_per_set = int(points_per_set)  # Conversion
        except ValueError:
            messages.error(request, "Veuillez saisir des valeurs numériques valides.")
            
            return redirect('create_tournament')

        # Création du tournoi avec les nouveaux champs
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
            nb_sets_to_win=nb_sets_to_win,  # Nouveau champ
            points_per_set=points_per_set,  # Nouveau champ
        )

        # Créer les pools pour ce tournoi
        for i in range(1, nb_pools + 1):
            pool_name = f"Pool {i}"
            Pool.objects.create(name=pool_name, tournament=tournoi)

        # Sauvegarde optionnelle en session
        request.session['tournament_created_id'] = tournoi.id
        request.session['nb_teams'] = nb_teams
        request.session['players_per_team'] = players_per_team
        request.session['nb_pools'] = nb_pools

        messages.success(request, f"Tournoi '{name}' créé avec succès.")
        return redirect('home')

    return render(request, 'create_tournament.html')

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
    
from django.shortcuts import render, get_object_or_404
from itertools import combinations
from .models import Pool, Team

from django.shortcuts import render, get_object_or_404
from itertools import combinations
from .models import Pool, Team

from django.shortcuts import render, get_object_or_404
from itertools import combinations
from .models import Pool, Team, Match

def detail_poule(request, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    teams = pool.teams.all()
    matchs = Match.objects.filter(pool=pool).select_related('team_a', 'team_b')

    # Générer les matchs possibles
    possible_matches = list(combinations(teams, 2))

    return render(request, 'detail_poule.html', {
        'pool': pool,
        'teams': teams,
        'matchs': matchs,
        'possible_matches': possible_matches
    })
