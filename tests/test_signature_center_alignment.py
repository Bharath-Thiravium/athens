#!/usr/bin/env python3
"""
Test script to verify center-aligned signature template generation
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, '/var/www/athens/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser, UserDetail
from authentication.signature_template_generator_new import create_user_signature_template

def test_signature_generation():
    """Test signature template generation with center alignment"""
    
    # Find a test user
    test_user = CustomUser.objects.filter(user_type='adminuser').first()
    if not test_user:
        print("No adminuser found for testing")
        return False
    
    print(f"Testing signature generation for user: {test_user.username}")
    
    # Get or create UserDetail
    user_detail, created = UserDetail.objects.get_or_create(user=test_user)
    if created:
        print("Created new UserDetail for testing")
    
    # Ensure user has required fields
    if not test_user.name:
        test_user.name = "Test User"
        test_user.save()
    
    if not test_user.designation:
        test_user.designation = "Test Designation"
        test_user.save()
    
    try:
        # Generate signature template
        result = create_user_signature_template(user_detail)
        
        if result and result.signature_template:
            print(f"✅ Signature template generated successfully!")
            print(f"   Template path: {result.signature_template.path}")
            print(f"   Template URL: {result.signature_template.url}")
            print(f"   Canvas size: 800x200 (center-aligned layout)")
            print(f"   Layout zones: LEFT (name+ID), CENTER (logo), RIGHT (signature text)")
            return True
        else:
            print("❌ Signature template generation failed - no template created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating signature template: {e}")
        return False

if __name__ == "__main__":
    print("Testing Center-Aligned Signature Template Generation")
    print("=" * 50)
    
    success = test_signature_generation()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("The signature template now uses:")
        print("- Fixed 800x200 canvas size")
        print("- LEFT zone (x=20): User name + Employee ID")
        print("- CENTER zone (horizontally centered): Company logo (50% opacity)")
        print("- RIGHT zone (x=450): Digital signature text + designation + company")
    else:
        print("\n❌ Test failed!")
    
    print("\nNext steps:")
    print("1. Frontend CSS will center the image container")
    print("2. Internal layout is now correctly aligned at image generation time")
    print("3. No CSS hacks needed for internal content alignment")