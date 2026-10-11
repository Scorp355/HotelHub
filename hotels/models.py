from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, Min, OuterRef, Subquery, Case, When, Value, Q, CharField

from core.validators import ALLOVED_IMAGE_EXTENSIONS, validate_images_size


class HotelQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_stats(self):
        return self.annotate(
            min_price=Min('rooms__price_night'),
            rooms_count=Count('rooms', distinct=True),
            category=Case(
                When(rating__gte=4.5, then=Value('Премиум')),
                default=Value('Стандарт'),
                output_field=CharField(),
                ),
            confirmed_bookings_count=Count(
                'rooms__bookings',
                filter=Q(rooms__bookings__status='confirmed'),
                distinct=True,
                )
            )

    def with_last_booking_date(self):
        """Аннотирует отель датой создания последней брони."""
        from bookings.models import Booking
        
        last_booking = Booking.objects.filter(room__hotel_id=OuterRef('pk')).order_by('-created_at')
        return self.annotate(last_booking_date=Subquery(last_booking.values('created_at')[:1]))


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

    objects = HotelQuerySet.as_manager()
    
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
