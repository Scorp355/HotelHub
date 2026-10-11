
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from hotels.views import stats_api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('hotels/', include('hotels.urls')),
    path('rooms/', include('rooms.urls')),
    path('bookings', include('bookings.urls')),
    path('api/stats/', stats_api, name='api_stats'),
]

# В режиме разработки отдаем загруженные медиафайлы напрямую через Django.
# В продакшене это делает веб-сервер
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
