from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Room
from .forms import RoomSearchForm

SORT_FIELDS = {
        'price': 'price_night',
        '-price': '-price_night',
    }

class RoomListView(ListView):
    model = Room
    template_name = 'rooms/list.html'
    context_object_name = 'rooms'
    paginate_by = 6     # Максимум 6 номеров на одной странице
    
    def get_queryset(self):
        queryset = Room.objects.filter(is_available=True).select_related('hotel')

        query = self.request.GET.get('q', '')
        if query:
            matching_types = [code for code, label in Room.ROOM_TYPES
                              if query.lower() in label.lower()]
            queryset = queryset.annotate(hotel_name_lower=Lower('hotel_name').filter(
                    Q(hotel_name_lower__contains=query.lower())
                    | Q(room_type__in=matching_types)
                ))            

        form = RoomSearchForm(self.request.GET)
        if form.is_valid():
            check_in = form.cleaned_data.get('check_in')
            check_out = form.cleaned_data.get('check_out')
            sort_by = form.cleaned_data.get('sort_by')
            # Фильтруем по занятости, только если обе даты заполнены —
            # частично заполненная форма не должна ломать обычный список.
            if check_in and check_out:
                queryset = queryset.free_between(check_in, check_out)

            if sort_by in SORT_FIELDS:
                sort_field = SORT_FIELDS[sort_by]
        return queryset.order_by(sort_field)    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RoomSearchForm(self.request.GET)
        context['query'] = self.request.GET.get('q', '')
        return context


def room_detail(request, pk):
    """Страница одного номера с кнопкой бронирования"""
    room = get_object_or_404(Room.objects.with_today_status(), pk=pk)
    return render(request, 'rooms/detail.html', {'room': room})


# Обрабатывает запрос пользователя и возвращает страницу со списком номеров
# def rooms_list(request):

#     form = RoomTypesFiter(request.GET)
#     rooms = Room.objects.filter(is_available=True).select_related('hotel')

#     if form.is_valid():
#         room_type = form.cleaned_data.get('room')
#         if room_type:
#             rooms = rooms.filter(room_type=room_type)
    
#     hotel_name = request.GET.get('hotel_name', '')
#     if hotel_name:
#         rooms = rooms.filter(hotel__name__icontains=hotel_name)
    
#     return render(request, 'rooms/list.html', {
#         'rooms': rooms,
#         'form': form
#     })



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