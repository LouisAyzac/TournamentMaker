# TournamentMaker/services/scheduling.py
from itertools import combinations

from TournamentMaker.models import Match


def ensure_pool_matches(pool):
    """
    Crée (en base) toutes les rencontres possibles entre les équipes de `pool`
    qui n'existent pas encore. Chaque nouveau match est mis en phase 'pool',
    statut « non débuté », round 1 par défaut.
    """
    teams = list(pool.teams.all())
    if len(teams) < 2:
        return  # rien à faire

    # couples déjà présents (id mini, id maxi) pour ignorer home/away inversé
    existing = {
        (min(m.team_a_id, m.team_b_id), max(m.team_a_id, m.team_b_id))
        for m in pool.matches.filter(phase=Match.Phase.GROUP)
    }

    new_matches = []
    for t1, t2 in combinations(teams, 2):
        key = (min(t1.id, t2.id), max(t1.id, t2.id))
        if key not in existing:
            new_matches.append(
                Match(
                    pool=pool,
                    team_a=t1,
                    team_b=t2,
                    phase=Match.Phase.GROUP,
                    statut=Match.Status.NOT_STARTED,  # "ND"
                    round=1,
                )
            )

    if new_matches:
        Match.objects.bulk_create(new_matches)
