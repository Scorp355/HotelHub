from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        # Порядок полей в форме = порядок в этом кореже
        fields = ('username', 'email', 'phone', 'password1', 'password2')


class ProfileUpdateForm(forms.ModelForm):
    """
    Форма редактирования профиля: только те поля, которые можно менять
    самостоятельно (без пароля и без username). avatar — обычный
    ImageField модели, Django сам подставит виджет загрузки файла
    (<input type="file">) и провалидирует его перед сохранением.
    """

    class Meta:
        model = User
        fields = ('email', 'phone', 'avatar')