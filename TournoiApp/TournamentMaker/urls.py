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
    path('pools/', views.pool_list, name='pool_list'),  # liste des pools
    path('pools/<int:pk>/', views.pool_detail, name='pool_detail'),  # détail d'une pool
    path('rankings/', views.rankings_list, name='rankings_list'),
    path('matchs-en-cours/', views.matchs_en_cours, name='matchs_en_cours'),
    

]
