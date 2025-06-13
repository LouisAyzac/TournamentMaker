from datetime import date
from .models import Tournament

def hide_inscription_button(request):
    try:
        tournament_id = request.session.get('selected_tournament_id')
        if not tournament_id:
            return {'hide_inscription': False}
        
        tournoi = Tournament.objects.get(id=tournament_id)

        is_full = tournoi.teams.count() >= tournoi.max_teams
        is_over = tournoi.end_date < date.today()

        return {'hide_inscription': is_full or is_over}
    except:
        return {'hide_inscription': False}
