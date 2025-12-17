#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser

def create_master_admin():
    try:
        # Check if master admin already exists
        if CustomUser.objects.filter(username='master').exists():
            print("Master admin already exists!")
            user = CustomUser.objects.get(username='master')
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            return
        
        # Create master admin
        user = CustomUser.objects.create_user(
            username='master',
            password='master@123',
            email='master@athens.com',
            user_type='MASTER_ADMIN',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print("✅ Master Admin Created Successfully!")
        print(f"Username: {user.username}")
        print(f"Password: master@123")
        print(f"Email: {user.email}")
        print(f"User Type: {user.user_type}")
        
    except Exception as e:
        print(f"❌ Error creating master admin: {e}")

if __name__ == '__main__':
    create_master_admin()