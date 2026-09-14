from django.shortcuts import render
from hotels.models import Hotel
from rooms.models import Room

# Главная функция нашей страницы
def home(request):
    top_hotels = Hotel.objects.filter(is_active=True).order_by('-rating')[:3]
    feautured_rooms = Room.objects.filter(is_available=True).select_related('hotel')[:3]

    stats = {
            'hotels': Hotel.objects.filter(is_active=True).count(),
            'rooms': Room.objects.filter(is_available=True).count(),
            'cities': Hotel.objects.values('city').distinct().count()
        }
