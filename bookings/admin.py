from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Управление бронированиями
    list_display = ('id', 'name', 'room', 'check_in', 'check_out', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'created_at')
    search_fields = ('user__username', 'room__number', 'room__hotel__name')
    # Навигация по датам
    date_hierarchy = 'check_in'
