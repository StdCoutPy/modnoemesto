from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmailVerificationToken, PasswordResetToken
from orders.models import Order, OrderItem

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Поля, которые будут видны в списке пользователей
    list_display = ('email', 'username', 'phone', 'email_verified', 'is_staff', 'is_admin','city','address','telegram_id','telegram_verified')
    list_filter = ('email_verified', 'is_staff', 'is_superuser', 'is_admin')

    # Группировка полей при редактировании пользователя
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'email_verified', 'is_admin','city','address','telegram_id','telegram_verified')}),
    )
    # Поля при создании нового пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('email', 'phone', 'email_verified', 'is_admin','city','address','telegram_id','telegram_verified')}),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_valid')
    readonly_fields = ('created_at',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_valid')
    readonly_fields = ('created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Чтобы не было пустых строк для добавления
    readonly_fields = ('product', 'size', 'quantity', 'price')  # Защита от случайного изменения


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Колонки, которые будут видны в списке заказов
    list_display = ('id', 'user', 'city', 'total_amount', 'status', 'created_at')

    # Фильтры справа
    list_filter = ('status', 'created_at', 'city')

    # Поиск по именам, почте и телефону
    search_fields = ('user__email', 'phone', 'city', 'address', 'id')

    # Чтобы товары заказа отображались внутри страницы заказа
    inlines = [OrderItemInline]

    # Возможность быстро сменить статус прямо в списке
    list_editable = ('status',)

# Если OrderItem уже был зарегистрирован просто, удали старую регистрацию
# admin.site.register(OrderItem)