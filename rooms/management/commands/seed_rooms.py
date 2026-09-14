# Скрипт-наполнитель
from django.core.management.base import BaseCommand

from hotels.models import Hotel
from rooms.models import Room


# Параметры по типам номеров: цена за ночь и вместимость
ROOM_TYPES = ['single', 'double', 'suite', 'family']
BASE_PRICES = {'single': 12000, 'double': 18000, 'suite': 32000, 'family': 26000}
CAPACITY = {'single': 1, 'double': 2, 'suite': 2, 'family': 4}


class Command(BaseCommand):
    help = 'Создает демонстрационные номера всех отелей'

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 1) >=1

        def say(msg):
            if verbose:
                self.stdout.write(msg)

        hotels = list(Hotel.objects.all())
        if not hotels:
            say(self.style.WARNING('Нет ни одного отеля. Сначала выполните: python manage.py seed_hotels'))
            return

        say('Создаю номера...')
        created_count = 0

        for hotel_index, hotel in enumerate(hotels, start=1):
            for i, rtype in enumerate(ROOM_TYPES, start=1):
                number = f'{i}0{hotel_index}'
                created = Room.objects.get_or_create(
                    hotel=hotel,
                    number=number,
                    defaults = {
                        'room_type': rtype,
                        'price_night': BASE_PRICES[rtype],
                        'capacity': CAPACITY[rtype],
                        'is_available': True,
                        'description': f'{dict(Room.ROOM_TYPES)[rtype]} в отеле "{hotel.name}"',
                    },
                )
                if created:
                    created_count += 1
        say(self.style.SUCCESS(f'Готово. Создано новых: {created_count}. Всего номеров {Room.objects.count()}'))
                