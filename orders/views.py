
from decimal import Decimal

from django.urls import reverse

from DjangoProject.settings import PG_KEY, PG_MERCHANT_ID
from .cart_utils import get_cart, get_cart_items_with_details, update_cart_totals, save_cart
#Для AJAX корзины
from django.http import JsonResponse



from products.models import Product, ProductSize



from .cart_utils import get_cart_summary

#LOGIN

# main/views.py
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.utils import timezone

from users.models import Coupon


#ORDER BD FREEDOM
import hashlib
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .models import Order, OrderItem
from products.models import Product, ProductSize
from users.models import Coupon
from .cart_utils import get_cart, get_cart_items_with_details, clear_cart_session
from django.core.mail import send_mail
from urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt

def cart_view(request):
    """Просмотр корзины с поддержкой промокодов"""
    cart = get_cart(request)
    cart_items = get_cart_items_with_details(request)

    if request.method == 'POST':
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')
        if size_id == '': size_id = None

        # --- НОВАЯ ЛОГИКА: ПРИМЕНЕНИЕ КУПОНА ---
        if action == 'apply_coupon':
            code = request.POST.get('coupon_code', '').strip()
            try:
                coupon = Coupon.objects.get(code__iexact=code, is_active=True)
                request.session['coupon_id'] = coupon.id
                messages.success(request, f'Промокод {code} применен!')
            except Coupon.DoesNotExist:
                request.session['coupon_id'] = None
                messages.error(request, 'Неверный или неактивный промокод')
            return redirect('cart')
        # ---------------------------------------

        # Твоя существующая логика (remove/update)
        elif action == 'remove' and product_id:
            for i, item in enumerate(cart['items']):
                if int(item['product_id']) == int(product_id):
                    item_size_id = item.get('size_id')
                    if (item_size_id is None and size_id is None) or (str(item_size_id) == str(size_id)):
                        del cart['items'][i]
                        break
            update_cart_totals(cart)
            save_cart(request, cart)
            messages.success(request, 'Товар удален')
            return redirect('cart')

        elif action == 'update' and product_id:
            quantity = request.POST.get('quantity')
            try:
                quantity = int(quantity)
                # ... твой код обновления количества ...
                for item in cart['items']:
                    if int(item['product_id']) == int(product_id):
                        item_size_id = item.get('size_id')
                        if (item_size_id is None and size_id is None) or (str(item_size_id) == str(size_id)):
                            item['quantity'] = max(0, quantity) # Упростил для примера
                            break
                update_cart_totals(cart)
                save_cart(request, cart)
                return redirect('cart')
            except (ValueError, TypeError):
                messages.error(request, 'Ошибка формата')

    # --- РАСЧЕТ СКИДКИ ДЛЯ ШАБЛОНА ---
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    if coupon_id:
        coupon = Coupon.objects.filter(id=coupon_id, is_active=True).first()
        if coupon:
            discount_amount = coupon.discount_value

    total_with_discount = Decimal(str(cart['total_price'])) - Decimal(str(discount_amount))
    total_with_discount = max(0, total_with_discount)

    # Проверяем, есть ли у юзера привязанный Telegram
    has_telegram = False
    if request.user.is_authenticated:
        has_telegram = request.user.telegram_verified

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_total_price': cart['total_price'],
        'cart_total_quantity': cart['total_quantity'],
        'discount_amount': discount_amount,
        'total_with_discount': total_with_discount,
        'coupon_id': coupon_id,
        'has_telegram': has_telegram,
    }
    return render(request, 'orders/cart.html', context)



