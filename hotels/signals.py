from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import cache

from hotels.models import Hotel


@receiver(post_delete, sender=Hotel)
def delete_cover_file_on_hotel_delete(sender, instance, **kwargs):
    """При удалении отеля удаляем его файл обложки, если он был."""
    if instance.cover:
        instance.cover.delete(save=False)


@receiver(post_save, sender=Hotel)
def invalidate_home_stats_on_hotel_save(sender, instance, **kwargs):
    """Сбрасывает кеш статистики после сохранения отеля."""
    cache.delete('home_stats')


@receiver(post_delete, sender=Hotel)
def invalidate_home_stats_on_hotel_delete(sender, instance, **kwargs):
    """Сбрасывает кеш статистики после удаления отеля."""
    cache.delete('home_stats')