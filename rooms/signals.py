from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from .models import Room


@receiver(post_delete, sender=Room)
def delete_image_file_on_room_delete(sender, instance, **kwargs):
    """При удалении номера удаляем его файл фото, если он был."""
    if instance.image:
        instance.image.delete(save=False)


@receiver(post_save, sender=Room)
def invalidate_home_stats_on_room_save(sender, instance, **kwargs):
    """Сбрасывает кеш статистики после сохранения номера."""
    cache.delete('home_stats')


@receiver(post_delete, sender=Room)
def invalidate_home_stats_on_room_delete(sender, instance, **kwargs):
    """Сбрасывает кеш статистики после удаления номера."""
    cache.delete('home_stats')
