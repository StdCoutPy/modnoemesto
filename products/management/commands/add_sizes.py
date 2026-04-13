from django.core.management.base import BaseCommand
from django.db import transaction
from products.models import Product, ProductSize, Category


class Command(BaseCommand):
    help = 'Добавляет размеры к товарам на основе их категорий'

    # Пресеты размеров для разных типов товаров
    SIZE_PRESETS = {
        'одежда': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
        'обувь': ['36', '37', '38', '39', '40', '41', '42', '43', '44'],
        'головные уборы': ['S (55-56)', 'M (57-58)', 'L (59-60)', 'XL (61-62)'],
        'аксессуары': ['ONE SIZE'],
        'по умолчанию': ['UNIVERSAL']
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--preset',
            type=str,
            choices=list(self.SIZE_PRESETS.keys()),
            default='по умолчанию',
            help='Пресет размеров для добавления'
        )
        parser.add_argument(
            '--quantity',
            type=int,
            default=10,
            help='Количество каждого размера'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано без сохранения'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Добавить размеры даже если они уже есть'
        )

    def handle(self, *args, **options):
        preset_name = options['preset']
        quantity = options['quantity']
        dry_run = options['dry_run']
        force = options['force']

        sizes = self.SIZE_PRESETS.get(preset_name, self.SIZE_PRESETS['по умолчанию'])

        # Определяем какие товары обрабатывать
        products = Product.objects.all()

        if preset_name in ['одежда', 'обувь', 'головные уборы']:
            # Ищем товары в соответствующих категориях
            category_names = {
                'одежда': ['Одежда', 'Футболки', 'Рубашки', 'Джинсы'],
                'обувь': ['Обувь', 'Кроссовки', 'Туфли'],
                'головные уборы': ['Головные уборы', 'Кепки', 'Шапки']
            }
            products = products.filter(
                categories__name__in=category_names.get(preset_name, [])
            ).distinct()

        self.stdout.write(f'Пресет: {preset_name}')
        self.stdout.write(f'Размеры: {", ".join(sizes)}')
        self.stdout.write(f'Количество каждого: {quantity}')
        self.stdout.write(f'Товаров для обработки: {products.count()}')

        if dry_run:
            self.stdout.write(self.style.WARNING('РЕЖИМ ПРОСМОТРА (dry-run) - изменения не сохранятся'))

        added_total = 0

        with transaction.atomic():
            for i, product in enumerate(products, 1):
                # Проверяем существующие размеры
                existing_sizes = set(product.available_sizes.values_list('size', flat=True))

                sizes_to_add = []
                for order, size in enumerate(sizes):
                    if force or size not in existing_sizes:
                        sizes_to_add.append(
                            ProductSize(
                                product=product,
                                size=size,
                                quantity=quantity,
                                size_order=order
                            )
                        )

                if sizes_to_add:
                    if not dry_run:
                        ProductSize.objects.bulk_create(sizes_to_add)

                    added_total += len(sizes_to_add)
                    self.stdout.write(
                        f'{i}. К товару "{product.name}" добавлено {len(sizes_to_add)} размеров'
                    )
                else:
                    self.stdout.write(f'{i}. У товара "{product.name}" все размеры уже есть')

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'\nВ режиме просмотра. Было бы добавлено: {added_total} размеров'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\nГотово! Добавлено {added_total} размеров к {products.count()} товарам'
            ))