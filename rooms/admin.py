from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'number', 'room_type', 'description', 'price_night', 'capacity', )
    list_filter = ('hotel', 'room_type')
    search_fields = ('hotel', 'room_type')