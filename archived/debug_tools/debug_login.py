#!/usr/bin/env python3
import os
import sys
import django

sys.path.append('/var/www/athens/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser
from authentication.serializers import CustomTokenObtainPairSerializer

def debug_login():
    print("=== Debug Login Issue ===")
    
    # Test credentials
    test_creds = [
        ('master', 'admin123'),
        ('admin', 'admin123'),
        ('test', 'admin123')
    ]
    
    for username, password in test_creds:
        print(f"\nTesting: {username} / {password}")
        
        try:
            user = CustomUser.objects.get(username=username)
            print(f"  ✓ User found: {user.username}")
            print(f"  - Active: {user.is_active}")
            print(f"  - Type: {user.user_type}")
            print(f"  - Admin: {user.admin_type}")
            
            # Test password
            if user.check_password(password):
                print(f"  ✅ Password correct")
                
                # Test serializer
                serializer = CustomTokenObtainPairSerializer(data={
                    'username': username,
                    'password': password
                })
                
                if serializer.is_valid():
                    print(f"  ✅ Serializer valid - tokens generated")
                else:
                    print(f"  ❌ Serializer invalid: {serializer.errors}")
                    
            else:
                print(f"  ❌ Password incorrect")
                
        except CustomUser.DoesNotExist:
            print(f"  ❌ User not found")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == '__main__':
    debug_login()