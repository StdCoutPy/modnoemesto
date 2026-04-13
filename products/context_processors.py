from .models import Category

def categories_menu(request):
    """Добавляет категории в контекст всех шаблонов для хедера и меню"""
    # Подтягиваем коллекции
    collections = Category.objects.filter(
        parent__slug='collections',
        is_active=True
    ).order_by('order')

    # Основные категории (исключаем служебные слаги)
    main_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).exclude(
        slug__in=['collections', 'new', 'sale'] # Senior-way: используем __in для списка
    ).order_by('order')

    return {
        'header_collections': collections,
        'header_main_categories': main_categories,
    }
