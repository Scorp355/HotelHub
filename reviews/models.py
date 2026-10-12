from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='reviews',
                              verbose_name='Отель')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews',
                             verbose_name='Автор')
    rating = models.PositiveSmallIntegerField(verbose_name='Оценка', validators=[MinValueValidator(1),
                                                                                 MaxValueValidator(5)])
    text = models.TextField(verbose_name='Текст отзыва')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name='review_rating_between_1_and_5'
            ),
            models.UniqueConstraint(
                fields=['hotel', 'user'],
                name='unique_review_per_hotel_user'
            )
        ]

    def __str__(self):
        return f'{self.hotel.name} - {self.user} {self.rating}/5'