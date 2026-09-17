from django.shortcuts import render, redirect
from django.contrib import messages
from hotels.models import Hotel
from rooms.models import Room
from . models import PromoOffer, Facility, Review, FAQItem, ContactMessage



# Главная функция нашей страницы
def home_view(request):
    context = {
            'promos': PromoOffer.objects.filter(is_active=True)[:3],
            'facilities': Facility.objects.all()[:4],
            'reviews': Review.objects.filter(ratting__gte=4).order_by('-created_at')[:3]
        }
    return render(request, 'core/home.html', context=context)


# Страница часто задаваемых вопросов
def faq_view(request):
    faqs = FAQItem.objects.all().order_by('order')
    return render(request, 'core/faq.html', {'faqs': faqs})

# Страница обратной связи
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        if name and email and message_text:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message_text)
            messages.success(request, 'Ваше сообщение успешно отправлено')
            return redirect('core:contact')
    else:
        messages.error(request, 'Ошибка! Пожалуйста, заполните все обязательные поля.')
    return render(request, 'core/contact.html')







            
# Главная функция нашей страницы
# def home(request):
#     top_hotels = Hotel.objects.filter(is_active=True).order_by('-rating')[:3]
#     feautured_rooms = Room.objects.filter(is_available=True).select_related('hotel')[:3]

#     stats = {
#             'hotels': Hotel.objects.filter(is_active=True).count(),
#             'rooms': Room.objects.filter(is_available=True).count(),
#             'cities': Hotel.objects.values('city').distinct().count()
#         }
