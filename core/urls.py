from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
        path('', views.home_view, name='home'),
        path('faq/', views.faq_view, name='faq'),
        path('contact/', views.contact_view, name='contact'),
    ]