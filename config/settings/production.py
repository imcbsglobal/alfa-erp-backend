"""
Production settings for ALFA ERP Backend
"""
from .base import *
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

def _required_csv_env(name):
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(f'{name} must be set for production.')
    values = [item.strip() for item in value.split(',') if item.strip()]
    if not values:
        raise ImproperlyConfigured(f'{name} must contain at least one value for production.')
    return values

ALLOWED_HOSTS = _required_csv_env('ALLOWED_HOSTS')

# Security Settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'true').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'https://alfa.imcbs.com',
    'https://www.alfa.imcbs.com',
]

# CORS - production must have specific origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = _required_csv_env('CORS_ALLOWED_ORIGINS')

EVENTSTREAM_ALLOW_ORIGIN = os.getenv('EVENTSTREAM_ALLOW_ORIGIN')
if not EVENTSTREAM_ALLOW_ORIGIN:
    raise ImproperlyConfigured('EVENTSTREAM_ALLOW_ORIGIN must be set for production.')

REDIS_URL = os.getenv('REDIS_URL')
if not REDIS_URL:
    raise ImproperlyConfigured('REDIS_URL must be set for production.')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    }
}
