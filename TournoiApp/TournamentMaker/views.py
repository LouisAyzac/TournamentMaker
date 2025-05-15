from django.shortcuts import render

# Create your views here.
from TournamentMaker.models import Player

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_Player = Player.objects.all().count()

    # Available books (status = 'a'

    context = {
        'num_Player': num_Player,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)
