from datetime import date

from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.serializers import Serializer
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ValidationError as DjangoValidationError

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking
from . serializers import HotelListSerializer, RoomListSerializer, BookingCreateSerializer, BookingListSerializer


class HotelListAPIView(ListAPIView):
    serializer_class = HotelListSerializer

    def get_queryset(self):
        return Hotel.objects.active().with_stats().order_by('-created_at', '-pk')


class RoomListAPIView(ListAPIView):
    serializer_class = RoomListSerializer

    def get_queryset(self):
        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')

        if not check_in or not check_out:
            raise DRFValidationError({'dates': 'Укажите check_in и check_out в формате YYYY-MM-DD.'})

        try:
            check_in_date = date.fromisoformat(check_in)
            check_out_date = date.fromisoformat(check_out)
        except ValueError:
            raise DRFValidationError({'dates': 'Некорректный формат даты. Используйте YYYY-MM-DD.'})

        if check_in_date < date.today():
            raise DRFValidationError({'check_in': 'Дата заезда не может быть в прошлом.'})

        if check_out_date <=check_in_date:
            raise DRFValidationError({'check_out': 'Дата выезда должна быть позже даты заезда.'})

        return (Room.objects.on_sale().free_between(check_in_date, check_out_date).select_related('hotel')
                .order_by('hotel__name', 'number', 'pk'))


class BookingListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        return (
            Booking.objects
            .filter(user=self.request.user)
            .select_related('room', 'room__hotel')
        )   

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BookingCreateSerializer
        return BookingListSerializer    
