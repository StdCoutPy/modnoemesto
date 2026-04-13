from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Модель категорий с древовидной структурой"""
    name = models.CharField("Название", max_length=100)
    name_en = models.CharField("Оригинальное название", max_length=100, blank=True)
    slug = models.SlugField("URL-адрес", max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        verbose_name="Родительская категория",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    order = models.IntegerField("Порядок отображения", default=0)
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(models.Model):
    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField(
        "Цена",
        max_digits=8,
        decimal_places=2,
        null=True,  # Позволяет хранить NULL в базе данных
        blank=True  # Позволяет оставлять поле пустым в формах/админке
    )
    # ЗАМЕНЯЕМ старое поле category на связь ManyToMany
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    # Добавляем новые поля для фильтрации
    is_new = models.BooleanField("Новинка", default=False)
    is_discounted = models.BooleanField("Со скидкой", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def sizes(self):
        """Возвращает все объекты ProductSize для этого товара"""
        return self.available_sizes.all()
    def has_sizes(self):
        """Проверяет, есть ли у товара размеры"""
        return self.available_sizes.exists()

    def __str__(self):
        return self.name

    # Сохраняем старое поле category для обратной совместимости (опционально)
    @property
    def category(self):
        """Для обратной совместимости с существующими шаблонами"""
        first_category = self.categories.first()
        return first_category.name if first_category else ""



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField("Изображение", upload_to="products/")
    is_main = models.BooleanField("Основное", default=False)



    def __str__(self):
        return f"Image for {self.product.name}"







# models.py
class ProductSize(models.Model):
    # Список доступных вариантов
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('ONE SIZE', 'ONE SIZE'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='available_sizes')
    # Добавляем choices=SIZE_CHOICES
    size = models.CharField("Размер", max_length=20, choices=SIZE_CHOICES)
    quantity = models.PositiveIntegerField("Количество", default=0)
    size_order = models.IntegerField("Порядок сортировки", default=0)

    class Meta:
        verbose_name = "Размер товара"
        verbose_name_plural = "Размеры товаров"
        ordering = ['size_order', 'size']  # Сортировка по порядку и размеру

    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.quantity} шт.)"

    def is_available(self):
        """Проверка доступности размера"""
        return self.quantity > 0

    @property
    def availability_status(self):
        """Текстовый статус доступности"""
        if self.quantity > 10:
            return "Много"
        elif self.quantity > 0:
            return f"Осталось {self.quantity} шт."
        else:
            return "Нет в наличии"
