#!/usr/bin/env python3
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/var/www/athens/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser

def test_user_credentials():
    print("=== Testing User Credentials ===")
    
    # Test common usernames
    test_users = ['master', 'admin', 'test', 'superadmin', 'masteradmin']
    test_passwords = ['admin123', 'password', 'master', 'admin', '123456']
    
    print("\nActive users in database:")
    users = CustomUser.objects.filter(is_active=True)
    for user in users[:10]:  # Show first 10 users
        print(f"- {user.username} (Type: {user.user_type}, Admin: {user.admin_type})")
    
    print(f"\nTotal active users: {users.count()}")
    
    # Test specific user credentials
    for username in test_users:
        try:
            user = CustomUser.objects.get(username=username, is_active=True)
            print(f"\n✓ Found user: {username}")
            print(f"  - User type: {user.user_type}")
            print(f"  - Admin type: {user.admin_type}")
            print(f"  - Is active: {user.is_active}")
            
            # Test passwords
            for password in test_passwords:
                if user.check_password(password):
                    print(f"  ✅ Password '{password}' works!")
                    break
            else:
                print(f"  ❌ None of the test passwords work")
                
        except CustomUser.DoesNotExist:
            print(f"✗ User '{username}' not found")

if __name__ == '__main__':
    test_user_credentials()