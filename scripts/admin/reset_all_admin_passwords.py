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

def reset_common_passwords():
    print("=== Resetting Common Admin Passwords ===")
    
    # Common admin users to reset
    admin_users = [
        'master', 'admin', 'test', 'superadmin', 'masteradmin'
    ]
    
    new_password = 'admin123'
    
    for username in admin_users:
        try:
            user = CustomUser.objects.get(username=username)
            user.set_password(new_password)
            user.is_active = True
            user.save()
            
            print(f"✅ Reset password for '{username}' to '{new_password}'")
            
            # Verify the password works
            if user.check_password(new_password):
                print(f"   ✓ Password verification successful")
            else:
                print(f"   ❌ Password verification failed")
                
        except CustomUser.DoesNotExist:
            print(f"❌ User '{username}' not found")
    
    print(f"\n🔑 All admin users now have password: {new_password}")
    print("You can now login with any of these users:")
    for username in admin_users:
        if CustomUser.objects.filter(username=username).exists():
            print(f"  - Username: {username}, Password: {new_password}")

if __name__ == '__main__':
    reset_common_passwords()