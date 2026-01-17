#!/usr/bin/env python3
import os
import sys
import django

sys.path.append('/var/www/athens/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser

def create_simple_test_user():
    print("=== Creating Simple Test User ===")
    
    username = "testuser123"
    password = "password123"
    
    # Delete if exists
    CustomUser.objects.filter(username=username).delete()
    
    # Create new user
    user = CustomUser.objects.create_user(
        username=username,
        password=password,
        user_type='master',
        admin_type='master',
        is_active=True
    )
    
    print(f"✅ Created user: {username}")
    print(f"✅ Password: {password}")
    
    # Verify
    if user.check_password(password):
        print("✅ Password verification successful")
    else:
        print("❌ Password verification failed")
    
    print(f"\n🔑 Try logging in with:")
    print(f"Username: {username}")
    print(f"Password: {password}")

if __name__ == '__main__':
    create_simple_test_user()