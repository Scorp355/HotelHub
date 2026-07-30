from django.shortcuts import render, get_object_or_404
from .models import Room
from .forms import RoomTypesFiter


# Обрабатывает запрос пользователя и возвращает страницу со списком номеров
def rooms_list(request):

    form = RoomTypesFiter(request.GET)

    rooms = Room.objects.filter(is_available=True).select_related('hotel')

    if form.is_valid():
        room_type = form.cleaned_data.get('room')
        if room_type:
            rooms = rooms.filter(room_type=room_type)
    
    hotel_name = request.GET.get('hotel_name', '')
    if hotel_name:
        rooms = rooms.filter(hotel__name__icontains=hotel_name)
    
    return render(request, 'rooms/list.html', {
        'rooms': rooms,
        'form': form
    })


def room_detail(request, pk):
    """Страница одного номера с кнопкой бронирования"""
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'rooms/detail.html', {'room': room})




    # query = request.GET.get('q', '')

    # rooms = Room.objects.all()

    # # Фильтрация по типу номера и по названию отеля
    # if query:
    #     rooms = [
    #             r for r in rooms
    #             if query.lower() in r.get_room_type_display().lower()
    #             or query.lower() in r.hotel.lower()
    #         ]
    
    # return render(request, 'rooms/list.html', {
    #         'rooms': rooms,
    #         'query': query
    #     })