from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True, null=True)
    avatar = models.ImageField(verbose_name='Аватар', upload_to='users/avatars/', blank=True, null=True)


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


    def __str__(self):
        return self.username