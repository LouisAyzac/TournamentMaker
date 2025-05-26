from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [


    path('', views.home, name='home'), 
                  # 👉 Nouvelle page d'accueil
    path('tournoi/', views.index, name='index'),  # 👉 Page tournoi (anciennement à la racine)
    path('players/', views.players, name='players'),  
    path('teams/', views.teams, name='teams'),  
    path('scores/', views.scores, name='scores'),  

    path('players/<int:pk>/', views.player_detail, name='player_detail'),  
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
    path('pools/', views.pool_list, name='pool_list'),
    path('pools/<int:pk>/', views.pool_detail, name='pool_detail'),
    path('rankings/', views.rankings_list, name='rankings_list'),
    path('select_tournament/', views.select_tournament, name='select_tournament'),
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

]

