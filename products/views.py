from django.shortcuts import render
from .models import Product, Category
from django.shortcuts import render, get_object_or_404

# Create your views here.
def collection(request):
    """Страница коллекций"""
    # Используем те же категории, что и в контекстном процессоре
    return render(request, 'products/collection.html')

def shop(request):
    """Главная страница магазина с фильтрацией"""
    category_slug = request.GET.get('category')
    is_new = request.GET.get('new')
    is_discounted = request.GET.get('sale')

    # Оптимизация: prefetch_related тянет картинки одним запросом
    products = Product.objects.prefetch_related('images').all()

    if category_slug:
        products = products.filter(categories__slug=category_slug)
    if is_new:
        products = products.filter(is_new=True)
    if is_discounted:
        products = products.filter(is_discounted=True)

    # В context передаем только то, что уникально для этой страницы
    return render(request, 'products/shop.html', {
        'products': products,
        'active_category': category_slug,
        'show_new': bool(is_new),
        'show_sale': bool(is_discounted),
    })


def category_detail(request, slug):
    """Товары конкретной категории"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(categories=category).prefetch_related('images')

    return render(request, 'products/shop.html', {
        'category': category,
        'products': products,
        'active_category': slug,
    })


def items(request):
    return render(request, 'products/item.html')


#Страница товара
def product_detail(request, product_id):
    """Карточка товара"""
    # Оптимизация: тянем сразу картинки и размеры
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'available_sizes'),
        id=product_id
    )

    main_image = product.images.filter(is_main=True).first() or product.images.first()
    other_images = product.images.exclude(id=main_image.id) if main_image else []

    # Размеры в наличии
    available_sizes = product.available_sizes.filter(quantity__gt=0)

    # Рекомендации: товары из тех же категорий
    similar_products = Product.objects.filter(
        categories__in=product.categories.all()
    ).exclude(id=product.id).distinct()[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'main_image': main_image,
        'other_images': other_images,
        'available_sizes': available_sizes,
        'similar_products': similar_products,
    })

# Новые views для специальных разделов
def new_arrivals(request):
    """Новинки"""
    products = Product.objects.filter(is_new=True).prefetch_related('images')
    return render(request, 'products/shop.html', {
        'products': products,
        'show_new': True,
    })


def sale(request):
    """Распродажа"""
    products = Product.objects.filter(is_discounted=True).prefetch_related('images')
    return render(request, 'products/shop.html', {
        'products': products,
        'show_sale': True,
    })