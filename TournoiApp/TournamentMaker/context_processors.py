from .models import Tournament

def selected_tournament(request):
    selected_id = request.session.get('selected_tournament_id')
    tournoi = None
    if selected_id:
        try:
            tournoi = Tournament.objects.get(id=selected_id)
        except Tournament.DoesNotExist:
            pass
    return {
        'tournoi': tournoi
    }
