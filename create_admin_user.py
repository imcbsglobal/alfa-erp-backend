#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if user exists
if User.objects.filter(email='admin@gmail.com').exists():
    user = User.objects.get(email='admin@gmail.com')
    print(f"User already exists: {user.email}")
else:
    # Create superuser
    user = User.objects.create_superuser(
        email='admin@gmail.com',
        password='admin@123'
    )
    print(f"Created superuser: {user.email}")

# Verify login will work
print(f"Password check: {user.check_password('admin@123')}")
print(f"Is active: {user.is_active}")
print(f"Is superuser: {user.is_superuser}")
