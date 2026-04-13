from django.urls import path
from . import views
from django.views.generic.base import RedirectView
from django.conf import settings
import os
from django.http import FileResponse, HttpResponse



urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),

    # Маскируемся под корень, как хочет iPhone
    path('apple-touch-icon.png', RedirectView.as_view(url=settings.STATIC_URL + 'images/apple-touch-icon.png')),
    path('apple-touch-icon-precomposed.png',
         RedirectView.as_view(url=settings.STATIC_URL + 'images/apple-touch-icon.png')),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'images/favicon.svg')),  # Или .ico, если он есть

]