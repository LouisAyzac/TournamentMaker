from django import template

register = template.Library()

@register.filter
def get_set_score(match, set_info):
    """
    Récupère le score d'un match pour un set et une équipe.
    Exemple : {{ match|get_set_score:"1_team_a" }}
    """
    try:
        set_number, team = set_info.split('_')
        field_name = f"set{set_number}_{team}"
        return getattr(match, field_name, 0)
    except (ValueError, AttributeError):
        return 0
