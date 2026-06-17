from django.shortcuts import render
from .models import Room


def rooms_list(request):
    query = request.GET.get('q', '')

    rooms = Room.objects.all()

    # Фильтрация по типу номера ил  по названию отеля
    if query:
        rooms = [
                r for r in rooms
                if query.lower() in r.get_room_type_display().lower()
                or query.lower() in r.hotel.lower()
            ]
    
    return render(request, 'rooms/list.html', {
            'rooms': rooms,
            'query': query
        })