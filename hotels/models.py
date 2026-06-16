from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    # Цена за 1 ноч проживания
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Название модели в единственном числе
        verbose_name = 'Отель'
        # Название модели во множественном числе
        verbose_name_plural = 'Отели'
        ordering = ['-created_at']


    def __str__(self):
        return self.name


