"""
Production settings for ALFA ERP Backend
"""
from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS - production should have specific origins
CORS_ALLOW_ALL_ORIGINS = False

# Get allowed hosts from environment
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
