from django.shortcuts import render
from . models import Hotel


def hotel_list(request):
    city = request.GET.get('city', '')
    hotels = Hotel.objects.all()

    # Фильтрация по городу
    if city:
        hotels = [h for h in hotels if city.lower() in h.city.lower()]

    return render(request, 'hotels/list.html', {
        'hotels': hotels,
        'city': city
        })
