from __future__ import annotations
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Q
from rooms.models import Room
from .models import Booking


ACTIVE_STATUSES = ('pending', 'confirmed')


def calculate_nights(check_in: date, check_out: date):
    nights = (check_out - check_in).days
    return nights if nights > 0 else 0


def calculate_total_price(room: Room, check_in: date, check_out: date) -> Decimal:
    """Рассчитывает итоговую стоимость проживания в номере"""
    nights = calculate_nights(check_in, check_out)
    return room.price_night * nights


def validate_booking_dates(check_in: date, check_out: date) -> None:
    if check_in is None or check_out is None:
        raise ValidationError('Укажите даты заезда и выезда')
    if check_in < date.today():
        raise ValidationError('Дата заезда не может быть в прошлом')
    if check_out <= check_in:
        raise ValidationError('Дата выезда должна быть позже даты заезда')


def is_room_available(room: Room, check_in: date, check_out: date,
                      exclude_booking_id: int|None = None) -> bool:
    
    overlapping = Booking.objects.filter(room=room, status__in=ACTIVE_STATUSES).filter(
        Q(check_in__lt=check_out) & Q(check_out__gt=check_in))    
    
    if exclude_booking_id is not None:
        overlapping = overlapping.exclude(pk=exclude_booking_id)

    return not overlapping.exists()


def create_booking(user, room: Room, check_in: date, check_out:date, guests: int = 1) -> Booking:
    validate_booking_dates(check_in, check_out)
    if guests < 1:
        raise ValidationError('Число гостей не должно быть меньше одного')
    if guests > room.capacity:
        raise ValidationError(f'Номер вмещает не более {room.capacity} гост(я/ей)')
    if not is_room_available(room, check_in, check_out):
        raise ValidationError('Номер уже забронирован на выбранные даты')
    return Booking.objects.create(user=user, room=room, check_in=check_in, check_out=check_out,
                                  guests=guests, status='pending')


def cansel_booking(booking: Booking) -> Booking:
    """Отменяет бронирование"""
    if booking.status == 'cancelled':
        raise ValidationError('Эта бронь уже отменена')
    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    return booking
