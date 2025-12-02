"""
Production settings for ALFA ERP Backend
"""
from .base import *
import os

DEBUG = False

# Allowed hosts from environment (comma separated string)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Security Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS - production should have specific origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
