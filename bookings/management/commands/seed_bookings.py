from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import Room
from bookings.models import Booking
from bookings import services


User = get_user_model()


class Command(BaseCommand):
    help = 'Создает демонстрационные бронирования'

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 1) >= 1
        user = User.objects.filter(username='guest').first()
        rooms = Room.objects.all()[:4]

        def say(msg):
            if verbose:
                self.stdout.write(msg)

        if not user or not rooms:
            say('Ошибка! Гостя или номеров не существует...')
            return
        
