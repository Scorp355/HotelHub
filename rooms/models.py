from django.db import models
from django.core.validators import FileExtensionValidator
from core.validators import ALLOVED_IMAGE_EXTENSIONS, validate_images_size
from hotels.models import Hotel


def room_image_path(instance, filename):
    return f'rooms/images/{instance.pk or 'new'}/{filename}'


class RoomQuerySet(models.QuerySet):
    def free_between(self, check_in, check_out):
        from bookings.services import ACTIVE_STATUSES
        from bookings.models import Booking
        busy_room_ids = Booking.objects.filter(status__in=ACTIVE_STATUSES, check_in__lt=check_out,
                                               check_out__gt=check_in).values_list('room_id', flat=True)
        return self.exclude(pk__in=busy_room_ids)


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

    image = models.ImageField('Фото номера', upload_to=room_image_path, blank=True, null=True,
                              validators=[FileExtensionValidator(ALLOVED_IMAGE_EXTENSIONS)],
                              help_text='JPG/PNG/WEBP, не более 5 МБ')

    objects = RoomQuerySet.as_manager()

    # Вложенный класс с настройками модели
    class Meta:
        verbose_name = 'Номер'  # в единственном числе
        verbose_name_plural = 'Номера' # в множественном числе
        ordering = ['-created_at']  # сортировка по дате создания записи
        constraints = [models.UniqueConstraint(fields=['hotel', 'number'], name='room_unique_number_hotel')]
        indexes = [models.Index(fields=['is_available', 'room_type'], name='room_is_available_room_type_idx')]

    def __str__(self):
        return f'{self.hotel.name} — номер {self.number}'
    
