from django.contrib import admin
from .models import Hotel


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'price_night', 'rating', 'is_active')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'city')


