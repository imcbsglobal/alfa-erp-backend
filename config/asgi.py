"""
ASGI config for alfa_erp_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Default to development locally; production deployments should set DJANGO_SETTINGS_MODULE explicitly.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Initialize Django ASGI application (let Django routing handle SSE view)
application = get_asgi_application()
