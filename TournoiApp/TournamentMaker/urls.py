from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('equipes/', views.equipes, name='equipes'),
    path('joueurs/', views.joueurs, name='joueurs'),
    path('matchs/', views.matchs, name='matchs'),
    path('ranking/', views.ranking, name='ranking'),

]
