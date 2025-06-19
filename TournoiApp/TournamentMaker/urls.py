from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import TournamentListView
from TournamentMaker.views import TournamentDetailView

urlpatterns = [
    # Accueil
    path('', views.home_landing, name='home_landing'),
    path('tournoi/', views.index, name='index'),

    # Authentification
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # Joueurs / équipes
    path('<slug:tournament_slug>/players/', views.players, name='players'),
    path('<slug:tournament_slug>/players/<int:pk>/', views.player_detail, name='player_detail'),
    path('<slug:tournament_slug>/teams/', views.teams, name='teams'),
    
    path('<slug:tournament_slug>/<int:pk>/', views.team_detail, name='team_detail'),

    # Scores & matchs
    path('scores/', views.scores, name='scores'),
    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('<slug:tournament_slug>/match/<int:match_id>/score/', views.score_match, name='score_match'),
    path('create_elimination_match/', views.create_elimination_match, name='create_elimination_match'),

    # Matchs (choix, poules, finale)
    path('<slug:tournament_slug>/matchs/', views.match_choice, name='matchs_choice'),
    path('<slug:tournament_slug>/matchs/poule/<int:pool_id>/', views.detail_poule, name='detail_poule'),
    path('<slug:tournament_slug>/poules/', views.matchs_poules, name='matchs_poules'),
    path('<slug:tournament_slug>/matchs-finale/', views.afficher_deux_premiers, name='matchs_finale'),
    path('<slug:tournament_slug>/matchs-finale/liste/', views.liste_matchs_phase_finale, name='liste_matchs_phase_finale'), # ← ajout ici
    path('matchs-en-cours/', views.matchs_en_cours, name='matchs_en_cours'),
    path('<slug:tournament_slug>/match/<int:match_id>/score/', views.score_match, name='score_match'),

    

    # Pools et classements
    path('pools/', views.pool_list, name='pool_list'),
    path('pools/<int:pk>/', views.pool_detail, name='pool_detail'),
    path('rankings/', views.rankings_list, name='rankings_list'),

    # Tournois
    path('creer_tournoi/etape1/', views.create_tournament_step1, name='create_tournament_step1'),
    path('creer_tournoi/etape2/', views.create_tournament_step2, name='create_tournament_step2'),
    path('<slug:tournament_slug>/ranking/', views.rankings_list, name='rankings_list'),
    path('<slug:slug>/detail', TournamentDetailView.as_view(), name='tournament_detail'),



    path('tournament/full/', views.tournament_full, name='tournament_full'),

    # Élimination directe
    path('<slug:tournament_slug>/direct-elimination/', views.direct_elimination, name='direct_elimination'),

    # Divers
    path('<slug:tournament_slug>/signup/', views.signup, name='signup'),
    path('<slug:tournament_slug>/signup/success/', views.signup_success, name='signup_success'),

    path('<slug:tournament_slug>/dashboard/', views.dashboard, name='dashboard'),
    
    path('<slug:tournament_slug>/match/<int:match_id>/score/', views.score_match, name='score_match'),
    path('select_tournament/', views.home, name='select_tournament'),
    path('tournois/', views.home, name='home'),
    path('carte-france/', views.france_map_view, name='france_map'),

    path('tournament/<slug:tournament_slug>/generate-bracket/', views.generate_elimination_bracket, name='generate_elimination_bracket'),


]
