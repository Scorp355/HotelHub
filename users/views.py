from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserRegisterForm


def register_view(request):
    # Проверка, была ли отправлена форма регистрации
    if request.method == 'POST':
        # Создаем объект формы и заполняем его данными из POST-запроса
        form = UserRegisterForm(request.POST)
        # Если все поля заполнены корректно
        if form.is_valid():
            # Сохраняем нового пользователя в БД
            user = form.save()
            # Сразу авторизуем пользователя после регистрации
            login(request, user)
            # Добавляем уведомление об успешной регистрации
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
            # Направляем пользователя в личный кабинет
            return redirect('users:profile')
    else:
        # При GET-запросе создаем пустую форму
        form = UserRegisterForm()
        # Отображаес мтраницу регистрации и передаем форму в шаблон
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    # Проверяем, отправлена ли форма авторизации
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        # Если логин и пароль прошли встроенную проверку
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Проверяем существование пользователя с такими данными
            user = authenticate(request, username=username, password=password)
            # Если пользователь найден
            if user is not None:
                # Авторизуем пользователя и сохраняем в текущей сессии
                login(request, user)
                messages.success(request, f"Вы вошли как {user.username}.")
                next_url = request.GET.get('next')
                return redirect(next_url or 'users:profile')
    else:
        # При первом открытии страницы отображаем пустую форму
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выход пользователя из системы"""
    # Очищаем текущую пользовательскую сессию
    logout(request)
    # Показываем информационное сообщение
    messages.info(request, 'Вы вышли из аккаунта')
    # return redirect('core:home')


@login_required
def profile_view(request):
    """Личный кабинет. Декоратор пускает сюда только авторизованных пользователей,
    гостя перенаправит на страницу входа"""
    # Данные текущего пользователя всегда доступны через request.user, поэтому не необходимости делать запрос к БД
    bookings = request.user.bookings.select_related('room', 'room__hotel').all()
    return render(request, 'users/profile.html', {
            'profile_user': request.user,
            'bookings': bookings
        })
