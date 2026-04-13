from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import string
import random
from .models import Coupon, CustomUser

@receiver(post_save, sender=CustomUser)
def send_welcome_coupon(sender, instance, created, **kwargs):
    if created:
        # Генерируем случайный код
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        Coupon.objects.create(code=code, discount_percent=10)  # Скидка 10% новичку

        # Отправка на почту
        send_mail(
            'Ваш промокод на скидку!',
            f'Добро пожаловать! Ваш промокод: {code}',
            'from@yourdomain.com',
            [instance.email],
            fail_silently=False,
        )
