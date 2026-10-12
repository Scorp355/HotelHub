from django.contrib import admin

from . models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('hotel__name', 'user__username', 'text')
    readonly_fields = ('created_at',)

    list_select_related = ('hotel', 'user')

    actions = ('approve_reviews', 'reject_reviews')

    @admin.action(description='Одобрить выбранные отзывы')
    def approve_reviews(self, request, queryset):
        count = 0
        for review in queryset.iterator():
            if not review.is_approved:
                review.is_approved = True
                review.save(update_fields=['is_approved'])
                count += 1
        self.message_user(request, f'Одобрено отзывов: {count}.')


    @admin.action(description='Отклонить выбранные отзывы')
    def reject_reviews(self, request, queryset):
        count = 0
        for review in queryset.iterator():
            if review.is_approved:
                review.is_approved = False
                review.save(update_fields=['is_approved'])
                count += 1
        self.message_user(request, f'Отклонено отзывов: {count}.')
