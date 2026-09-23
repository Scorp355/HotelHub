from django.core.management.base import BaseCommand
from core.models import PromoOffer, Facility, Review, FAQItem


class Command(BaseCommand):
    help = 'Наполнение БД стартовыми данными для приложения core'

    def handle(self, *args, **kwargs):
        self.stdout.write('Очистка старых данных...')
        PromoOffer.objects.all().delete()
        Facility.objects.all().delete()
        Review.objects.all().delete()
        FAQItem.objects.all().delete()

        self.stdout.write('Создание услуг...')
        Facility.objects.create(name='Premium SPA', short_desc='Ритуалы релаксациии восстановления',
                                icon_class='fa-spa')
        Facility.objects.create(name='Lounge-Bar', short_desc='Авторские коктейли и живой джаз',
                                icon_class='fa-glass-martini-alt')
        Facility.objects.create(name='Fitness Club', short_desc='Современное оборудование Technogym',
                                        icon_class='fa-dumbbell')
        Facility.objects.create(name='Консьерж 24/7', short_desc='Персональное сопровождение вашего отдыха',
                                                icon_class='fa-concierge-bell')

        self.stdout.write('Создание промоакций...')
        PromoOffer.objects.create(
            title = 'Бизнес-ретрит',
            description='Идеальные условия для работы и отдыха. Включен доступ в закрытый лаунж и' \
            ' переговорные комнаты.',
            discount_percent=15
        )
        PromoOffer.objects.create(
                    title = 'Романтический уикенд',
                    description='Поздний выезд, завтрак в номер и комплимент от шеф-повара при бронировании' \
                    ' номеров категории Люкс."',
                    discount_percent=15
                )

        self.stdout.write('Создание отзывов...')
        Review.objects.create(
            author='Александр В.',
            text='Безупречный сервис и потрясающая эстетика минимализма во всем. Лучший отель в городе.',
            ratting = 5
        )
        Review.objects.create(
                    author='Елена М.',
                    text='Отличный SPA комплекс, идеальная чистота и очень вежливый персонал. Обязательно' \
                    ' вернусь.',
                    ratting = 5
                )
        Review.objects.create(
                            author='Михаил Т.',
                            text='text="Понравилась строгая архитектура номеров и качественная шумоизоляция.',
                            ratting = 4
                        )

        self.stdout.write('Создание FAQ...')
        FAQItem.objects.create(
            question='Во сколько заезд и выезд?',
            answer='Стандартное время заезда — 14:00, время выезда — 12:00.',
            order=1
        )
        FAQItem.objects.create(
                    question='question="Можно ли с питомцами?',
                    answer='Да, мы принимаем гостей с собаками мелких пород (до 5 кг)',
                    order=2
                )

        self.stdout.write(self.style.SUCCESS('База данных успешно наполнена стартовыми данными!'))
        