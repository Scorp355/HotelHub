from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from core.validators import ALLOVED_IMAGE_EXTENSIONS, validate_images_size
from django.db import models

def hotel_cover_path(instance, filename):
    return f'hotels/covers/{instance.pk or "new"}/{filename}'


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    # Цена за 1 ноч проживания
    price_night = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField(default=0, validators=[
            MinValueValidator(0), MaxValueValidator(5)
            ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Обложка отеля
    cover = models.ImageField('Обложка', upload_to=hotel_cover_path, blank=True, null=True,
                              validators=[FileExtensionValidator(ALLOVED_IMAGE_EXTENSIONS),
                                          validate_images_size,],
                                help_text='JPG/PNG/WEBP, не более 5 МБ.' )    
    
    class Meta:
        # Название модели в единственном числе
        verbose_name = 'Отель'
        # Название модели во множественном числе
        verbose_name_plural = 'Отели'
        ordering = ['-created_at']
        indexes = [
                models.Index(fields=['city'], name='hotel_city_idx'),
                models.Index(fields=['is_active', '-rating'], name='hotel_active_rating_idx'),
            ]
        constraints = [
                models.CheckConstraint(condition=models.Q(rating__gte=0) & models.Q(rating__lte=5),
                                       name='hotel_rating_between_0_and_5'),                
            ]


    def __str__(self):
        return self.name
