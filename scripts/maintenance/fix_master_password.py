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

def fix_master_password():
    print("=== Fixing Master Admin Password ===")
    
    try:
        # Find master admin user
        master_user = CustomUser.objects.filter(admin_type='master').first()
        
        if not master_user:
            print("No master admin found!")
            return
        
        print(f"Found master admin: {master_user.username}")
        
        # Set a known password
        new_password = "admin123"
        master_user.set_password(new_password)
        master_user.is_active = True
        master_user.save()
        
        print(f"✅ Password reset successfully!")
        print(f"Username: {master_user.username}")
        print(f"Password: {new_password}")
        
        # Test the password
        if master_user.check_password(new_password):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    fix_master_password()