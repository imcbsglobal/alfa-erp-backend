"""
Development settings for ALFA ERP Backend
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Development CORS - allow all origins
CORS_ALLOW_ALL_ORIGINS = True
