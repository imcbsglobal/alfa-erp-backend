"""
Access Control app configuration
Menu-based role access control
"""
from django.apps import AppConfig


class AccessControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accesscontrol'
    verbose_name = 'Access Control'
