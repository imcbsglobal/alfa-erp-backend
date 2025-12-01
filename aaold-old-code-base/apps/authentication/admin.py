"""
Admin configuration for authentication models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role, UserSession


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for Role model."""
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'created_at'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'roles', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['last_login', 'created_at', 'updated_at', 'last_login_ip']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Roles', {
            'fields': ('roles',)
        }),
        ('Security', {
            'fields': ('last_login', 'last_login_ip', 'failed_login_attempts')
        }),
        ('Important dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'is_staff', 'is_active'
            ),
        }),
    )
    
    filter_horizontal = ['groups', 'user_permissions', 'roles']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for UserSession model."""
    list_display = [
        'user', 'ip_address', 'is_active',
        'expires_at', 'created_at'
    ]
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