def add_to_cart(request, product_id):

    """Добавить товар в корзину (работает для обычных и AJAX запросов)"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        # Получаем данные из формы
        size_id = request.POST.get('size')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        # Проверяем размер
        size = None
        # В начале функции add_to_cart
        if product.price is None:
            message = 'Этот товар временно недоступен для заказа'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message})
            messages.error(request, message)
            return redirect('product_detail', product_id=product_id)
        if size_id:
            try:
                size = ProductSize.objects.get(id=size_id, product=product)
                if size.quantity < quantity:
                    message = f'Недостаточно товара размера {size.size} в наличии'
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': message})
                    messages.error(request, message)
                    return redirect('product_detail', product_id=product_id)
            except ProductSize.DoesNotExist:
                message = 'Выбранный размер недоступен'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': message})
                messages.error(request, message)
                return redirect('product_detail', product_id=product_id)

        # Если у товара есть размеры, но не выбран
        elif product.sizes.exists():
            message = 'Пожалуйста, выберите размер'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message})
            messages.error(request, message)
            return redirect('product_detail', product_id=product_id)

        # Добавляем в корзину
        from .cart_utils import add_to_cart_session, get_cart_summary
        success, message = add_to_cart_session(request, product_id, size_id, quantity)

        if success:
            cart_summary = get_cart_summary(request)

            # Если это AJAX запрос
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'{message} В корзине: {cart_summary["total_quantity"]} товар(ов)',
                    'cart_total_quantity': cart_summary['total_quantity'],
                    'cart_total_price': cart_summary['total_price']
                })

            # Если обычный запрос
            messages.success(request, f'{message} В корзине: {cart_summary["total_quantity"]} товар(ов)')
            return redirect('product_detail', product_id=product_id)

        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': message})
            messages.error(request, message)

    # Если не POST запрос
    return redirect('product_detail', product_id=product_id)


def update_cart_item(request):
    """Обновить количество товара в корзине (AJAX)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id') or None
        quantity = request.POST.get('quantity')

        if not product_id or not quantity:
            return JsonResponse({'success': False, 'error': 'Неверные данные'})

        try:
            quantity = int(quantity)
            if quantity < 0:
                return JsonResponse({'success': False, 'error': 'Количество не может быть отрицательным'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверное количество'})

        cart = get_cart(request)

        # Ищем товар в корзине
        for item in cart['items']:
            if str(item['product_id']) == str(product_id) and str(item.get('size_id')) == str(size_id):
                if quantity == 0:
                    # Удаляем товар
                    cart['items'].remove(item)
                else:
                    # Обновляем количество
                    item['quantity'] = quantity
                    item['updated_at'] = timezone.now().isoformat()

                update_cart_totals(cart)
                save_cart(request, cart)

                # Получаем обновленную корзину
                cart_summary = get_cart_summary(request)
                cart_items = get_cart_items_with_details(request)

                # Находим обновленный товар для расчета его суммы
                item_total = 0
                for cart_item in cart_items:
                    if (str(cart_item['product'].id) == str(product_id) and
                            str(cart_item['size'].id if cart_item['size'] else '') == str(size_id)):
                        item_total = cart_item['item_total']
                        break

                return JsonResponse({
                    'success': True,
                    'cart_total_quantity': cart_summary['total_quantity'],
                    'cart_total_price': cart_summary['total_price'],
                    'item_total': item_total,
                    'item_removed': quantity == 0
                })

        return JsonResponse({'success': False, 'error': 'Товар не найден в корзине'})

    return JsonResponse({'success': False, 'error': 'Неверный запрос'})




def generate_pg_sig(script_name, params, secret_key):
    """Генерация подписи для Freedom Pay по алфавиту параметров"""
    sorted_params = [str(params[k]) for k in sorted(params.keys())]
    sig_str = f"{script_name};" + ";".join(sorted_params) + f";{secret_key}"
    return hashlib.md5(sig_str.encode()).hexdigest()

def create_order_view(request):
    """Шаг 1: Создание заказа из корзины и редирект на Sandbox"""
    cart_items_details = get_cart_items_with_details(request)
    if not cart_items_details:
        messages.error(request, "Ваша корзина пуста")
        return redirect('cart')

    # Получаем итоговую сумму с учетом промокода (как в твоем cart_view)
    cart = get_cart(request)
    discount_amount = Decimal('0')
    coupon_id = request.session.get('coupon_id')
    if coupon_id:
        coupon = Coupon.objects.filter(id=coupon_id, is_active=True).first()
        if coupon:
            discount_amount = Decimal(str(coupon.discount_value))

    total_price = Decimal(str(cart['total_price'])) - discount_amount
    total_price = max(Decimal('0'), total_price)

    # 1. Создаем Заказ
    order = Order.objects.create(
        user=request.user,
        phone=request.user.phone or '',
        city=request.user.city or '',
        address=request.user.address or '',
        total_amount=total_price,
        discount_amount=discount_amount
    )

    # 2. Создаем элементы заказа (OrderItem)
    for item_detail in cart_items_details:
        OrderItem.objects.create(
            order=order,
            product=item_detail['product'],
            size=item_detail['size'] or 'ONE SIZE',  # Сохраняем строку ('M', 'L' и т.д.)
            quantity=item_detail['item']['quantity'],
            price=item_detail['product'].price
        )

    # 3. Параметры для Freedom Pay Sandbox
    pg_params = {
        'pg_merchant_id': PG_MERCHANT_ID,
        'pg_order_id': str(order.id),
        'pg_amount': f"{order.total_amount:.0f}",
        'pg_description': f'Оплата заказа №{order.id} на сайте Modnoe Mesto',
        'pg_salt': 'random_salt_999',
        'pg_testing_mode': '1',  # ✅ исправлено
        'pg_success_url': request.build_absolute_uri('/orders/payment/success/'),
        'pg_user_contact_email': 'test@test.com',
    }

    # Секретный ключ для Sandbox: Uf89H398S8
    pg_params['pg_sig'] = generate_pg_sig('init_payment.php', pg_params, PG_KEY)



    # АКТУАЛЬНЫЙ URL
    #base_url = "https://api.freedompay.kz/init_payment.php"
    # Собираем итоговую ссылку
    #final_url = f"{base_url}?{urlencode(pg_params)}"
    #return redirect(final_url)
    return render(request, 'orders/pay_redirect.html', {
        'params': pg_params,
        'pay_url': request.build_absolute_uri(reverse('fake_payment', args=[order.id]))
    })
@csrf_exempt
def fake_payment_page(request, order_id):
    # Берем заказ из базы, а не из «летящего» POST. Это надежно на 100%.
    order = get_object_or_404(Order, id=order_id)

    # Принимаем данные, которые прислала форма из pay_redirect
    context = {
        'order': order,
        'pg_order_id': request.POST.get('pg_order_id'),
        'pg_amount': request.POST.get('pg_amount'),
        #'pg_description': request.POST.get('pg_description'),
        'pg_description': f"Оплата заказа №{order.id}"
    }
    return render(request, 'orders/fake_freedom_pay.html', context)

@csrf_exempt
def payment_success_view(request, order_id):
    """Шаг 2: Обработка успешного возврата. Списание остатков и Email."""
    # Сначала пробуем взять из POST (как Freedom),
    # если пусто — берем из сессии или GET как запасной вариант
    #order_id = request.POST.get('pg_order_id') or request.GET.get('pg_order_id')
    # больше не нужно делать request.POST.get, так как ID уже в переменной order_id
    order = get_object_or_404(Order, id=order_id)

    if not order_id:
        return redirect('cart')

    order = get_object_or_404(Order, id=order_id)
    if order.status == 'new':
        # --- ПУНКТ 7: ВЫЧИТАНИЕ ИЗ СКЛАДА ---
        order_details_list = []
        for item in order.items.all():
            # Ищем ProductSize по товару и строковому значению размера
            stock = ProductSize.objects.filter(product=item.product, size=item.size).first()
            if stock:
                stock.quantity = max(0, stock.quantity - item.quantity)
                stock.save()
            order_details_list.append(f"{item.product.name} (Размер: {item.size}) x{item.quantity}")

        # Обновляем статус
        order.status = 'paid'
        order.save()

        # --- ПУНКТ 6: ОТПРАВКА EMAIL АДМИНУ И ЮЗЕРУ ---
        message_body = f"""
        Ура! Новый оплаченный заказ №{order.id}

        Данные доставки:
        Город: {order.city}
        Адрес: {order.address}
        Телефон: {order.phone}

        Состав заказа:
        {chr(10).join(order_details_list)}

        Сумма к оплате: {order.total_amount} тг.
        """

        send_mail(
            f'Заказ №{order.id} оплачен успешно',
            message_body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL, order.user.email],
            fail_silently=True
        )

        # Очистка
        clear_cart_session(request)
        request.session['coupon_id'] = None

    return render(request, 'orders/success.html', {'order': order})
