from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match


@receiver(post_save, sender=Match)
def update_ranking_after_match(sender, instance, **kwargs):
    update_rankings()
