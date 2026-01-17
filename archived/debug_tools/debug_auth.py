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

def debug_auth():
    print("=== Authentication Debug ===")
    
    # Check master admin
    try:
        master = CustomUser.objects.get(username='master')
        print(f"✅ Master admin found:")
        print(f"   - Username: {master.username}")
        print(f"   - User Type: {master.user_type}")
        print(f"   - Admin Type: {master.admin_type}")
        print(f"   - Is Active: {master.is_active}")
        print(f"   - Project: {master.project}")
        print(f"   - Company Name: {master.company_name}")
        print(f"   - Department: {getattr(master, 'department', 'N/A')}")
        print(f"   - Grade: {getattr(master, 'grade', 'N/A')}")
        
        # Test password
        if master.check_password('admin123'):
            print("   - Password 'admin123': ✅ CORRECT")
        else:
            print("   - Password 'admin123': ❌ INCORRECT")
            # Reset password
            master.set_password('admin123')
            master.save()
            print("   - Password reset to 'admin123': ✅ DONE")
            
    except CustomUser.DoesNotExist:
        print("❌ Master admin not found")
        
        # Create master admin
        master = CustomUser.objects.create_user(
            username='master',
            password='admin123',
            user_type='master',
            admin_type='master',
            is_active=True,
            company_name='Athens EHS'
        )
        print("✅ Master admin created with password 'admin123'")
    
    # Check all users
    print(f"\n=== All Users ===")
    users = CustomUser.objects.all()
    for user in users:
        print(f"- {user.username}: {user.user_type}/{user.admin_type} (Active: {user.is_active})")

if __name__ == '__main__':
    debug_auth()