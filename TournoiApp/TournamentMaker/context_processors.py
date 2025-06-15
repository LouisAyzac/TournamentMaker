from TournamentMaker.models import Tournament

def selected_tournament_slug(request):
    selected_id = request.session.get('selected_tournament_id')
    if selected_id:
        try:
            tournoi = Tournament.objects.get(id=selected_id)
            return {'selected_tournament_slug': tournoi.slug}
        except Tournament.DoesNotExist:
            pass
    return {'selected_tournament_slug': None}