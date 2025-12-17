from django.contrib import admin
from .models import Warehouse, Item

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'user') 
    list_filter = ('user',) 
    search_fields = ('name', 'address')  
    ordering = ('name',)  

@admin.register(Item)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'quantity', 'warehouse')
    list_filter = ('warehouse',)
    search_fields = ('name', 'warehouse')
    ordering = ('warehouse',)