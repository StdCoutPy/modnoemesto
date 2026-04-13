from products.models import Product
from django.shortcuts import render


def index(request):
    # Можно добавить featured products на главную
    featured_products = Product.objects.filter(is_new=True)[:8]
    return render(request, 'main/index.html', {'featured_products': featured_products})


def about(request):
    return render(request, 'main/about.html')





