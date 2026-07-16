from django.shortcuts import render, get_object_or_404
# Импорт функций для отображения и поиска объектов
from .models import Hotel




def hotel_list(request):
    city = request.GET.get('city', '')
    hotels = Hotel.objects.filter(is_active=True)

    # Фильтрация по городу

    # if city:
    #     hotels = [h for h in hotels if city.lower() in h.city.lower()]
    
    if city:
        hotels = hotels.filter(city_icintains=city)

    return render(request, 'hotels/list.html', {
        'hotels': hotels,   # список найденных отелей
        'city': city        # текст поиска для отображения в форме
        })


# Функция отображения информации об одном отеле
def hotel_detail(request, pk):
    # Ищем отель по id
    hotel = get_object_or_404(
            Hotel,
            pk=pk,
            is_active=True
        )
    # получаем свободные номера выбранного отеля
    rooms = hotel.rooms.filter(is_available=True)
    return render(request, 'hotel_detail.html', {'hotel': hotel, 'rooms': rooms})
    

