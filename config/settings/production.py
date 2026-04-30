"""
Production settings for ALFA ERP Backend
"""
from .base import *
import os

DEBUG = True

# Allowed hosts from environment (comma separated string)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if os.getenv("ALLOWED_HOSTS") else ['*']

# Security Settings
SECURE_SSL_REDIRECT = False  # Set to True if using HTTPS everywhere
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

# CORS - production should have specific origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if os.getenv("CORS_ALLOWED_ORIGINS") else [
    'https://alfa.imcbs.com',
    'https://www.alfa.imcbs.com',
]
