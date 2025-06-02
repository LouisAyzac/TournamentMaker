from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'department', 'address', 'is_indoor', 'start_date', 'end_date', 'sport']

