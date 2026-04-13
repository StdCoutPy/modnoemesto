from django.urls import path
from . import views

urlpatterns = [

    path("lookbook/", views.lookbook_index, name="lookbook_index"),
    path("lookbook/<slug:slug>/", views.lookbook_detail, name="lookbook_detail"),

]