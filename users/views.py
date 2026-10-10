from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UserRegisterForm, ProfileUpdateForm


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
        # Отображаем мтраницу регистрации и передаем форму в шаблон
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    # Проверяем, отправлена ли форма авторизации
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        user = form.get_user()
        login(request, user)      
        messages.success(request, f'Вы вошли как {user.username}')

        next_url = request.POST.get('next') or request.GET.get('next')

        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect('users:profile')
    else:
        form = AuthenticationForm()
        
    return render(request, 'users/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


@require_POST
def logout_view(request):
    """Выход пользователя из системы"""
    # Очищаем текущую пользовательскую сессию
    logout(request)
    # Показываем информационное сообщение
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('core:home')


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен')
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def profile_view(request):
    """Личный кабинет. Декоратор пускает сюда только авторизованных пользователей,
    гостя перенаправит на страницу входа"""
    # Данные текущего пользователя всегда доступны через request.user, поэтому нет необходимости делать запрос к БД
    bookings = request.user.bookings.select_related('room', 'room__hotel').all()
    return render(request, 'users/profile.html', {
            'profile_user': request.user,
            'bookings': bookings
        })
