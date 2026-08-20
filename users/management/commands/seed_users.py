
# Идемпотентность - данные заполняются только при певом запуске - не создаются дубли данных

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()

# Список демо-гостей: (логин, email, телефон, пароль)
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
        # Создание обычных пользователей
        for username, email, phone, password in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'phone': phone}
                )
            # Проверяем, был ли пользователь только что создан
            if created:
                user.set_password(password)
                user.save()
                say(f'  +{user} / {password}')    # В degug режиме
                # say(f'+{username}') # Для продакшн
            else:
                say(f'  - {username} уже существует')

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
            say('  + admin / admin12345')
        else:
            say('  - admin уже существует')

        say(self.style.SUCCESS(f'Готово. Пользователей в базе: {User.objects.count()}'))

                