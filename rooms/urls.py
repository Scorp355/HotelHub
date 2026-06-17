from django.urls import path
from . import views


urlpatterns = [
    path('', views.rooms_list, name='room_list'),
]