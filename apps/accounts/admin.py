"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import JobTitle, Department,Courier

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = ['email', 'name', 'role', 'department', 'job_title', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'role', 'date_joined']
    search_fields = ['email', 'name', 'department__name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'avatar')}),
        ('Organization', {'fields': ('department', 'job_title')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Tracking', {'fields': ('created_by',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'department', 'job_title', 'role', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    """Admin for JobTitle model"""
    list_display = ['title', 'department', 'is_active', 'created_at']
    list_filter = ['department', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'department__name']
    ordering = ['department', 'title']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin for Department model"""
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

# Add this at the end of admin.py
@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    """Admin for Courier model"""
    list_display = [
        'courier_code', 
        'courier_name', 
        'type', 
        'contact_person', 
        'phone', 
        'status',
        'cod_supported',
        'created_at'
    ]
    list_filter = ['type', 'status', 'cod_supported', 'rate_type', 'created_at']
    search_fields = ['courier_code', 'courier_name', 'contact_person', 'phone', 'email']
    readonly_fields = ['courier_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('courier_id', 'courier_code', 'courier_name', 'type', 'status')
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'phone', 'alt_phone', 'email', 'address')
        }),
        ('Service Details', {
            'fields': ('service_area', 'vehicle_type', 'max_weight', 'cod_supported')
        }),
        ('Pricing', {
            'fields': ('rate_type', 'base_rate')
        }),
        ('Additional Information', {
            'fields': ('remarks', 'created_at', 'updated_at')
        }),
    )
    
    ordering = ['-created_at']