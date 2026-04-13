#!/usr/bin/env python
"""
Тестовый скрипт для проверки корзины
Запуск: python test_cart.py
"""

import os
import django
import sys

# 1. Добавляем путь к проекту
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# 2. Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

# 3. Инициализируем Django
django.setup()

print("=" * 60)
print("ТЕСТИРОВАНИЕ СИСТЕМЫ КОРЗИНЫ")
print("=" * 60)

from products.models import Product, ProductSize, Category

# Тест 1: Проверка моделей
print("\n1. ПРОВЕРКА МОДЕЛЕЙ:")
print("-" * 30)

# Создаем тестовую категорию
category, created = Category.objects.get_or_create(
    name="Тестовая категория",
    slug="test-category",
    defaults={'is_active': True}
)
print(f"Категория: {category.name} ({'создана' if created else 'уже есть'})")

# Создаем тестовый товар
product, created = Product.objects.get_or_create(
    name="Тестовый товар для корзины",
    defaults={
        'description': 'Тестовое описание товара',
        'price': 1999.99,
    }
)
product.categories.add(category)
print(f"Товар: {product.name} ({'создан' if created else 'уже есть'})")

# Создаем размеры для товара
sizes_data = ['S', 'M', 'L', 'XL']
for size_name in sizes_data:
    size_obj, created = ProductSize.objects.get_or_create(
        product=product,
        size=size_name,
        defaults={'quantity': 10}
    )
    print(f"  Размер {size_name}: {size_obj.quantity} шт. ({'создан' if created else 'уже есть'})")

# Тест 2: Проверка функций корзины
print("\n2. ПРОВЕРКА ФУНКЦИЙ КОРЗИНЫ:")
print("-" * 30)

# Имитируем request с сессией
class MockRequest:
    def __init__(self):
        self.session = {}
        self.method = 'GET'

request = MockRequest()

from orders.cart_utils import get_cart, add_to_cart_session, get_cart_summary

# Проверяем создание корзины
cart = get_cart(request)
print(f"Корзина создана: {'items' in cart}")
print(f"Корзина пуста: {len(cart['items']) == 0}")

# Добавляем товар в корзину
test_size = product.sizes.first()
success, message = add_to_cart_session(
    request,
    product.id,
    test_size.id if test_size else None,
    2
)
print(f"\nДобавление товара в корзину:")
print(f"  Успех: {success}")
print(f"  Сообщение: {message}")
print(f"  Товаров в корзине: {len(cart['items'])}")

# Проверяем общую сумму
cart_summary = get_cart_summary(request)
print(f"\nОбщая информация корзины:")
print(f"  Общее количество: {cart_summary['total_quantity']}")
print(f"  Общая сумма: {cart_summary['total_price']} ₽")

# Тест 3: Проверка цен
print("\n3. ПРОВЕРКА РАСЧЕТОВ:")
print("-" * 30)
print(f"Цена товара: {product.price} ₽")
print(f"Количество в корзине: {cart_summary['total_quantity']}")
print(f"Ожидаемая сумма: {product.price * cart_summary['total_quantity']} ₽")
print(f"Фактическая сумма: {cart_summary['total_price']} ₽")

# Проверяем правильность расчета
expected_total = float(product.price * cart_summary['total_quantity'])
actual_total = cart_summary['total_price']
calculation_correct = abs(expected_total - actual_total) < 0.01
print(f"Расчет верный: {calculation_correct}")

print("\n" + "=" * 60)
print("ТЕСТ ЗАВЕРШЕН")
print("=" * 60)

# Инструкция для ручного тестирования
print("\n📋 ИНСТРУКЦИЯ ДЛЯ РУЧНОГО ТЕСТИРОВАНИЯ:")
print("1. Запустите сервер: python manage.py runserver")
print("2. Откройте в браузере:")
print(f"   - Страница товара: http://127.0.0.1:8000/product/{product.id}/")
print("   - Корзина: http://127.0.0.1:8000/cart/")
print("3. Проверьте добавление товара в корзину")
print("4. Проверьте обновление количества")
print("5. Проверьте удаление товара")

# Проверка URL-адресов
print("\n🔗 ПРОВЕРКА URL-АДРЕСОВ:")
urls_to_check = [
    ('cart/', 'Страница корзины'),
    (f'product/{product.id}/', 'Страница товара'),
    (f'cart/add/{product.id}/', 'Добавление в корзину'),
]

from django.urls import reverse, NoReverseMatch
for url_name, description in urls_to_check:
    try:
        # Пытаемся получить URL по имени
        if url_name == 'cart/':
            reverse('cart')
        elif url_name.startswith('product/'):
            reverse('product_detail', args=[product.id])
        elif url_name.startswith('cart/add/'):
            reverse('add_to_cart', args=[product.id])
        print(f"✅ {description}: OK")
    except NoReverseMatch as e:
        print(f"❌ {description}: Ошибка - {e}")
    except Exception as e:
        print(f"⚠️ {description}: Предупреждение - {e}")