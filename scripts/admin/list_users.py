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

def list_active_users():
    print("=== Active Users ===")
    
    try:
        users = User.objects.filter(is_active=True)
        if not users:
            print("No active users found.")
            return
        
        for user in users:
            print(f"- {user.username}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    list_active_users()
