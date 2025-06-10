from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import TournamentListView 
from TournamentMaker.views import TournamentDetailView

urlpatterns = [


    path('', views.home, name='home'), 
    #  Nouvelle page d'accueil
    path('tournoi/', views.index, name='index'),  #  Page tournoi (anciennement à la racine)
    path('players/', views.players, name='players'),  
    path('teams/', views.teams, name='teams'),  
    path('scores/', views.scores, name='scores'),  
    

    path('players/<int:pk>/', views.player_detail, name='player_detail'),  
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('pools/', views.pool_list, name='pool_list'),
    path('pools/<int:pk>/', views.pool_detail, name='pool_detail'),
    path('rankings/', views.rankings_list, name='rankings_list'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('signup/success/', views.signup_success, name='signup_success'),
    path('matchs-en-cours/', views.matchs_en_cours, name='matchs_en_cours'),
    
    

    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),


    path('creer_tournoi/', views.create_tournament, name='create_tournament'),


    

       # 🆕 Vue d’aiguillage
    path('matchs/', views.match_choice, name='matchs'),

    # 🆕 Matchs de poules et détails
    path('matchs/poule/<int:pool_id>/', views.detail_poule, name='detail_poule'),
    path('tournoi/<int:tournament_id>/poules/', views.matchs_poules, name='matchs_poules'),

    # 🆕 Phase finale
    path('matchs/finale/', views.matchs_finale, name='matchs_finale'),


    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('tournaments/', TournamentListView.as_view(), name='tournament_list'),
    path('tournament/<int:pk>/', TournamentDetailView.as_view(), name='tournament_detail'),
        path('tournament/full/', views.tournament_full, name='tournament_full'),



]