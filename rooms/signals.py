from django.db.models.signals import post_delete
from django.dispatch import receiver

from rooms.models import Room


@receiver(post_delete, sender=Room)
def delete_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)