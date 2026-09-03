from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from rooms.models import Room
from bookings.models import Booking
from .forms import BookingForm
from . import services


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room', 'room_id')
    return render(request, 'bookings/list.html', {'bookings': bookings})


@login_required
def booking_create(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                services.create_booking(user=request.user,
                                        room=room,
                                        check_in=form.cleaned_data['check_in'],
                                        check_out=form.cleaned_data['check_out'],
                                        guests=form.cleaned_data['guests'],
                                        )
            except ValidationError as exc:
                form.add_error(None, exc.messages[0])

            else:
                messages.success(request, 'Номер забронирован! Проверьте бронь в личном кабинете!')
                # Переадресация на бронирование: список всех бронирований
                return redirect('bookings:list')
    else:
        form = BookingForm(initial={'room': room})
    
    return render(request, 'bookings/create.html', {'form': form, 'room': room})


@login_required
def booking_cansel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    try:
        services.cansel_booking(booking)
        messages.info(request, f'Бронь {booking.pk} отменена')
    except ValidationError as exc:
        messages.error(request, exc.messages[0])

    return redirect('bookings:list')
            