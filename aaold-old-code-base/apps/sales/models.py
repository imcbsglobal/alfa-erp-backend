"""
Sales models.
Add your order, invoice, customer models here.
"""
from django.db import models
from apps.common.models import BaseModel


class Customer(BaseModel):
    """Customer model for sales management."""
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'sales_customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return self.name
