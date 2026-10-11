from django.core import signing
from . models import Booking


VOUCHER_SALT = 'bookings.voucher'
VOUCHER_MAX_AGE = 7 * 24 * 60 *60   # 7 дней в секундах


def create_voucher_token(booking: Booking) -> str:
    """Создаёт подписанный токен для бронирования."""
    if booking.status != 'confirmed':
        raise ValueError('Ваучер доступен только для подтверждённого бронирования.')
    signer = signing.TimestampSigner(salt=VOUCHER_SALT)
    return signer.sign(str(booking.pk))


def get_booking_by_vaucher_token(token: str) -> Booking:
    """Проверяет подпись и срок действия токена, возвращает бронирование."""
    signer = signing.TimestampSigner(salt=VOUCHER_SALT)
    try:
        booking_id = signer.unsign(token, max_age=VOUCHER_MAX_AGE)
        booking = Booking.objects.select_related('user', 'room', 'room__hotel').get(pk=int(booking_id))
    except(signing.BadSignature, ValueError, Booking.DoesNotExist):
        from django.http import Http404
        raise Http404('Ваучер недействителен или срок его действия истёк.')

    if booking.status != 'confirmed':
        from django.http import Http404
        raise Http404('Ваучер недоступен.')
    return booking
