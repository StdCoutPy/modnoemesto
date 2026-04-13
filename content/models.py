from django.db import models



class Lookbook(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class LookbookImage(models.Model):
    lookbook = models.ForeignKey(
        Lookbook,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="lookbooks/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
