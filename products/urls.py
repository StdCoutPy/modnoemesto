from django.urls import path
from . import views

urlpatterns = [
    path('shop/', views.shop, name='shop'),
    path('items/', views.items, name='items'),
    # Новые URL для товаров
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # Категории
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('new/', views.new_arrivals, name='new_arrivals'),
    path('sale/', views.sale, name='sale'),
    path('collection/', views.collection, name='collection'),
]