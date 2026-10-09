from django.db.models.signals import post_delete
from django.dispatch import receiver

from hotels.models import Hotel


@receiver(post_delete, sender=Hotel)
def delete_cover_file_on_hotel_delete(sender, instance, **kwargs):
    """При удалении отеля удаляем его файл обложки, если он был."""
    if instance.cover:
        instance.cover.delete(save=False)