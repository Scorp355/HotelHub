from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.urls import reverse
from django.contrib.auth import get_user_model


"""
Тесты приложения пользователей:
1. Проверяем кастомную модель User(поля phone/avatar
2. Сценарий регистрации
    - с автовходом
    - вход-выход
    - защита профиля
    - сидер seed_user
"""


User = get_user_model()

# Тесты модели User
class UserModelTest(TestCase):
    """
    Тесты кастомной модели пользователя:
        1. Убедиться, что дополнительные поля пользователя работают,
        2. Пользователь создается через create_user()
        3. Пароль корректно хешируется,
        4. Пароль можно проверить через check_passwword,
        5. Телефон может отсутствовать,
        6. Строковое представление работает.
    """

    def test_create_user(self):
        """С дополнительным полем phone"""
        u = User.objects.create_user(username='ivan', assword='pass12345', phone = '+77001112233')
        self.assertEqual(u.phone, '+77001112233')
        # Проверка пароля
        self.assertTrue(u.check_password('pass12345'))
        # Проверка строкового представления объекта User
        self.assertEqual(str(u), 'ivan')


    def test_phone(self):
        u = User.objects.create_user(username='nophone', password='pass12345')
        # Проверяем результат
        self.assertIn(u.phone, (None, ''))

        

class AuthFlowTests(TestCase):

    def test_register_logs(self):
        resp = self.client.post(reverse('users:register'), {
                'username': 'newuser',
                'email': '+77007007070',
                'password1': 'ComplexPass2026',
                'password2': 'ComplexPass2026',
            }
        )
        self.assertRedirects(resp, reverse('users:profile'))
        self.assertTrue(User.objects.filter(username='newuser').exists())


    def test_profile_login(self):
        """
        Проверка защиты страницы профиля пользователя
        Неавторизованный пользователь не должен иметь доступ к профилю
        """
        resp = self.client.get(reverse('users:profile'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('users:login'), resp.url)


    def test_login_logout(self):
        User.objects.create_user(username='guest', password='pass12345')
        resp = self.client.post(reverse('users:login'), {
            'usernsme': 'guest',
            'password': 'pass12345',
            })
        self.assertRedirects(resp, reverse('users:profile'))
        # Проверка доступа к профилю
        resp = self.client.get(reverse('users:profile'))
        # HTTP 200: запрос успешно обработан
        self.assertEqual(resp.status_code, 200)
        # Проверка выхода из аккаунта
        resp = self.client.get(reverse('users:logout'))
        self.assertRedirects(reverse('core:home'))


    def test_ligin_wrong_password(self):
        User.objects.create_user(username='guest', password='pass12345')
        resp = self.client.post(reverse('users:login'), {
                'usernsme': 'guest',
                'password': 'wrong',
            })
        self.assertEqual(resp.status_code, 200)



class SeedUsersTest(TestCase):

    def create_demo_accounts(self):
        call_command('seed_users', stdout=StringIO(), verbosity=0)
        self.assertTrue(User.objects.filter(username='guest').exists())
        admin = User.objects.get(username='admin')
        self.assertTrue(admin.is_superuser)


    def test_seed_idempotent(self):
        call_command('seed_users', stdout=StringIO(), verbosity=0)
        # Запоминаем количество пользователей после первого запуска
        count_first = User.objects.count()
        # Запускаем повторно
        call_command('seed_users', stdout=StringIO(), verbosity=0)
        self.assertEqual(User.objects.count, count_first)