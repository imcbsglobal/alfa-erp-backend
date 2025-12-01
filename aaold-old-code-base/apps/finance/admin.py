"""
Finance admin configuration.
"""
from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_number', 'account_type', 'balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'created_at']
    search_fields = ['name', 'account_number']
