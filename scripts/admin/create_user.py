#!/usr/bin/env python3

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/var/www/athens/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user():
    print("=== Creating Test User ===")
    
    try:
        username = "testuser"
        password = "testpassword"
        user_type = "projectadmin" # Add this line
        
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists.")
            # Update password
            user = User.objects.get(username=username)
            user.set_password(password)
            user.user_type = user_type
            user.save()
            print(f"Password for user '{username}' has been updated to '{password}'.")
        else:
            User.objects.create_user(username=username, password=password, user_type=user_type, is_active=True) # Add user_type
            print(f"User '{username}' created with password '{password}'.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_user()