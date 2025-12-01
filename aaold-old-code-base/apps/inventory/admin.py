"""
Inventory admin configuration.
"""
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'unit_price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'sku']
