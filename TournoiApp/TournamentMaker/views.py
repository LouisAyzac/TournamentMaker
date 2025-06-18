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

        return redirect('dashboard', tournament_slug=tournoi.slug)  # Correction ici ✅

    if request.method == 'POST':
        selected_id = request.POST.get('tournament_id')
        if selected_id:
            tournoi = get_object_or_404(Tournament, id=selected_id)
            request.session['selected_tournament_id'] = tournoi.id
            request.session['selected_tournament_name'] = tournoi.name
            request.session['type_tournament'] = tournoi.type_tournament
            return redirect('dashboard', tournament_slug=tournoi.slug)  # Correction ici ✅

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

def dashboard(request, tournament_slug):
    # On ne prend plus selected_id depuis la session → on utilise tournament_slug
    tournoi = get_object_or_404(Tournament, slug=tournament_slug)
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

def teams(request, tournament_slug):
    tournoi = get_object_or_404(Tournament, slug=tournament_slug)

    all_teams = tournoi.teams.all()


    all_teams = Team.objects.filter(tournament_id=tournoi.id)

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

    return render(request, 'teams.html', {
    'teams': all_teams,
    'tournament_slug': tournament_slug,  # <-- passe le slug au template
        })
from django.shortcuts import render, get_object_or_404
from TournamentMaker.models import Player, Team


def player_detail(request, tournament_slug, pk):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)
    player = get_object_or_404(Player, pk=pk, team__tournament=tournament)

    return render(request, 'players_detail.html', {
        'player': player,
        'tournament_slug': tournament_slug,
    })




from TournamentMaker.models import Team, Ranking    

from TournamentMaker.models import Team, Ranking
from django.shortcuts import get_object_or_404, render

from django.shortcuts import get_object_or_404, render
from TournamentMaker.models import Team, Ranking, Match

