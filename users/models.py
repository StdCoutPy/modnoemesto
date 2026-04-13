from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
import string
import random

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")
    # Добавляем новые поля:
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")

    created_at = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)

    # 👇 Telegram поля
    telegram_id = models.CharField(max_length=50, blank=True, null=True)
    telegram_verified = models.BooleanField(default=False)
    telegram_token = models.CharField(max_length=100, blank=True, null=True)
    telegram_token_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email
#
class EmailVerificationToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        return timezone.now() < self.expires_at


class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        return timezone.now() < self.expires_at


#LOGIN END


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Сумма скидки")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

