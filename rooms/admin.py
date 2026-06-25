from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'number', 'room_type', 'description', 'price_night', 'capacity')
    list_filter = ('hotel', 'room_type', 'is_available')
    search_fields = ('hotel', 'room_type', 'description')


# Поля и их порядок на странице редактирования номера
fields = (
        'hotel',
        'number',
        'room_type',
        ('price_night', 'capacity'),
        'description',
        'is_available'
    )
def short_description(self, obj):
    # Если описание отсутствуе - выводим прочерк
    if not obj.description:
        return '-'
    text = obj.description
    return text if len(text) <= 50 else text[:50] + '...'
    
# Заголовок столбца в админ панели
short_description.short_description = 'Описание'
    