def team_detail(request, pk, tournament_slug):
    # Récupérer le tournoi par son slug
    tournament = get_object_or_404(Tournament, slug=tournament_slug)

    # Récupérer l'équipe liée à ce tournoi
    team = get_object_or_404(Team, pk=pk, tournament=tournament)

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

    # On passe tout au template, y compris le slug pour faciliter les liens
    return render(request, 'teams_detail.html', {
        'team': team,
        'ranking': ranking,
        'tournament_slug': tournament_slug,
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

from django.shortcuts import get_object_or_404, render

def rankings_list(request, tournament_slug):
    # Récupération du tournoi via le slug
    tournoi = get_object_or_404(Tournament, slug=tournament_slug)

    # ---------- 1. Classements par poule ----------
    pool_rankings = []
    pools = Pool.objects.filter(tournament=tournoi)

    for pool in pools:
        rankings = (
            Ranking.objects
            .filter(team__in=pool.teams.all())
            .select_related('team')
            .order_by('rank')
        )
        pool_rankings.append({'pool': pool, 'rankings': rankings})

    # ---------- 2. Vainqueur & finaliste ----------
    winner = finalist = third_place = None

    final_match = (
        Match.objects
        .filter(
            tournament=tournoi,
            phase='final',
            team_a__isnull=False,
            team_b__isnull=False
        )
        .first()
    )

    if final_match and final_match.winner_side:
        winner = final_match.team_a if final_match.winner_side == 'A' else final_match.team_b
        finalist = final_match.team_b if final_match.winner_side == 'A' else final_match.team_a

    # ---------- 3. Troisième place (petite finale) ----------
    third_place_match = (
        Match.objects
        .filter(
            tournament=tournoi,
            phase='third_place',
            team_a__isnull=False,
            team_b__isnull=False,
            statut='T'  # terminé uniquement
        )
        .first()
    )

    if third_place_match and third_place_match.winner_side:
        third_place = (
            third_place_match.team_a if third_place_match.winner_side == 'A'
            else third_place_match.team_b
        )

    # ---------- 4. Rendu ----------
    return render(request, 'rankings.html', {
        'pool_rankings': pool_rankings,
        'winner':        winner,
        'finalist':      finalist,
        'third_place':   third_place,  # ← ajouté ici
        'tournament':    tournoi,
        'tournament_slug': tournoi.slug,
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


def signup(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)

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
        return redirect('signup_success', tournament_slug=tournament.slug)


    return render(request, 'signup.html', {
        'players_per_team': players_per_team,
        'total_players': total_players
    })

 
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tournament   # adapte le chemin si besoin

def signup_success(request, tournament_slug):
    print("Page de succès atteinte.")
    return render(request, 'signup_success.html', {
        'selected_tournament_slug': tournament_slug
    })


# === 🆕 Matchs ===

# Choix entre les phases
from django.shortcuts import render
from .models import Tournament

from django.shortcuts import render, get_object_or_404
from .models import Tournament

def match_choice(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)
    return render(request, 'matchs_choice.html', {'tournament': tournament})

    if not tournament:
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

from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .models import Tournament, Pool, Match

def matchs_poules(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)
    pools_data = []

    pools = Pool.objects.filter(tournament=tournament)

    for pool in pools.prefetch_related('teams'):
        stats = []

        for team in pool.teams.all():
            # On récupère les matchs joués de cette équipe dans cette pool
            matchs_joues = Match.objects.filter(pool=pool, phase='pool')\
                .filter(Q(team_a=team) | Q(team_b=team))\
                .exclude(statut='ND')

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

                    # Pour les points : somme directe
                    if match.team_a == team:
                        diff_points += score_a - score_b
                    elif match.team_b == team:
                        diff_points += score_b - score_a

                    # Pour les sets : on compte le set gagné
                    if match.team_a == team:
                        if score_a > score_b:
                            diff_sets += 1
                        elif score_a < score_b:
                            diff_sets -= 1
                    elif match.team_b == team:
                        if score_b > score_a:
                            diff_sets += 1
                        elif score_b < score_a:
                            diff_sets -= 1


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

        pools_data.append({'pool': pool, 'stats': stats})

    return render(request, 'matchs_poules.html', {
        'pools_data': pools_data,
        'tournament': tournament
    })

 
# Détail d'une poule
from django.shortcuts import render, get_object_or_404
from .models import Pool, Match

def detail_poule(request, tournament_slug, pool_id):
    pool = get_object_or_404(Pool, pk=pool_id)
    tournament = pool.tournament

    if tournament.slug != tournament_slug:
        return redirect('detail_poule', tournament_slug=tournament.slug, pool_id=pool.id)

    # On récupère tous les matchs de poule
    all_matchs = list(Match.objects.filter(pool=pool, phase='pool').select_related('team_a', 'team_b'))

    # Récupère toutes les équipes de la poule
    teams = list(pool.teams.all())

    # Ordre équilibré des matchs basé sur les équipes
    scheduled_pairs = generate_balanced_schedule(teams)

    # On réorganise les matchs selon cet ordre
    ordered_matchs = []
    for team_a, team_b in scheduled_pairs:
        match = next(
            (m for m in all_matchs if {m.team_a, m.team_b} == {team_a, team_b}),
            None
        )
        if match:
            ordered_matchs.append(match)

    # Calcul des scores set par set pour chaque match
    for match in ordered_matchs:
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
        'matchs': ordered_matchs,
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
from django.utils.text import slugify
def create_tournament_step1(request):
    if request.method == 'POST':
        preset_key = request.POST.get('preset')  # nom technique du preset
        preset_name_map = {
            'volley_classique': 'Volleyball Classique',
            'foot_5v5': 'Football 5v5 Indoor',
            'basket_standard': 'Basketball Standard',
        }

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
            'email': request.POST.get('email'),
            'preset_name': preset_name_map.get(preset_key, 'non spécifié'),  # ✅ ajouté
        }

        return redirect('create_tournament_step2')

    return render(request, 'create_tournament_step1.html')


def create_tournament_step2(request):
    step1 = request.session.get('step1')
    if not step1:
        return redirect('create_tournament_step1')

    sport = step1['sport']
    type_tournament = step1['type_tournament']
    preset_name = step1.get('preset_name', 'non spécifié')

    sport_presets = {
        'volleyball': {
            'nb_teams': 8,
            'players_per_team': 6,
            'nb_sets_to_win': 3,
            'points_per_set': 25
        },
        'football': {
            'nb_teams': 12,
            'players_per_team': 11,
            'match_duration': 90,
            'extra_time': True,
            'penalty_shootout': True
        },
        'rugby': {
            'nb_teams': 10,
            'players_per_team': 15,
            'match_duration': 80,
            'half_time_duration': 10
        },
        'basketball': {
            'nb_teams': 6,
            'players_per_team': 5,
            'quarter_duration': 10,
            'number_of_quarters': 4
        }
    }

    preset = sport_presets.get(sport, {})

    if request.method == 'POST':
        try:
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
                'slug': slugify(step1['name']),
            }

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

            email = step1.get('email')
            if not email:
                messages.error(request, "L'email de l'organisateur est requis.")
                return redirect('create_tournament_step1')

            tournoi = Tournament.objects.create(**common_data)

            if type_tournament == 'RR' and tournoi.number_of_pools > 0:
                if not Pool.objects.filter(tournament=tournoi).exists():
                    for i in range(1, tournoi.number_of_pools + 1):
                        Pool.objects.create(name=f"Pool {i}", tournament=tournoi)

            try:
                username = f"{email}_{tournoi.id}"
                user = User.objects.create_user(username=username, email=email)
                organisateur = Organisateur.objects.create(user=user)
                tournoi.organizer = organisateur
                tournoi.save()

                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                domain = '127.0.0.1:8000'
                link = f"http://{domain}/accounts/reset/{uid}/{token}/"

                send_mail(
                    f"Bienvenue organisateur du tournoi {tournoi.name} !",
                    f"""Bonjour,

Vous avez été inscrit comme organisateur du tournoi "{tournoi.name}".
Veuillez cliquer sur le lien suivant pour définir votre mot de passe :

{link}

Merci,
L'équipe du tournoi
""",
                    'projetE3match@gmail.com',
                    [email],
                    fail_silently=False
                )

            except Exception as e:
                messages.error(request, f"Erreur création organisateur : {str(e)}")
                tournoi.delete()
                return redirect('create_tournament_step2')

            request.session['selected_tournament_id'] = tournoi.id
            messages.success(request, f"Tournoi '{tournoi.name}' créé avec succès et sélectionné.")
            return redirect(f"{reverse('home')}?tournament_id={tournoi.id}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f"Erreur : {str(e)}")
            return redirect('create_tournament_step2')

    return render(request, 'create_tournament_step2.html', {
        'sport': sport,
        'preset': preset,
        'preset_name': preset_name,
        'hide_navbar_buttons': True,  
    })



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
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
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

from django.shortcuts import render, get_object_or_404, redirect
from .models import Tournament, Match
from django.contrib import messages

from math import ceil, log2
from django.shortcuts import render, get_object_or_404, redirect
from math import ceil, log2
from .models import Tournament, Match, Team

from django.shortcuts import render, get_object_or_404, redirect
from math import ceil, log2
from .models import Tournament, Match

from django.shortcuts import get_object_or_404, render, redirect
from math import ceil, log2
from TournamentMaker.models import Tournament, Match

def direct_elimination(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)

    if tournament.type_tournament != 'DE':
        return redirect('home')

    phase_order = [
        ('sixteenth', 'Seizièmes'),
        ('eighth', 'Huitièmes'),
        ('quarter', 'Quarts'),
        ('semi', 'Demi-finales'),
        ('final', 'Finale'),
    ]

    phases_present = []
    has_matches = False

    for phase_code, phase_label in phase_order:
        matches = Match.objects.filter(tournament=tournament, phase=phase_code).order_by('bracket_position')
        if matches.exists():
            has_matches = True
            phases_present.append((phase_code, phase_label, list(matches)))  # ✅ uniquement si des matchs

    third_place_matches = Match.objects.filter(tournament=tournament, phase='third_place').order_by('bracket_position')
    if third_place_matches.exists():
        has_matches = True
        phases_present.append(('third_place', 'Petite finale', list(third_place_matches)))

    return render(request, 'direct_elimination.html', {
        'tournament': tournament,
        'phases_present': phases_present,
        'has_matches': has_matches,
    })


from .models import Match, Team, Tournament
def create_elimination_match(request,tournament_slug):
    if request.method == 'POST':
        team_a_id = request.POST.get('team_a_id')
        team_b_id = request.POST.get('team_b_id')
        tournament_id = request.session.get('selected_tournament_id')

        if not (team_a_id and team_b_id and tournament_id):
            reverse('direct_elimination', args=[tournament_slug])

        try:
            team_a = Team.objects.get(id=team_a_id)
            team_b = Team.objects.get(id=team_b_id)
            tournament = Tournament.objects.get(id=tournament_id)
        except (Team.DoesNotExist, Tournament.DoesNotExist):
            reverse('direct_elimination', args=[tournament_slug])

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

    return redirect('direct_elimination', args=[tournament_slug])

    



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
    # ───── 1. Vainqueur et perdant ─────
    if match.winner_side == 'A':
        winner = match.team_a
        loser = match.team_b
    elif match.winner_side == 'B':
        winner = match.team_b
        loser = match.team_a
    else:
        return

    if not winner or match.bracket_position is None:
        return

    current_phase = match.phase
    next_phase = get_next_phase(current_phase)
    if not next_phase:
        return

    tournament = match.tournament or (match.pool.tournament if match.pool else None)
    if not tournament:
        return

    # ───── 2. Bracket position ─────
    if current_phase == 'eighth':
        next_position = 100 + (match.bracket_position // 2)

    elif current_phase == 'quarter':
        total_quarters = Match.objects.filter(
            tournament=tournament,
            phase='quarter'
        ).count()

        if total_quarters == 2:
            next_position = 1  # Cas 3 poules : 2 quarts → tous dans demi 1
        elif match.bracket_position in (0, 1):
            next_position = 0  # Quarts 0-1 → demi 0
        else:
            next_position = 1  # Quarts 2-3 → demi 1
    else:
        next_position = match.bracket_position // 2

    # ───── 3. Récupération / création du match suivant ─────
    next_match, _ = Match.objects.get_or_create(
        tournament=tournament,
        phase=next_phase,
        bracket_position=next_position,
        defaults={'team_a': None, 'team_b': None, 'statut': 'ND'}
    )

    # ───── 4. Placement du vainqueur ─────
    if match.bracket_position >= 100:  # quarts spéciaux (3 poules)
        even_index = (match.bracket_position - 100) % 2 == 0
    else:
        even_index = match.bracket_position % 2 == 0

    target_is_a = even_index
    target_field = 'team_a' if target_is_a else 'team_b'

    already_there = getattr(next_match, target_field)
    if already_there and already_there != winner:
        next_match = Match.objects.create(
            tournament=tournament,
            phase=next_phase,
            bracket_position=next_position + 1000,
            statut='ND'
        )

    setattr(next_match, target_field, winner)
    next_match.save()

    # ───── 5. Ajout automatique à la petite finale ─────
    if current_phase == 'semi' and loser:
        third_place, _ = Match.objects.get_or_create(
            tournament=tournament,
            phase='third_place',
            bracket_position=0,
            defaults={'team_a': None, 'team_b': None, 'statut': 'ND'}
        )
        if not third_place.team_a:
            third_place.team_a = loser
        elif not third_place.team_b and third_place.team_a != loser:
            third_place.team_b = loser
        third_place.save()

    # ───── 6. Propagation récursive ─────
    if next_match.statut == 'T' and next_match.winner_side in ('A', 'B'):
        advance_elimination_bracket(next_match)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Tournament, Match

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Match, UserProfile

 


@login_required

def score_match(request, tournament_slug, match_id):
    from_param = request.GET.get('from')
    tournament = get_object_or_404(Tournament, slug=tournament_slug)
    match = get_object_or_404(Match, id=match_id)

    if match.pool:
        match_tournament = match.pool.tournament
    else:
        match_tournament = match.team_a.tournament

    if match_tournament != tournament:
        return render(request, 'score_match.html', {
            'match': match,
            'tournament_slug': tournament_slug,
            'back_url': reverse('direct_elimination', args=[tournament_slug]),
            'set_numbers': [],
            'score_fields': {},
        })

    user = request.user
    authorized = user.is_superuser

    if not authorized:
        if hasattr(user, 'organisateur') and (
            (match.pool and match.pool.tournament.organizer == user.organisateur) or
            (not match.pool and match.team_a.tournament.organizer == user.organisateur)
        ):
            authorized = True
        else:
            try:
                user_profile = user.userprofile
                user_team = user_profile.team
                if user_team == match.team_a and match.team_a.captain == user_profile:
                    authorized = True
                elif user_team == match.team_b and match.team_b.captain == user_profile:
                    authorized = True
            except:
                pass

    if not authorized and from_param != 'phase_finale':
        return render(request, 'no_team.html', {
            'error': "Vous n’avez pas le droit de modifier ce match.",
            'from_param': from_param,
            'tournament_id': tournament.id,
            'pool_id': match.pool.id if match.pool else None,
            'tournament_slug': tournament_slug,
        })

    tournament = match.pool.tournament if match.pool else match.team_a.tournament
    nb_sets_display = min(2 * tournament.nb_sets_to_win - 1, 5)
    set_numbers = list(range(1, nb_sets_display + 1))

    score_fields = {
        f'set{n}_team_a': getattr(match, f'set{n}_team_a') for n in set_numbers
    }
    score_fields.update({
        f'set{n}_team_b': getattr(match, f'set{n}_team_b') for n in set_numbers
    })

    # 🔄 Préparer back_url AVANT le POST
    if match.phase == 'pool' and match.pool:
        back_url = reverse('detail_poule', args=[tournament_slug, match.pool.id])
    else:
        back_url = reverse('direct_elimination', args=[tournament_slug])  # 🔥 correction

    # 🔄 Préparer back_url AVANT le POST
    if match.phase == 'pool' and match.pool:
        back_url = reverse('detail_poule', args=[tournament_slug, match.pool.id])
    elif from_param == 'phase_finale':
        back_url = reverse('liste_matchs_phase_finale', args=[tournament_slug]) + f'?tournament_id={tournament.id}'
    else:
        back_url = reverse('direct_elimination', args=[tournament_slug])

    # ✅ Traitement du POST
    if request.method == 'POST':
        for n in set_numbers:
            a_field = f'set{n}_team_a'
            b_field = f'set{n}_team_b'
            a_val = request.POST.get(a_field, '')
            b_val = request.POST.get(b_field, '')
            setattr(match, a_field, int(a_val) if a_val.isdigit() else 0)
            setattr(match, b_field, int(b_val) if b_val.isdigit() else 0)

        winner = match.get_auto_winner(tournament.nb_sets_to_win)
        match.winner_side = 'A' if winner == match.team_a else 'B' if winner == match.team_b else None

        if winner:
            match.statut = 'T'
        elif any(getattr(match, f'set{i}_team_a') or getattr(match, f'set{i}_team_b') for i in set_numbers):
            match.statut = 'EC'
        else:
            match.statut = 'ND'

        match.save()

        if match.phase == 'pool' and match.pool:
            match.pool.calculate_rankings()
        else:
            advance_elimination_bracket(match)
            if match.phase == 'semi':
                update_third_place_match(tournament)

        if match.phase == 'pool' and match.pool:
            return redirect('detail_poule', tournament_slug=tournament_slug, pool_id=match.pool.id)
        elif from_param == 'phase_finale':
            url = reverse('liste_matchs_phase_finale', args=[tournament_slug])
            return HttpResponseRedirect(f"{url}?tournament_id={tournament.id}")
        else:
            return redirect('direct_elimination', tournament_slug=tournament_slug)

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

from django.shortcuts import render, get_object_or_404, redirect
from .models import Pool, Ranking, Tournament, Match

from django.shortcuts import render, get_object_or_404, redirect
from .models import Pool, Ranking, Tournament, Match

def afficher_deux_premiers(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)

    matchs_existent = Match.objects.filter(
        tournament=tournament, phase__in=['eighth', 'quarter', 'semi']
    ).exists()

    pools = Pool.objects.filter(tournament=tournament)
    data = []
    qualified_teams = []

    for pool in pools:
        pool.calculate_rankings()
        rankings = Ranking.objects.filter(team__pool=pool).order_by('rank')[:2]
        data.append({'pool': pool, 'rankings': rankings})
        qualified_teams.extend([ranking.team for ranking in rankings])

    total_teams = len(qualified_teams)
    nb_pools = len(pools)
    is_three_pool_scenario = (nb_pools == 3 and total_teams == 6)

    match_range_eighth = []
    match_range_quarter = []
    match_range_semi = []

    teams_for_eighth = []
    teams_for_quarter = []
    teams_for_semi = []

    # Nouveau flag ajouté ici
    show_quarters = False

    if is_three_pool_scenario:
        match_range_quarter = range(2)
        match_range_semi = range(1)
        teams_for_quarter = qualified_teams
        teams_for_semi = qualified_teams
        show_quarters = True

    elif total_teams == 4:
        match_range_semi = range(2)
        teams_for_semi = qualified_teams

    elif total_teams == 8:
        match_range_quarter = range(4)
        teams_for_quarter = qualified_teams
        show_quarters = True

    else:
        nb_teams_needed_in_quarter = 8
        nb_eighth_matches = max(0, total_teams - nb_teams_needed_in_quarter)
        nb_teams_in_eighth = nb_eighth_matches * 2
        teams_for_eighth = qualified_teams[:nb_teams_in_eighth]
        teams_for_quarter = qualified_teams[nb_teams_in_eighth:]
        match_range_eighth = range(nb_eighth_matches)
        match_range_quarter = range(len(teams_for_quarter) // 2)
        show_quarters = len(match_range_quarter) > 0

    if request.method == 'POST' and not matchs_existent:
        created_match_ids = []

        if is_three_pool_scenario:
            for i in range(2):
                team_a_id = request.POST.get(f'quarter_team_a_{i}')
                team_b_id = request.POST.get(f'quarter_team_b_{i}')
                if team_a_id and team_b_id and team_a_id != team_b_id:
                    match = Match.objects.create(
                        team_a_id=team_a_id,
                        team_b_id=team_b_id,
                        tournament=tournament,
                        phase='quarter',
                        statut='ND',
                        bracket_position=i
                    )
                    created_match_ids.append(match.id)

            team_a_id = request.POST.get('semi_team_a_0')
            team_b_id = request.POST.get('semi_team_b_0')
            if team_a_id and team_b_id and team_a_id != team_b_id:
                match = Match.objects.create(
                    team_a_id=team_a_id,
                    team_b_id=team_b_id,
                    tournament=tournament,
                    phase='semi',
                    statut='ND',
                    bracket_position=0
                )
                created_match_ids.append(match.id)

            request.session['created_match_ids'] = created_match_ids
            return redirect('matchs_choice', tournament_slug=tournament.slug)

        # Huitièmes
        for i in match_range_eighth:
            team_a_id = request.POST.get(f'eighth_team_a_{i}')
            team_b_id = request.POST.get(f'eighth_team_b_{i}')
            if team_a_id and team_b_id and team_a_id != team_b_id:
                match = Match.objects.create(
                    team_a_id=team_a_id,
                    team_b_id=team_b_id,
                    tournament=tournament,
                    phase='eighth',
                    statut='ND',
                    bracket_position=i
                )
                created_match_ids.append(match.id)

        # Quarts
        for i in match_range_quarter:
            team_a_id = request.POST.get(f'quarter_team_a_{i}')
            team_b_id = request.POST.get(f'quarter_team_b_{i}')
            if team_a_id and team_b_id and team_a_id != team_b_id:
                match = Match.objects.create(
                    team_a_id=team_a_id,
                    team_b_id=team_b_id,
                    tournament=tournament,
                    phase='quarter',
                    statut='ND',
                    bracket_position=i
                )
                created_match_ids.append(match.id)

        # Demis
        for i in match_range_semi:
            team_a_id = request.POST.get(f'semi_team_a_{i}')
            team_b_id = request.POST.get(f'semi_team_b_{i}')
            if team_a_id and team_b_id and team_a_id != team_b_id:
                match = Match.objects.create(
                    team_a_id=team_a_id,
                    team_b_id=team_b_id,
                    tournament=tournament,
                    phase='semi',
                    statut='ND',
                    bracket_position=i
                )
                created_match_ids.append(match.id)

        request.session['created_match_ids'] = created_match_ids
        return redirect('matchs_choice', tournament_slug=tournament.slug)

    return render(request, 'matchs_finale.html', {
        'data': data,
        'tournament': tournament,
        'qualified_teams': qualified_teams,
        'teams_for_eighth': teams_for_eighth,
        'teams_for_quarter': teams_for_quarter,
        'teams_for_semi': teams_for_semi,
        'match_range_eighth': match_range_eighth,
        'match_range_quarter': match_range_quarter,
        'match_range_semi': match_range_semi,
        'matchs_existent': matchs_existent,
        'is_three_pool_scenario': is_three_pool_scenario,
        'show_quarters': show_quarters,  # ✅ ajouté ici pour le HTML
    })




from django.shortcuts import render
from .models import Match

from django.shortcuts import render
from .models import Match

from django.shortcuts import render, get_object_or_404
from .models import Match, Tournament

def liste_matchs_phase_finale(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)

    phase_order = ['eighth', 'quarter', 'semi', 'final', 'third_place']
    phase_labels = {
        'eighth': "Huitièmes de finale",
        'quarter': "Quarts de finale",
        'semi': "Demi-finales",
        'final': "Finale",
        'third_place': "Petite finale"
    }

    match_groups = []

    # Récupération des matchs pour chaque phase
    phase_to_matches = {
        phase: list(Match.objects.filter(
            tournament=tournament,
            phase=phase
        ).order_by('bracket_position', 'id'))
        for phase in phase_order
    }

    # Trouver la première phase ayant des matchs
    first_phase = next((p for p in phase_order if phase_to_matches[p]), None)

    if not first_phase:
        return render(request, 'liste_matchs_phase_finale.html', {
            'match_groups': [],
            'message': "Aucun match de phase finale pour ce tournoi."
        })

    # Cas spécial : phase quarter utilisée pour 5, 6, 7 équipes avec des huitièmes "visuels"
    if first_phase == 'quarter':
        quarter_matches = phase_to_matches['quarter']
        total = len(quarter_matches)

        if 5 <= total <= 7:
            num_eighth = (total - 4) * 2  # 5 → 2, 6 → 4, 7 → 6
            huitiemes = quarter_matches[:num_eighth]
            quarts = quarter_matches[num_eighth:]

            if huitiemes:
                match_groups.append({
                    'label': phase_labels['eighth'],
                    'matchs': huitiemes
                })

            if quarts:
                match_groups.append({
                    'label': phase_labels['quarter'],
                    'matchs': quarts
                })
        else:
            match_groups.append({
                'label': phase_labels['quarter'],
                'matchs': quarter_matches
            })

        for phase in phase_order[phase_order.index('semi'):]:
            if phase_to_matches[phase]:
                match_groups.append({
                    'label': phase_labels[phase],
                    'matchs': phase_to_matches[phase]
                })
    else:
        for phase in phase_order[phase_order.index(first_phase):]:
            if phase_to_matches[phase]:
                match_groups.append({
                    'label': phase_labels[phase],
                    'matchs': phase_to_matches[phase]
                })

    return render(request, 'liste_matchs_phase_finale.html', {
        'match_groups': match_groups,
        'message': "Matchs de phase finale pour ce tournoi.",
        'tournament': tournament,  # ✅ celui-là est ESSENTIEL
})



# Coordonées simplifiées pour démonstration
DEPARTMENT_COORDS = {
    '75': {'x': 300, 'y': 200},
    '33': {'x': 150, 'y': 400},
    '69': {'x': 350, 'y': 350},
    '13': {'x': 400, 'y': 500},
    '59': {'x': 250, 'y': 100},
    # Tu ajoutes ici les départements que tu veux
}

def france_map_view(request):
    tournaments_by_dep = Tournament.objects.values('department').annotate(tournament_count=Count('id'))

    departments_with_tournaments = []
    for item in tournaments_by_dep:
        dep_code = item['department']
        if dep_code in DEPARTMENT_COORDS:
            departments_with_tournaments.append({
                'department': dep_code,
                'tournament_count': item['tournament_count'],
                'coord_x': DEPARTMENT_COORDS[dep_code]['x'],
                'coord_y': DEPARTMENT_COORDS[dep_code]['y'],
            })

    return render(request, 'france_map.html', {
        'departments_with_tournaments': departments_with_tournaments
    })

def tournaments_by_department(request, department):
    tournois = Tournament.objects.filter(department=department)
    return render(request, 'tournament_list.html', {
        'tournois': tournois,
        'selected_department': department,
    })


from django.db.models import Count
from django.shortcuts import render
from .models import Tournament

DEPARTMENT_COORDS = {
    '01': {'lat': 46.25, 'lon': 5.65},
    '02': {'lat': 49.50, 'lon': 3.40},
    '03': {'lat': 46.33, 'lon': 3.00},
    '04': {'lat': 44.00, 'lon': 6.25},
    '05': {'lat': 44.75, 'lon': 6.35},
    '06': {'lat': 43.85, 'lon': 7.10},
    '07': {'lat': 44.75, 'lon': 4.50},
    '08': {'lat': 49.75, 'lon': 4.75},
    '09': {'lat': 42.88, 'lon': 1.63},
    '10': {'lat': 48.30, 'lon': 4.05},
    '11': {'lat': 43.10, 'lon': 2.35},
    '12': {'lat': 44.40, 'lon': 2.60},
    '13': {'lat': 43.40, 'lon': 5.40},
    '14': {'lat': 49.00, 'lon': -0.40},
    '15': {'lat': 45.05, 'lon': 2.70},
    '16': {'lat': 45.65, 'lon': 0.25},
    '17': {'lat': 45.95, 'lon': -0.75},
    '18': {'lat': 47.00, 'lon': 2.45},
    '19': {'lat': 45.40, 'lon': 1.75},
    '21': {'lat': 47.30, 'lon': 4.95},
    '22': {'lat': 48.45, 'lon': -2.85},
    '23': {'lat': 46.05, 'lon': 2.05},
    '24': {'lat': 45.15, 'lon': 0.85},
    '25': {'lat': 47.10, 'lon': 6.15},
    '26': {'lat': 44.75, 'lon': 5.15},
    '27': {'lat': 49.10, 'lon': 1.10},
    '28': {'lat': 48.45, 'lon': 1.35},
    '29': {'lat': 48.20, 'lon': -4.10},
    '2A': {'lat': 41.95, 'lon': 8.75},
    '2B': {'lat': 42.50, 'lon': 9.35},
    '30': {'lat': 43.90, 'lon': 4.40},
    '31': {'lat': 43.40, 'lon': 1.50},
    '32': {'lat': 43.65, 'lon': 0.60},
    '33': {'lat': 44.85, 'lon': -0.60},
    '34': {'lat': 43.65, 'lon': 3.40},
    '35': {'lat': 48.15, 'lon': -1.65},
    '36': {'lat': 46.80, 'lon': 1.65},
    '37': {'lat': 47.30, 'lon': 0.65},
    '38': {'lat': 45.25, 'lon': 5.75},
    '39': {'lat': 46.75, 'lon': 5.75},
    '40': {'lat': 44.00, 'lon': -0.85},
    '41': {'lat': 47.65, 'lon': 1.35},
    '42': {'lat': 45.60, 'lon': 4.15},
    '43': {'lat': 45.05, 'lon': 3.85},
    '44': {'lat': 47.30, 'lon': -1.55},
    '45': {'lat': 47.95, 'lon': 2.05},
    '46': {'lat': 44.65, 'lon': 1.65},
    '47': {'lat': 44.35, 'lon': 0.40},
    '48': {'lat': 44.50, 'lon': 3.50},
    '49': {'lat': 47.35, 'lon': -0.55},
    '50': {'lat': 49.15, 'lon': -1.40},
    '51': {'lat': 49.05, 'lon': 4.25},
    '52': {'lat': 48.05, 'lon': 5.15},
    '53': {'lat': 48.10, 'lon': -0.65},
    '54': {'lat': 48.85, 'lon': 6.20},
    '55': {'lat': 49.05, 'lon': 5.35},
    '56': {'lat': 47.90, 'lon': -2.95},
    '57': {'lat': 49.00, 'lon': 6.70},
    '58': {'lat': 47.00, 'lon': 3.45},
    '59': {'lat': 50.50, 'lon': 3.10},
    '60': {'lat': 49.40, 'lon': 2.45},
    '61': {'lat': 48.50, 'lon': 0.55},
    '62': {'lat': 50.50, 'lon': 2.50},
    '63': {'lat': 45.75, 'lon': 3.10},
    '64': {'lat': 43.25, 'lon': -0.35},
    '65': {'lat': 43.05, 'lon': 0.10},
    '66': {'lat': 42.65, 'lon': 2.75},
    '67': {'lat': 48.55, 'lon': 7.50},
    '68': {'lat': 47.80, 'lon': 7.25},
    '69': {'lat': 45.75, 'lon': 4.85},
    '70': {'lat': 47.65, 'lon': 6.15},
    '71': {'lat': 46.75, 'lon': 4.65},
    '72': {'lat': 48.00, 'lon': 0.25},
    '73': {'lat': 45.50, 'lon': 6.35},
    '74': {'lat': 46.05, 'lon': 6.35},
    '75': {'lat': 48.8566, 'lon': 2.3522},
    '76': {'lat': 49.55, 'lon': 0.95},
    '77': {'lat': 48.65, 'lon': 2.85},
    '78': {'lat': 48.80, 'lon': 1.95},
    '79': {'lat': 46.45, 'lon': -0.35},
    '80': {'lat': 49.95, 'lon': 2.30},
    '81': {'lat': 43.85, 'lon': 2.15},
    '82': {'lat': 44.05, 'lon': 1.35},
    '83': {'lat': 43.30, 'lon': 6.60},
    '84': {'lat': 44.05, 'lon': 4.85},
    '85': {'lat': 46.65, 'lon': -1.15},
    '86': {'lat': 46.65, 'lon': 0.40},
    '87': {'lat': 45.85, 'lon': 1.25},
    '88': {'lat': 48.15, 'lon': 6.65},
    '89': {'lat': 47.80, 'lon': 3.60},
    '90': {'lat': 47.65, 'lon': 6.85},
    '91': {'lat': 48.55, 'lon': 2.25},
    '92': {'lat': 48.90, 'lon': 2.25},
    '93': {'lat': 48.90, 'lon': 2.45},
    '94': {'lat': 48.80, 'lon': 2.45},
    '95': {'lat': 49.05, 'lon': 2.25},
}


def france_map_view(request):
    tournaments_by_dep = Tournament.objects.values('department').annotate(tournament_count=Count('id'))

    departments_with_tournaments = []
    for item in tournaments_by_dep:
        dep_code = item['department']
        if dep_code in DEPARTMENT_COORDS:
            departments_with_tournaments.append({
                'department': dep_code,
                'tournament_count': item['tournament_count'],
                'lat': DEPARTMENT_COORDS[dep_code]['lat'],
                'lon': DEPARTMENT_COORDS[dep_code]['lon'],
            })

    return render(request, 'france_map.html', {
        'departments_with_tournaments': departments_with_tournaments
    })
 
from itertools import combinations

def generate_balanced_schedule(teams):
    matchs = list(combinations(teams, 2))
    schedule = []
    
    while matchs:
        for i, match in enumerate(matchs):
            team_a, team_b = match
            if not schedule or (team_a not in schedule[-1] and team_b not in schedule[-1]):
                schedule.append(match)
                matchs.pop(i)
                break
        else:
            schedule.append(matchs.pop(0))  # si pas possible, on prend le premier match

    return schedule
 
