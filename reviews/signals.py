from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from . models import Review


def invalidate_hotel_rating(hotel_id):
    if hotel_id is not None:
        cache.delete(f'hotel:{hotel_id}:avg_rating')


@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    invalidate_hotel_rating(instance.hotel_id)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    invalidate_hotel_rating(instance.hotel_id)