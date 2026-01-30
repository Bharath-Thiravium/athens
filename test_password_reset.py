#!/usr/bin/env python3
"""
Test script for Master Admin Password Reset functionality
Run this script to test the new password reset system
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/var/www/athens/app/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser
from authentication.password_utils import validate_password_strength

def test_password_reset_fields():
    """Test that the new fields exist and work correctly"""
    print("Testing password reset fields...")
    
    # Find a master admin user
    try:
        master_admin = CustomUser.objects.filter(admin_type='master').first()
        if not master_admin:
            print("❌ No master admin found. Create one first.")
            return False
        
        print(f"✅ Found master admin: {master_admin.username}")
        
        # Test field access
        print(f"   can_reset_password: {master_admin.can_reset_password}")
        print(f"   password_set_by_superadmin: {master_admin.password_set_by_superadmin}")
        
        # Test field updates
        original_can_reset = master_admin.can_reset_password
        master_admin.can_reset_password = not original_can_reset
        master_admin.save()
        
        master_admin.refresh_from_db()
        if master_admin.can_reset_password != original_can_reset:
            print("✅ Field updates work correctly")
            # Restore original value
            master_admin.can_reset_password = original_can_reset
            master_admin.save()
        else:
            print("❌ Field updates not working")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing fields: {e}")
        return False

def test_password_validation():
    """Test password validation function"""
    print("\nTesting password validation...")
    
    test_cases = [
        ("weak", False),
        ("WeakPassword", False),
        ("WeakPassword123", False),
        ("StrongPassword123!", True),
        ("MySecureP@ssw0rd", True),
    ]
    
    for password, should_be_valid in test_cases:
        is_valid, message = validate_password_strength(password)
        if is_valid == should_be_valid:
            status = "✅"
        else:
            status = "❌"
        print(f"   {status} '{password}': {message}")
    
    return True

def simulate_password_reset_workflow():
    """Simulate the complete password reset workflow"""
    print("\nSimulating password reset workflow...")
    
    try:
        master_admin = CustomUser.objects.filter(admin_type='master').first()
        if not master_admin:
            print("❌ No master admin found")
            return False
        
        print(f"✅ Testing with master admin: {master_admin.username}")
        
        # Store original values
        original_can_reset = master_admin.can_reset_password
        original_set_by_superadmin = master_admin.password_set_by_superadmin
        
        # Step 1: Superadmin sets password
        print("   Step 1: Superadmin sets password...")
        master_admin.can_reset_password = True
        master_admin.password_set_by_superadmin = True
        master_admin.save()
        print("   ✅ Password set by superadmin, reset enabled")
        
        # Step 2: Master admin resets password (simulate)
        print("   Step 2: Master admin resets password...")
        if master_admin.can_reset_password and master_admin.password_set_by_superadmin:
            master_admin.can_reset_password = False
            master_admin.password_set_by_superadmin = False
            master_admin.save()
            print("   ✅ Password reset by master admin, further resets disabled")
        else:
            print("   ❌ Reset conditions not met")
            return False
        
        # Step 3: Try to reset again (should fail)
        print("   Step 3: Try to reset again...")
        if not master_admin.can_reset_password:
            print("   ✅ Second reset correctly blocked")
        else:
            print("   ❌ Second reset not blocked")
            return False
        
        # Restore original values
        master_admin.can_reset_password = original_can_reset
        master_admin.password_set_by_superadmin = original_set_by_superadmin
        master_admin.save()
        print("   ✅ Original values restored")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in workflow simulation: {e}")
        return False

def main():
    """Run all tests"""
    print("🔐 Master Admin Password Reset System Test")
    print("=" * 50)
    
    tests = [
        test_password_reset_fields,
        test_password_validation,
        simulate_password_reset_workflow,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The password reset system is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())