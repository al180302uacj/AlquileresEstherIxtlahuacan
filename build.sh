#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create a superuser with hardcoded values
python << END
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AlquileresEsther.settings')
django.setup()

User = get_user_model()

# Hardcoded superuser credentials
USERNAME = 'guru'
EMAIL = 'guru@gmail.com'
PASSWORD = 'guru1234'

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f"Superuser {USERNAME} created successfully.")
else:
    print(f"Superuser {USERNAME} already exists.")
END
