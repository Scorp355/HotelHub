from django.urls import path

from . views import HotelListAPIView, RoomListAPIView, BookingListCreateAPIView


app_name = 'api'


urlpatterns = [
    path('hotels/', HotelListAPIView.as_view(), name='hotel-list'),
    path('rooms/', RoomListAPIView.as_view(), name='room-list'),
    path('bookings/', BookingListCreateAPIView.as_view(), name='booking-list'),
]