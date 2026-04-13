from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Полная очистка таблицы категорий'

    def handle(self, *args, **options):
        # Считаем количество перед удалением для отчета
        count = Category.objects.count()

        # Удаляем все записи
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS(f'Успешно удалено категорий: {count}'))
