"""
Inventory models.
Add your product, stock, warehouse models here.
"""
from django.db import models
from apps.common.models import BaseModel


class Product(BaseModel):
    """Product model for inventory management."""
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    
    class Meta:
        db_table = 'inventory_products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
