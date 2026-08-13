
# Идемпотентность - данные заполняются только при певом запуске

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

# Список демо-гостей: (логин, emailб телефон, пароль)
DEMO_USERS = [
        ('guest', 'guest@example.com', '+7 700 000 00 00', 'guestpass123'),
        ('aizhan', 'aizhan@example.com', '+7 701 111 22 33', 'aizhan2026'),
        ('danyar', 'danyar@example.com', '+7 702 222 33 44', 'danyar2026'),
        ('marat', 'marat@example.com', '+7 705 333 44 55', 'marat2026'),
    ]

class Command(BaseCommand):

    help = 'Создает демо-пользователей и суперпользователя admin'


    def handle(self, *args, **options):
        verbose = options.get('verbosity', 1) >= 1

        def say(msg):
            if verbose:
                self.stdout.write(msg)

        say('Создаю пользователей...')
        

