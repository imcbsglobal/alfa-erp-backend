"""
Django settings initialization.
"""
import os

# Determine which settings to use based on environment variable
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    from .development import *
