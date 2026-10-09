from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking

User = get_user_model()


class Command(BaseCommand):
    help = 'Наполняет базу демо-данными, вызывая сидеры всех приложений по порядку.'

    def add_arguments(self, parser):
        # Необязательный флаг: python manage.py seed --flush
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Удалить существующие демо-данные перед заполнением.',
        )

    def handle(self, *args, **options):
        if options['flush']:
            self.stdout.write(self.style.WARNING('Очищаю демо-данные...'))
            # Порядок удаления обратный порядку создания (сначала зависимые).
            Booking.objects.all().delete()
            Room.objects.all().delete()
            Hotel.objects.all().delete()
            # Пользователей-демо удаляем, суперпользователей не трогаем.
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.MIGRATE_HEADING('Запуск сидеров по приложениям:'))

        # Пробрасываем текущий уровень детализации в под-команды: при запуске
        # из тестов (verbosity=0) сидеры молчат и не засоряют вывод тестов.
        v = options.get('verbosity', 1)

        # Вызываем per-app команды в порядке зависимостей.
        # call_command запускает другую management-команду программно.
        call_command('seed_users', verbosity=v)
        call_command('seed_hotels', verbosity=v)
        call_command('seed_rooms', verbosity=v)
        call_command('seed_bookings', verbosity=v)

        self.stdout.write(self.style.SUCCESS('\nГотово! База наполнена демо-данными.'))
        self.stdout.write(
            'Демо-доступы:  guest / guestpass123   ·   admin / admin12345'
        )
