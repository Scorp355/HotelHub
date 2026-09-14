from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rooms.models import Room
from bookings.models import Booking
from bookings import services


User = get_user_model()


class Command(BaseCommand):
    help = 'Создает демонстрационные бронирования для демо-пользователей'

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 1) >= 1

        def say(msg):
            if verbose:
                self.stdout.write(msg)

        guest = User.objects.filter(username='guest').first()
        rooms = list(Room.objects.all()[:4])

        if guest is None or len(rooms) < 2:
            say(self.style.WARNING(
                    'Нужны пользователь guest и хотя бы 2 номера'
                    'Сначала выполните seed_users и seed_rooms'
                ))
            return

        if Booking.objects.filter(user=guest).exists():
            say('    — У пользователя уже есть брони - пропускаю')
            say(self.style.SUCCESS(
                    f'Всего бронирований: {Booking.objects.count()}'
                ))
            return

        say('Создаю броирования...')

        today = date.today()

        plan = [
                (rooms[0], 3, 3, 2),
                (rooms[1], 14, 2, 1),
            ]

        for room, start_offset, nights, guests in plan:
            check_in = today + timedelta(days=start_offset)
            check_out = check_in + timedelta(days=nights)
            try:
                booking = services.create_booking(room=room, check_in=check_in, check_out=check_out,
                                                  guests=min(guests, room.capacity))
                say(f'  + Бронь №{booking.pk}: {room}'
                f'({check_in} - {check_out}, {booking.nights} ноч.)'
                )
            except ValidationError as exc:
                say(self.style.WARNING(f'   ! Пропущено: {exc.messages[0]}'))
        say(self.style.SUCCESS(f'Готово: Всего бронирований в системе {Booking.objects.count()}'))
