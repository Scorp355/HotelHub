from django.contrib import admin
from django.utils.html import format_html
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'number', 'hotel', 'room_type', 'price_night', 'capacity', 'is_available')
    list_filter = ('hotel', 'room_type', 'is_available')
    search_fields = ('number', 'hotel__name')

    def image_preview(self, obj):
        """Миниатюра фото номера в списке админки."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width:48px;height:32px;object-fit:cover;'
                'border-radius:4px;">', obj.image.url,
            )
        return '—'
    
    image_preview.short_description = 'Фото'



    
    # # Поля и их порядок на странице редактирования номера
    # fields = (
    #         'hotel',
    #         'number',
    #         'room_type',
    #         ('price_night', 'capacity'),
    #         'description',
    #         'is_available'
    #     )
    
    # def short_description(self, obj):
    #     # Если описание отсутствуе - выводим прочерк
    #     if not obj.description:
    #         return '-'
    #     text = obj.description
    #     return text if len(text) <= 50 else text[:50] + '...'
        
    # # Заголовок столбца в админ панели
    # short_description.short_description = 'Описание'
    
