from django.contrib import admin
from . models import PromoOffer, Review, Facility, FAQItem, ContactMessage


@admin.register(PromoOffer)
class PromoOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percent', 'valid_until', 'is_active')
    list_filter = ('is_active', 'valid_until')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'ratting', 'created_at')
    list_filter = ('ratting', 'created_at')
    search_fields = ('author', 'text')


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'order')
    list_editable = ('order')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

