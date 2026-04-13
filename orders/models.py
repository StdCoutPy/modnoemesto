from django.db import models
from django.conf import settings
from products.models import Product  # Твоя модель товара


class Order(models.Model):
    STATUS_CHOICES = [('new', 'Новый'), ('paid', 'Оплачен'), ('failed', 'Ошибка')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Снимок данных (Snapshot), чтобы история заказов не менялась при смене профиля
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address = models.TextField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')

    # Поля для Freedom Pay
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена на момент покупки
