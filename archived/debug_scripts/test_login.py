#!/usr/bin/env python
import os
import django
import requests

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser

# Test database connection
try:
    user_count = CustomUser.objects.count()
    print(f"Database connection OK - {user_count} users found")
except Exception as e:
    print(f"Database error: {e}")

# Test login endpoint
try:
    response = requests.post('http://localhost:8000/authentication/login/', 
                           json={'username': 'ilaiaraja', 'password': 'admin123'})
    print(f"Login test - Status: {response.status_code}")
    if response.status_code == 200:
        print("Login successful!")
    else:
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Login endpoint error: {e}")