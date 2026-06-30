from django.db import models
from rooms.models import Room


class Booking(models.Model):

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтверждена'),
        ('canselled', 'Отменена'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    
    guest_name = models.CharField(max_length=150)
    guest_email = models.CharField(blank=True, max_length=64, unique=True)

    date_of_check_in = models.DateTimeField()
    date_check_out = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Брони'
        ordering = ['-created_at']
    

    def __str__(self):
        return f'Бронь {self.room.number} - {self.guest_name}'



