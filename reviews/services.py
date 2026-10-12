from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Avg

from bookings.models import Booking
from hotels.models import Hotel
from .  models import Review


def create_review(user, hotel, rating, text):
    """Создаёт отзыв или обновляет существующий. Отзыв разрешён только
      пользователю, у которого есть подтверждённая бронь с датой выезда в
      прошлом."""
    has_completed_booking = Booking.objects.filter(user=user, room__hotel=hotel,
                                                   status='confirmed', check_out__lt=timezone.localdate()).exists()
    if not has_completed_booking:
        raise ValidationError('Оставить отзыв можно тоько после завершенного проживания в отеле' \
        ' по подтвержденной брони')

    review, created = Review.objects.update_or_create(hotel=hotel, user=user, defaults={
        'rating': rating,
        'text': text,
        'is_approved': False
    })
    return review


def get_hotel_avg_rating(hotel_id):
    """Возвращает средний рейтинг по одобренным отзывам с кешированием."""
    cache_key = f'hotel:{hotel_id}:avg_rating'
    return cache.get_or_set(
        cache_key,
        lambda: Review.objects.filter(hotel_id=hotel_id, is_approved=True)
        .aggregate(avg_rating=Avg('rating'))['avg_rating'],
        timeout=60 * 15
    )
