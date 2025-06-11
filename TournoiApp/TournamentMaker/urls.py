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
    path('players/', views.players, name='players'),
    path('players/<int:pk>/', views.player_detail, name='player_detail'),
    path('teams/', views.teams, name='teams'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),

    # Scores & matchs
    path('scores/', views.scores, name='scores'),
    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('match/<int:match_id>/score/', views.score_match, name='score_match'),
    path('create_elimination_match/', views.create_elimination_match, name='create_elimination_match'),

    # Matchs (choix, poules, finale)
    path('matchs/', views.match_choice, name='matchs_choice'),
    path('matchs/poule/<int:pool_id>/', views.detail_poule, name='detail_poule'),
    path('tournoi/<int:tournament_id>/poules/', views.matchs_poules, name='matchs_poules'),
    path('matchs/finale/', views.matchs_finale, name='matchs_finale'),
    path('matchs-en-cours/', views.matchs_en_cours, name='matchs_en_cours'),

    # Pools et classements
    path('pools/', views.pool_list, name='pool_list'),
    path('pools/<int:pk>/', views.pool_detail, name='pool_detail'),
    path('rankings/', views.rankings_list, name='rankings_list'),

    # Tournois
    path('creer_tournoi/', views.create_tournament, name='create_tournament'),
    path('tournaments/', TournamentListView.as_view(), name='tournament_list'),
    path('tournament/<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
    path('tournament/full/', views.tournament_full, name='tournament_full'),

    # Élimination directe
    path('direct-elimination/', views.direct_elimination, name='direct_elimination'),

    # Divers
    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('match/<int:match_id>/score/', views.score_match, name='score_match'),
    path('select_tournament/', views.home, name='select_tournament'),
    path('tournois/', views.home, name='home'),


]
