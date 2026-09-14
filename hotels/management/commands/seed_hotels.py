from django.core.management.base import BaseCommand
from hotels.models import Hotel

# name, city, address, price_night, rating, description
HOTELS = [
        ('Grand Astana', 'Астана', 'пр. Кабанбай-батыра, 12', 45000, 4.7, 'Пятизвездочный отель в центре столицы с панорамным видом на Байтерек'),
        ('Almaty Plaza', 'Алматы', 'ул. Достык, 85', 38000, 4.5, 'Современный отель у подножия гор, в шаговой доступности от парков'),
        ('Caspian Resort', 'Актау', 'мкр. 15, дом 4', 52000, 4.8, 'Курортный комплекс на берегу Каспийского моря с собственным пляжем'),
        ('Shymkent City', 'Шымкент', 'пр. Тауке Хана, 21', 27000, 4.2, 'Уютный городской отель для деловых поездок и туризма'),
        ('Turkistan Palace', 'Туркестан', 'ул. Айтеке би, 7', 33000, 4.6, 'Отель, расположенный рядом с мавзолеем Ходжи Ахмеда Ясави, восточный колорит'),
        ('Karaganda Central', 'Караганда', 'пр. Бахар жырау, 40', 24000, 4.0, 'Классический городской отель в деловом центре Караганды'),
    ]


class Command(BaseCommand):
    help = 'Создает демонстрациолнные отели'

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 1) >= 1

        def say(msg):
            if verbose:
                self.stdout.write(msg)

        say('Создаю отель...')
        created_count = 0

        for name, city, address, price_night, rating, desc in HOTELS:
            hotel, created = Hotel.objects.get_or_create(
                    name=name,
                    defaults={
                            'city': city, 'address': address, 'price_night': price_night, 'rating': rating, 'description': desc,
                            'is_active': True
                        },                        
                )
            if created:
                created_count += 1
                say(f'  +{name} ({city})')
        say(self.style.SUCCESS(f'Готово. Создано новых: {created_count}. Всего отелей: {Hotel.objects.count()}'))

