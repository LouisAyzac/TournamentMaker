from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),  # ⬅️ Ceci est essentiel
    path('players/', views.players, name='players'),  
    path('teams/', views.teams, name='teams'),  
    path('scores/', views.scores, name='scores'),  
    path('teams/', views.teams, name='teams'), 
    path('players/<int:pk>/', views.player_detail, name='player_detail'),  
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),
]
