from django import forms
from .models import TournamentPhoto

class TournamentPhotoForm(forms.ModelForm):
    class Meta:
        model = TournamentPhoto
        fields = ['title', 'image', 'tournament']
