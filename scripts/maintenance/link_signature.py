#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('/var/www/athens/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser, UserDetail, AdminDetail

def link_signature_for_user(user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        print(f"Processing user: {user.username} (ID: {user.id}, Type: {user.user_type})")
        
        # Find the latest signature file for this user
        signature_dir = '/var/www/athens/backend/media/signatures'
        signature_files = [f for f in os.listdir(signature_dir) if f.startswith(f'signature_{user_id}_')]
        
        if not signature_files:
            print(f"No signature files found for user {user_id}")
            return
        
        # Get the latest signature file
        latest_signature = sorted(signature_files)[-1]
        signature_path = f'signatures/{latest_signature}'
        
        print(f"Found signature file: {latest_signature}")
        
        # Create or get user detail based on user type
        if user.user_type == 'adminuser':
            detail, created = UserDetail.objects.get_or_create(user=user)
            detail.signature_template = signature_path
            detail.save()
            print(f"UserDetail {'created' if created else 'updated'} with signature: {detail.signature_template.url}")
            
        elif user.user_type == 'projectadmin':
            detail, created = AdminDetail.objects.get_or_create(user=user)
            detail.signature_template = signature_path
            detail.save()
            print(f"AdminDetail {'created' if created else 'updated'} with signature: {detail.signature_template.url}")
        
        print("✅ Signature successfully linked!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Link signature for user ID 66 (rahul.chauhan)
    link_signature_for_user(66)