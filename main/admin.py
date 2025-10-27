from django.contrib import admin
from .models import Warehouse

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'user')  # Поля, которые будут отображаться в списке
    list_filter = ('user',)  # Фильтры по полям
    search_fields = ('name', 'address')  # Поля для поиска
    ordering = ('name',)  # Сортировка по умолчанию
