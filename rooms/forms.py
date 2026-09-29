from django import forms
from django.utils import timezone
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


class RoomSearchForm(forms.Form):
    # Поле для даты заезда
    check_in = forms.DateField(required=False, widget=forms.DateInput(
            attrs={'type': 'date'}
        ))
    check_out = forms.DateField(required=False, widget=forms.DateInput(
            {'type': 'date'}
        ))
    sort_by = forms.DateField(choices=[
            ('price', 'Сначала дешевле'),
            ('-price', 'Сначала дороже')
        ], required=False)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        if check_in and check_out and check_in >= check_out:
            raise forms.ValidationError('Дата выезда должна быть позже даты заезда.')
        return cleaned_data

