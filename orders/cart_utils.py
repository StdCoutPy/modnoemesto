from django.utils import timezone
from products.models import Product, ProductSize
from decimal import Decimal


def get_cart(request):
    """Получить корзину из сессии или создать новую"""
    if 'cart' not in request.session:
        request.session['cart'] = {
            'items': [],
            'total_price': 0,
            'total_quantity': 0,
            'created_at': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat()
        }
    return request.session['cart']


def save_cart(request, cart):
    """Сохранить корзину в сессию"""
    request.session['cart'] = cart
    request.session.modified = True


def remove_from_cart_session(request, product_id, size_id=None):
    """Удалить товар из корзины"""
    cart = get_cart(request)

    # Ищем товар для удаления
    for i, item in enumerate(cart['items']):
        if item['product_id'] == product_id and item['size_id'] == size_id:
            del cart['items'][i]
            update_cart_totals(cart)
            save_cart(request, cart)
            return True, 'Товар удален из корзины'

    return False, 'Товар не найден в корзине'


def update_cart_totals(cart):
    """Обновить общие суммы и количество в корзине"""
    total_price = Decimal('0')
    total_quantity = 0

    for item in cart['items']:
        try:
            product = Product.objects.get(id=item['product_id'])
            total_price += product.price * item['quantity']
            total_quantity += item['quantity']
        except Product.DoesNotExist:
            # Если товар удален из БД, удаляем его из корзины
            cart['items'].remove(item)

    cart['total_price'] = float(total_price)  # Для сериализации в JSON
    cart['total_quantity'] = total_quantity
    cart['updated_at'] = timezone.now().isoformat()

def get_cart_items_with_details(request):
    """Получить товары в корзине с полной информацией о товарах"""
    cart = get_cart(request)
    items_with_details = []
    for item in cart['items']:
        try:
            product = Product.objects.get(id=item['product_id'])
            # Получаем размер, если указан
            # Получаем размер, если указан
            size = None
            size_obj = None

            # ВАЖНО: проверяем, что size_id не None и не пустой
            current_size_id = item.get('size_id')

            if current_size_id is not None:
                try:
                    size_obj = ProductSize.objects.get(id=current_size_id)
                    size = size_obj.size
                except (ProductSize.DoesNotExist, ValueError):
                    size = None
                    size_obj = None

            # Проверяем доступность размера
            is_available = True
            # Если размер должен быть, но его нет в базе или количество 0
            if size_obj:
                if item['quantity'] > size_obj.quantity:
                    is_available = False
            elif item.get('size_id') is not None:
                # Если ID размера был, но объект не найден
                is_available = False

            items_with_details.append({
                'item': item,
                'product': product,
                'size': size,  # строковое значение размера
                'size_obj': size_obj,  # объект размера или None
                'item_total': product.price * item['quantity'],
                'is_available': is_available,
                'max_quantity': size_obj.quantity if size_obj else 999
            })
        except Product.DoesNotExist:
            continue

    return items_with_details
def add_to_cart_session(request, product_id, size_id=None, quantity=1):
    """Добавить товар в корзину (сессии) с проверкой доступности"""
    cart = get_cart(request)

    # Проверяем доступность товара и размера
    try:
        product = Product.objects.get(id=product_id)

        # Если у товара есть размеры, но размер не выбран
        if product.available_sizes.exists() and not size_id:
            return False, 'Для этого товара нужно выбрать размер'

        # Проверяем размер, если указан
        size_obj = None
        if size_id:
            try:
                size_obj = ProductSize.objects.get(id=size_id, product=product)
                if size_obj.quantity < quantity:
                    return False, f'Недостаточно товара. Доступно: {size_obj.quantity} шт.'
            except ProductSize.DoesNotExist:
                return False, 'Выбранный размер недоступен'
    except Product.DoesNotExist:
        return False, 'Товар не найден'

    # Проверяем, есть ли уже такой товар с таким размером
    for item in cart['items']:
        if item['product_id'] == product_id and item['size_id'] == size_id:
            # Проверяем, не превысит ли новое количество доступное
            if size_obj and (item['quantity'] + quantity) > size_obj.quantity:
                available = size_obj.quantity - item['quantity']
                return False, f'Можно добавить только {available} шт.'

            # Увеличиваем количество
            item['quantity'] += quantity
            item['updated_at'] = timezone.now().isoformat()
            update_cart_totals(cart)
            save_cart(request, cart)
            return True, 'Количество обновлено'

    # Если товара еще нет в корзине
    new_item = {
        'product_id': product_id,
        'size_id': size_id,
        'quantity': quantity,
        'added_at': timezone.now().isoformat(),
        'updated_at': timezone.now().isoformat()
    }

    cart['items'].append(new_item)
    update_cart_totals(cart)
    save_cart(request, cart)
    return True, 'Товар добавлен в корзину'

def clear_cart_session(request):
    """Очистить корзину"""
    request.session['cart'] = {
        'items': [],
        'total_price': 0,
        'total_quantity': 0,
        'created_at': timezone.now().isoformat(),
        'updated_at': timezone.now().isoformat()
    }
    request.session.modified = True


def get_cart_summary(request):
    """Получить сводку корзины (для шапки сайта)"""
    cart = get_cart(request)
    return {
        'total_quantity': cart['total_quantity'],
        'total_price': cart['total_price']
    }