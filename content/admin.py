from django.contrib import admin
from .models import Lookbook, LookbookImage
from django.utils.html import format_html


class LookbookImageInline(admin.TabularInline):
    model = LookbookImage
    extra = 1


@admin.register(Lookbook)
class LookbookAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [LookbookImageInline]


