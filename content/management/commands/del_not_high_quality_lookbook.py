import os
from django.core.management.base import BaseCommand
from content.models import Lookbook, LookbookImage


class Command(BaseCommand):
    help = 'Удаляет фото низкого качества в определенной категории'

    def handle(self, *args, **options):
        lookbook_name = "Grizas Precollection Aw25 Campaign"
        min_width = 800
        min_height = 600

        # 1. Get the specific Lookbook first
        try:
            target_lookbook = Lookbook.objects.get(name=lookbook_name)
        except Lookbook.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Lookbook '{lookbook_name}' not found."))
            return

        # 2. Get all images for THIS lookbook
        # We use .images.all() because 'images' is your related_name
        photos = target_lookbook.images.all()

        deleted_count = 0
        for photo_obj in photos:
            try:
                # 'photo_obj' is a LookbookImage instance
                # 'photo_obj.image' is the ImageField
                if photo_obj.image.width < min_width or photo_obj.image.height < min_height:
                    image_path = photo_obj.image.path

                    # Store ID for logging
                    p_id = photo_obj.id

                    # Delete from DB
                    photo_obj.delete()

                    # Delete from Disk
                    if os.path.exists(image_path):
                        os.remove(image_path)

                    deleted_count += 1
                    self.stdout.write(f"Deleted photo ID {p_id} (Low quality)")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing image {photo_obj.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} images."))
