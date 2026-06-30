from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BoockingAdmin(admin.ModelAdmin):

    list_display = ('room', 'guest_name', 'guest_email', 'date_of_check_in', 'date_check_out', 'status', 'created_at')
    list_filter = ('status', 'date_of_check_in')
    search_fields = ('guest_name', 'room__number')


