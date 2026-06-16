from django.urls import path
from . import views


urlpatterns = [
    # path('admin/', views.admin.site.urls),
    path('', views.hotel_list, name='hotel_list'),
]