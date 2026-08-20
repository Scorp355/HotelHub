from django.urls import path
from . import views


app_name = 'boockings'

urlpatterns = [
        path('', views.booking_list, name='list'),
        path('create/<int:room_id/>', views.booking_create, name='create'),
    ]