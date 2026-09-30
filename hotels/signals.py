from django.db.models.signals import post_delete
from django.dispatch import receiver

from hotels.models import Hotel


@receiver(post_delete, sender=Hotel)
def delete_cover(sender, instance, **kwargs):
    if instance.cover:
        instance.cover.delete(save=False)
        