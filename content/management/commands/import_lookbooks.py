import re
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from content.models import Lookbook, LookbookImage


class Command(BaseCommand):
    help = "Import lookbooks from media/lookbooks/<folder_name>/"

    def handle(self, *args, **options):
        base_dir = os.path.join(settings.MEDIA_ROOT, "lookbooks")

        if not os.path.exists(base_dir):
            self.stdout.write(self.style.ERROR("media/lookbooks not found"))
            return

        for folder_name in os.listdir(base_dir):
            lookbook_dir = os.path.join(base_dir, folder_name)

            # Пропускаем файлы и системную папку 'lookbooks'
            if not os.path.isdir(lookbook_dir) or folder_name == "lookbooks":
                continue

            # 1. Генерируем SLUG: всё, что не буквы и не цифры -> '_'
            # [^\w] заменит пробелы, &, точки, тире и т.д. на подчеркивание
            new_slug = re.sub(r'[^\w]+', '_', folder_name).lower().strip('_')

            if Lookbook.objects.filter(slug=new_slug).exists():
                self.stdout.write(f"Skipping '{new_slug}': already exists")
                continue

            # Создаем лукбук: slug — трансформированный, name — как папка
            lookbook = Lookbook.objects.create(
                slug=new_slug,
                name=folder_name
            )

            self.stdout.write(f"Importing new lookbook: {folder_name} as {new_slug}")

            # Собираем изображения
            for index, filename in enumerate(sorted(os.listdir(lookbook_dir))):
                if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                    continue

                full_path = os.path.join(lookbook_dir, filename)

                with open(full_path, "rb") as f:
                    LookbookImage.objects.create(
                        lookbook=lookbook,
                        image=File(f, name=f"{new_slug}/{filename}"),  # Django сам положит в media/lookbooks/lookbooks/
                        order=index
                    )

            # Удаляем исходную папку после завершения импорта
            shutil.rmtree(lookbook_dir)
            self.stdout.write(self.style.SUCCESS(f"Deleted source folder: {lookbook_dir}"))

        self.stdout.write(self.style.SUCCESS("Import finished"))
