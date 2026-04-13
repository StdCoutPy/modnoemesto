
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Category, ProductSize


# --- Вставляем Инлайны ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    max_num = 7
    fields = ('image', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "Нет изображения"

    image_preview.short_description = "Предпросмотр"


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 7  # Поставим 7, чтобы сразу видеть все стандартные размеры при создании
    max_num = 30
    fields = ('size', 'quantity', 'size_order', 'availability_status')
    readonly_fields = ('availability_status',)
    ordering = ('size_order', 'size')

    def availability_status(self, obj):
        # Проверка на существование объекта (для пустых строк в extra)
        if not obj or not obj.id:
            return "-"
        if obj.quantity == 0:
            return format_html('<span style="color:red;">Нет в наличии</span>')
        elif obj.quantity <= 5:
            return format_html('<span style="color:orange;">Осталось {}</span>', obj.quantity)
        else:
            return format_html('<span style="color:green;">В наличии</span>')

    availability_status.short_description = "Статус"


# --- Настройка Категорий ---
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'order', 'is_active', 'product_count']
    list_filter = ['parent', 'is_active']
    search_fields = ['name', 'name_en']
    list_editable = ['order', 'is_active']

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Товаров'


# --- Настройка Товаров ---
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_new', 'is_discounted', 'created_at', 'category_list', 'has_sizes']
    list_filter = ['is_new', 'is_discounted', 'categories', 'created_at']
    filter_horizontal = ['categories']
    inlines = [ProductSizeInline, ProductImageInline]
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Основная информация', {'fields': ('name', 'description', 'price')}),
        ('Категории', {'fields': ('categories',)}),
        ('Флаги', {'fields': ('is_new', 'is_discounted'), 'classes': ('collapse',)}),
        ('Даты', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def category_list(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])

    category_list.short_description = 'Категории'

    def has_sizes(self, obj):
        return obj.available_sizes.exists()

    has_sizes.boolean = True
    has_sizes.short_description = 'Размеры'


# --- Настройка Размеров ---
@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ['product_link', 'size', 'quantity', 'size_order', 'is_available_display']
    list_editable = ['size', 'quantity', 'size_order']
    list_filter = ['product__categories', 'product__is_new']
    search_fields = ['product__name', 'size']

    def product_link(self, obj):
        # ВНИМАНИЕ: Изменили main на products в пути
        return format_html('<a href="/admin/products/product/{}/change/">{}</a>',
                           obj.product.id, obj.product.name)

    product_link.short_description = 'Товар'

    def is_available_display(self, obj):
        if obj.is_available():
            return format_html('<span style="color:green;">✓ Доступно ({} шт.)</span>', obj.quantity)
        return format_html('<span style="color:red;">✗ Нет в наличии</span>')

    is_available_display.short_description = 'Наличие'

    @admin.action(description="Установить количество = 0")
    def set_zero_quantity(self, request, queryset):
        queryset.update(quantity=0)

    @admin.action(description="Установить количество = 10")
    def set_default_quantity(self, request, queryset):
        queryset.update(quantity=10)

    actions = [set_zero_quantity, set_default_quantity]


# --- Регистрация ---
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
