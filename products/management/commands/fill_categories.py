from django.core.management.base import BaseCommand
from products.models import Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Заполнение упрощенных категорий'

    def handle(self, *args, **options):
        # Очищаем старые данные перед заполнением (опционально)
        # Category.objects.all().delete()

        # 1. Основные разделы (Родители)
        main_categories = [
            {'name': 'НОВИНКИ', 'slug': 'new', 'order': 1},
            {'name': 'ОДЕЖДА', 'slug': 'clothing', 'order': 2},
            {'name': 'АКСЕССУАРЫ', 'slug': 'accessories', 'order': 3},
            {'name': 'СМОТРЕТЬ ВСЁ', 'slug': 'shop-all', 'order': 5},
            {'name': 'СКИДКИ', 'slug': 'sale', 'order': 4},
        ]

        # 2. Подкатегории для ОДЕЖДЫ (Объединенные)
        clothing_subs = [
            {'name': 'Верхняя одежда', 'slug': 'outerwear'},  # Coats, Jackets
            {'name': 'Платья и комбинезоны', 'slug': 'dresses-jumpsuits'},
            {'name': 'Трикотаж и худи', 'slug': 'knitwear-hoodies'},  # Sweaters, Cardigans, Pullovers
            {'name': 'Топы, футболки и рубашки', 'slug': 'tops-tshirts'},  # Blouses, Shirts
            {'name': 'Брюки и джинсы', 'slug': 'trousers-denim'},  # Leggings
            {'name': 'Юбки и шорты', 'slug': 'skirts-shorts'},

        ]

        # 3. Подкатегории для АКСЕССУАРОВ
        acc_subs = [
            {'name': 'Сумки', 'slug': 'bags'},
            {'name': 'Обувь', 'slug': 'shoes'},
            {'name': 'Головные уборы', 'slug': 'hats'},
            {'name': 'Украшения', 'slug': 'jewelry'},
            {'name': 'Ремни и кошельки', 'slug': 'belts-wallets'},

        ]


        # Функция для создания
        def create_cats(data, parent=None):
            for item in data:
                cat, created = Category.objects.update_or_create(
                    slug=item['slug'],
                    defaults={
                        'name': item['name'],
                        'parent': parent,
                        'order': item.get('order', 0)
                    }
                )
                status = "Создана" if created else "Обновлена"
                self.stdout.write(f"{status}: {cat.name}")

        # Запуск создания
        create_cats(main_categories)

        # Привязываем подкатегории
        clothing_parent = Category.objects.get(slug='clothing')
        create_cats(clothing_subs, parent=clothing_parent)

        acc_parent = Category.objects.get(slug='accessories')
        create_cats(acc_subs, parent=acc_parent)



        self.stdout.write(self.style.SUCCESS('Категории успешно обновлены!'))
