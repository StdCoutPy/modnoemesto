from django.urls import path
from . import views

urlpatterns = [
    # Временный URL для добавления в корзину
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # Просмотр корзины
    path('cart/', views.cart_view, name='cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    # Путь для создания заказа и ухода на оплату
    path('checkout/', views.create_order_view, name='checkout'),

    # Путь, на который Freedom Pay вернет пользователя после оплаты
    path('payment/success/', views.payment_success_view, name='payment_success'),
    # Принимал ID
    path('fake-payment/<int:order_id>/', views.fake_payment_page, name='fake_payment'),
    path('process-fake-success/<int:order_id>/', views.payment_success_view, name='payment_success'),
]