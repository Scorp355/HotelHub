from django.urls import path

from . import views


app_name = 'reviews'


urlpatterns = [
    path('hotels/<int:hotel_id>/submit', views.submit_review, name='submit_review'),
    path('<int:review_id>/delete', views.delete_review, name='delete_review')
]