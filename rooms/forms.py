from django import forms
from .models import Room


class RoomTypesFiter(forms.Form):

    ROOM_TYPES = [('', 'Все типы')] + list(Room.ROOM_TYPES)
    
    room = forms.ChoiceField(
        choices=ROOM_TYPES,
        label='Выбери тип номера',
        initial='',
        required=False,
        widget=forms.Select(attrs={
            'class': 'search-select custom-dropdown', # Ваши CSS-классы
        })
    )