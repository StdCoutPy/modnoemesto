# LOGIN

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from .models import CustomUser, EmailVerificationToken, PasswordResetToken
from .forms import RegistrationForm, PasswordSetForm, LoginForm
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import string
import random
from .models import Coupon

from rest_framework.decorators import api_view
from rest_framework.response import Response

import uuid


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            existing_user = CustomUser.objects.filter(email=email).first()

            if existing_user:
                # если email уже подтвержден — запрещаем регистрацию
                if existing_user.email_verified:
                    messages.error(request, 'Пользователь с таким email уже существует')
                    return redirect('register')

                # если email не подтвержден — удаляем старого пользователя и токен
                EmailVerificationToken.objects.filter(user=existing_user).delete()
                existing_user.delete()

            # Создаем пользователя
            user = CustomUser.objects.create_user(
                username=email,  # Используем email как username
                email=email,
                password=None,  # Пароль пока не установлен
                is_active=True
            )

            # Проверяем, является ли email админским
            from django.conf import settings
            if email in settings.ADMIN_EMAILS:
                user.is_admin = True
                user.save()

            # Создаем токен для верификации email
            token = EmailVerificationToken.objects.create(user=user)
            token.expires_at = timezone.now() + timedelta(hours=1)
            token.save()

            # Отправляем email с подтверждением
            verification_url = f"{request.scheme}://{request.get_host()}/users/accounts/verify-email/{token.token}/"

            # ТЕПЕРЬ ИСПОЛЬЗУЕМ НАШИ НАСТРОЙКИ И КРАСИВОЕ ПИСЬМО
            subject = 'Подтверждение email - Modnoe Mesto'

            # 1. Текстовый вариант (для почтовых клиентов без HTML)
            text_content = f"""
            Подтверждение email - Modnoe Mesto

            Здравствуйте!

            Благодарим за регистрацию в интернет-магазине Modnoe Mesto.

            Для завершения регистрации и активации вашего аккаунта, 
            пожалуйста, подтвердите ваш email по ссылке:

            {verification_url}

            Ссылка действительна в течение 24 часов.

            Если вы не регистрировались на нашем сайте, 
            пожалуйста, проигнорируйте это письмо.

            ---
            Modnoe Mesto
            г. Москва, ул. Примерная, д. 1
            Телефон: +7 (495) 123-45-67
            https://modnoemesto.ru
            """

            # 2. HTML вариант (красивое письмо)
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: #000; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .button {{ display: inline-block; background: #000; color: white; padding: 12px 25px; 
                              text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ background: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                    .link-box {{ background: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; 
                               word-break: break-all; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>MODNOE MESTO</h1>
                </div>

                <div class="content">
                    <h2>Подтверждение Email</h2>

                    <p>Здравствуйте!</p>

                    <p>Благодарим за регистрацию в интернет-магазине <strong>Modnoe Mesto</strong>.</p>

                    <p>Для завершения регистрации нажмите на кнопку:</p>

                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">Подтвердить Email</a>
                    </div>

                    <p>Или скопируйте ссылку:</p>
                    <div class="link-box">{verification_url}</div>

                    <p>Ссылка действительна <strong>24 часа</strong>.</p>

                    <p>Если вы не регистрировались, проигнорируйте это письмо.</p>

                    <p>С уважением,<br>Команда Modnoe Mesto</p>
                </div>

                <div class="footer">
                    <p>&copy; 2025 Modnoe Mesto. Все права защищены.</p>
                    <p>г. Москва, ул. Примерная, д. 1</p>
                    <p>Телефон: +7 (495) 123-45-67</p>
                    <p><a href="https://modnoemesto.ru" style="color: #666;">modnoemesto.ru</a></p>
                </div>
            </body>
            </html>
            """

            # Создаем и отправляем письмо
            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,  # Используем настройки из settings.py
                    to=[email],
                    headers={'X-Priority': '1', 'Importance': 'high'}  # Помечаем как важное
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                messages.success(request, 'На ваш email отправлено письмо с подтверждением')
                return redirect('register')

            except Exception as e:
                # Если произошла ошибка при отправке, показываем ссылку для теста
                print(f"Ошибка отправки email: {e}")
                messages.warning(request,
                                 f'Письмо не отправлено. Для теста используйте ссылку: {verification_url}')
                return redirect('register')

    else:
        form = RegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def verify_email_view(request, token):
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        if verification_token.is_valid():
            user = verification_token.user
            user.email_verified = True
            user.save()

            # ВАЖНО: Генерируем и отправляем купон только после подтверждения!
            generate_welcome_coupon(user)

            verification_token.delete()

            request.session['user_for_password'] = user.id
            messages.success(request, 'Email подтвержден! Промокод на скидку отправлен вам на почту.')
            return redirect('set_password')
        else:
            messages.error(request, 'Срок действия ссылки истек')
            return redirect('register')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения')
        return redirect('register')


def set_password_view(request):
    user_id = request.session.get('user_for_password')
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, начните регистрацию заново')
        return redirect('register')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = PasswordSetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password1'])
            user.save()
            del request.session['user_for_password']

            # Автоматически логиним пользователя
            login(request, user)
            messages.success(request, 'Пароль успешно установлен! Добро пожаловать!')
            return redirect('profile')
    else:
        form = PasswordSetForm()

    return render(request, 'users/set_password.html', {'form': form, 'user': user})


def generate_welcome_coupon(user):
    # Генерируем код
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    promo_code = f"HELLO-{random_str}"

    # Создаем в базе
    Coupon.objects.create(code=promo_code, discount_value=5000, is_active=True)

    # Подготовка письма
    subject = '🎁 Ваш промокод на скидку!'

    # Можно создать отдельный HTML-шаблон для купона: emails/coupon_email.html
    context = {'user': user, 'promo_code': promo_code, 'discount': 5000}
    html_content = render_to_string('emails/coupon_email.html', context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        headers={'X-Priority': '1', 'Importance': 'high'}
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, f'Добро пожаловать, {form.user.email}!')

            # Перенаправляем админов в админку или профиль
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')


# LOGIN END
@login_required
def profile_view(request):
    # Получаем все заказы пользователя, сортируем: новые в начале
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')  # или как называется твой URL профиля
    else:
        form = ProfileUpdateForm(instance=request.user)

    # Передаем заказы в шаблон
    return render(request, 'users/profile.html', {'form': form,
                                                  'orders': user_orders

                                                  })


@login_required
@api_view(['POST'])
def link_telegram(request):
    token = request.data.get('token')
    telegram_id = request.data.get('telegram_id')

    try:
        user = CustomUser.objects.get(telegram_token=token)

        user.telegram_id = telegram_id
        user.telegram_verified = True
        user.telegram_token = None
        user.save()

        return Response({"status": "ok"})

    except CustomUser.DoesNotExist:
        return Response({"error": "invalid token"}, status=400)


def generate_telegram_token(user):
    token = str(uuid.uuid4())

    user.telegram_token = token
    user.telegram_token_created_at = timezone.now()
    user.save()

    return token


def get_telegram_link(user):
    token = generate_telegram_token(user)
    return f"https://t.me/your_bot?start={token}"


# users/views.py

import hashlib
import hmac
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import CustomUser


def check_telegram_auth(data):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    check_hash = data.pop('hash')

    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(data.items())
    )

    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(hmac_hash, check_hash)


def telegram_callback(request):
    data = request.GET.dict()

    if not check_telegram_auth(data.copy()):
        return JsonResponse({"error": "invalid telegram auth"}, status=400)

    telegram_id = data.get('id')

    if not request.user.is_authenticated:
        return JsonResponse({"error": "not logged in"}, status=403)

    user = request.user

    # защита от дублей
    if CustomUser.objects.filter(telegram_id=telegram_id).exclude(id=user.id).exists():
        return JsonResponse({"error": "telegram already linked"}, status=400)

    user.telegram_id = telegram_id
    user.telegram_verified = True
    user.save()

    return redirect('/users/accounts/profile/')  # куда вернуть пользователя
