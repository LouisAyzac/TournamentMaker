from django.apps import AppConfig


class TournamentmakerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TournamentMaker'

def ready(self):
    import TournamentMaker.signals  # adapte si ton app a un autre nom
