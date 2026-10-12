from django import forms

from . models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(label='Оценка', choices=[
        (5, '5 - Отлично'),
        (4, '4 - Хорошо'),
        (3, '3 - Нормально'),
        (2, '2 - Плохо'),
        (1, '1 - Очень плохо'),
    ], widget=forms.Select(attrs={'class':'review-form__select'}))

    text = forms.CharField(label='Ваш отзыв', min_length=10, widget=forms.Textarea(
        attrs={
            'class': 'review-form__textarea',
            'rows': 5,
            'placeholder': 'Расскажите о своих впечатлениях...'
        }
    ))

    class Meta:
        model = Review
        fields = ('rating', 'text')

    def clean_text(self):
        text = self.cleaned_data['text'].strip()

        if not text:
            raise forms.ValidationError('Текст отзыва не может быть пустым')

        return text