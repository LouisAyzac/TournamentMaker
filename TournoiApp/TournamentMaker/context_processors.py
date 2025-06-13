from datetime import date
from .models import Tournament
from datetime import date

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
def selected_tournament(request):
    selected_id = request.session.get('selected_tournament_id')
    tournoi = None
    if selected_id:
        try:
            tournoi = Tournament.objects.get(id=selected_id)
        except Tournament.DoesNotExist:
            pass
    return {
        'tournoi': tournoi,
        'today': date.today()  # 👈 ajoute cette ligne
    }
