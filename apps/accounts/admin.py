"""
Admin configuration for accounts app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Department, JobTitle

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    
    list_display = ['email', 'first_name', 'last_name', 'role', 'department', 'job_title', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'role', 'department', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Organization', {'fields': ('department', 'job_title')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Tracking', {'fields': ('created_by',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'department', 'job_title', 'role', 'is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']


class JobTitleInline(admin.TabularInline):
    """Inline admin for JobTitle under Department"""
    model = JobTitle
    extra = 1
    fields = ['title', 'description', 'is_active']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin for Department model"""
    list_display = ['name', 'is_active', 'get_job_titles_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    inlines = [JobTitleInline]
    
    def get_job_titles_count(self, obj):
        """Display count of job titles"""
        return obj.job_titles.count()
    get_job_titles_count.short_description = 'Job Titles'


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    """Admin for JobTitle model"""
    list_display = ['title', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['title', 'description', 'department__name']
    ordering = ['department', 'title']
