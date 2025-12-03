"""
Admin interface for Access Control - Direct User-to-Menu Assignment
"""
from django.contrib import admin
from .models import MenuItem, UserMenu


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'url', 'parent', 'order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code', 'url']
    ordering = ['order', 'name']


@admin.register(UserMenu)
class UserMenuAdmin(admin.ModelAdmin):
    list_display = ['user', 'menu', 'is_active', 'assigned_by', 'assigned_at']
    list_filter = ['is_active', 'menu', 'assigned_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'menu__name']
    autocomplete_fields = ['user', 'assigned_by']
    date_hierarchy = 'assigned_at'
    ordering = ['-assigned_at']
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('user', 'menu', 'assigned_by')
