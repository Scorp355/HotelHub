from django.db import models
from django.conf import settings
from rooms.models import Room


class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),        
        ('confirmed', 'Подтверждено'),        
        ('cancelled', 'Отменено'),        
    ]    

    # Кто забронировал: settings 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings', verbose_name='Гость')
    # Номер
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name='Номер')
    # Дата заезда и выезда
    check_in = models.DateField('Дата заезда')
    check_out = models.DateField('Дата выезда')
    # Количество гостей
    guests = models.PositiveIntegerField('Количество гостей', default=1)
    # Статус бронирования
    status = models.CharField('Статус', max_length=30, choices=STATUS_CHOICES, default='pending')
    # Дата создания
    created_at = models.DateTimeField('Создано', auto_now_add=True)


    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(condition=models.Q(check_out__gt=models.F('check_in')), name='booking_checkout_after_checkin'),            
            ]
        indexes = [
            models.Index(fields=['user', '-created_at'], name='booking_user_created_at-idx'),       # Составной индекс
            models.Index(fields=['room', 'status']),
            ]


    def __str__(self):
        return f'Бронь №{self.pk} — {self.room} ({self.user})'


    # Вычисляемое поле
    @property    
    def nights(self):
        # Число ночей брони
        return (self.check_out - self.check_in).days


    @property
    # Итоговая стоимость
    def total_price(self):
        nights = self.nights
        if nights < 0:
            nights = 0
        return self.room.price_night * nights
