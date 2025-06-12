from django import template

register = template.Library()

@register.filter
def get_set_score(match, set_number):
    """
    Récupère le score d'un set donné pour un match.
    """
    set_team_a = getattr(match, f'set{set_number}_team_a', None)
    set_team_b = getattr(match, f'set{set_number}_team_b', None)
    if set_team_a is not None and set_team_b is not None:
        return f'{set_team_a}-{set_team_b}'
    return 'N/A'
