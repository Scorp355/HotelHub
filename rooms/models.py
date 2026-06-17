from django.db import models
from hotels.models import Hotel


class Room(models.Model):
    
    # Список допустимых типов номера
    ROOM_TYPES = [
            ('single', 'Одноместный'),
            ('double', 'Двухместный'),
            ('suite', 'Люкс'),
            ('family', 'Семейный'),
        ]
    
    # Связь "M:1" (многие к одному)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    # номер комнаты как строка (может быть '101' или '101A')
    number = models.CharField(max_length=20)
    # Тип номера
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='single')
    # Описание
    description = models.TextField(blank=True, null=True)
    # Цена за ночь
    price_night = models.DecimalField(max_digits=10, decimal_places=2)
    # Вместимость
    capacity = models.PositiveIntegerField(default=1)
    # Доступен ли номер
    is_available = models.BooleanField(default=True)
    # дата создания записи
    created_at = models.DateTimeField(auto_now_add=True)


    # Вложенный класс с настройками модели
    class Meta:
        verbose_name = 'Номер'  # в единственном числе
        verbose_name_plural = 'Номера' # в множественном числе
        ordering = ['-created_at']  # сортировка по дате создания записи
    

    def __str__(self):
        return f'{self.hotel.name} — номер {self.number}'
    
