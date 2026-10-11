from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Hotel


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('cover_preview','name', 'city', 'price_night', 'rating', 'is_active', 'last_booking_date')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city')

    def get_queryset(self, request):
        """Получает отели с датой последнего бронирования."""
        queryset = super().get_queryset(request)
        return queryset.with_last_booking_date()

    @admin.display(description='Последняя бронь', ordering='last_booking_date')
    def last_booking_date(self, obj):
        """Отображает дату последней брони или прочерк."""
        if obj.last_booking_date is None:
            return '—'

        return timezone.localtime(obj.last_booking_date).strftime(
            '%d.%m.%Y %H:%M'
        )

    def cover_preview(self, obj):
        """Маленькая миниатюра обложки прямо в списке — видно сразу,
        у какого отеля уже есть фото, без открытия карточки."""
        if obj.cover:
            return format_html(
                '<img src="{}" style="width:48px;height:32px;object-fit:cover;'
                'border-radius:4px;">', obj.cover.url,
            )
        return '—'
    cover_preview.short_description = 'Обложка'


