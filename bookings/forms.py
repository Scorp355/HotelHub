from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):
    """Форма создания брони. Поле room прячем и подставляем номер из url"""

    class Meta:
        model = Booking
        fields = ('room', 'check_in', 'check_out', 'guests')
        widgets = {
                'room': forms.HiddenInput(),
                'check_in': forms.DateInput(attrs={'type': 'date'}),
                'check_out': forms.DateInput(attrs={'type': 'date'}),
                'guests': forms.NumberInput(attrs={'min': 1}),
            }


    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError('Дата выезда должна быть позже даты заезда')
        return cleaned