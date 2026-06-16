#!/usr/bin/env python3
"""
Test script for PTW Unified Error Handling
Verifies that the unified error handling is working correctly in PTW workflow views
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/var/www/athens/app/backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_unified_error_handling_import():
    """Test that unified error handling classes can be imported"""
    print("Testing unified error handling import...")
    
    try:
        from ptw.unified_error_handling import (
            PTWError, PTWValidationError, PTWPermissionError, 
            PTWWorkflowError, PTWSignatureError, PTWConflictError,
            unified_exception_handler, ptw_error_handler
        )
        print("✅ All unified error handling classes imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import unified error handling classes: {e}")
        return False

def test_workflow_views_import():
    """Test that workflow views can import unified error handling"""
    print("\nTesting workflow views import...")
    
    try:
        from ptw.workflow_views import PTWValidationError, PTWPermissionError, PTWWorkflowError
        print("✅ Workflow views can import unified error handling classes")
        return True
    except ImportError as e:
        print(f"❌ Failed to import error classes in workflow views: {e}")
        return False

def test_error_class_functionality():
    """Test that error classes work correctly"""
    print("\nTesting error class functionality...")
    
    try:
        from ptw.unified_error_handling import PTWValidationError, PTWPermissionError, PTWWorkflowError
        
        # Test PTWValidationError
        try:
            raise PTWValidationError("Test validation error", field="test_field")
        except PTWValidationError as e:
            assert e.message == "Test validation error"
            assert e.field == "test_field"
            assert e.code == "VALIDATION_ERROR"
            print("✅ PTWValidationError works correctly")
        
        # Test PTWPermissionError
        try:
            raise PTWPermissionError("Test permission error", action="test_action")
        except PTWPermissionError as e:
            assert e.message == "Test permission error"
            assert e.action == "test_action"
            assert e.code == "PERMISSION_ERROR"
            print("✅ PTWPermissionError works correctly")
        
        # Test PTWWorkflowError
        try:
            raise PTWWorkflowError("Test workflow error", current_status="draft", target_status="submitted")
        except PTWWorkflowError as e:
            assert e.message == "Test workflow error"
            assert e.current_status == "draft"
            assert e.target_status == "submitted"
            assert e.code == "WORKFLOW_ERROR"
            print("✅ PTWWorkflowError works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Error class functionality test failed: {e}")
        return False

def test_error_handler_functionality():
    """Test that error handler works correctly"""
    print("\nTesting error handler functionality...")
    
    try:
        from ptw.unified_error_handling import ptw_error_handler
        from rest_framework.response import Response
        
        # Test success response creation
        response = ptw_error_handler.create_success_response(
            data={"test": "data"}, 
            message="Test success"
        )
        assert isinstance(response, Response)
        assert response.status_code == 200
        print("✅ Success response creation works")
        
        # Test created response creation
        response = ptw_error_handler.create_created_response(
            data={"test": "created"}, 
            message="Test created"
        )
        assert isinstance(response, Response)
        assert response.status_code == 201
        print("✅ Created response creation works")
        
        return True
    except Exception as e:
        print(f"❌ Error handler functionality test failed: {e}")
        return False

def test_other_ptw_modules_integration():
    """Test that other PTW modules can use unified error handling"""
    print("\nTesting other PTW modules integration...")
    
    try:
        # Test signature service
        from ptw.signature_service import PTWSignatureError, PTWPermissionError, PTWValidationError
        print("✅ Signature service can import unified error handling")
        
        # Test canonical workflow manager
        from ptw.canonical_workflow_manager import PTWWorkflowError, PTWValidationError, PTWPermissionError
        print("✅ Canonical workflow manager can import unified error handling")
        
        return True
    except ImportError as e:
        print(f"❌ Other PTW modules integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 PTW Unified Error Handling Test Suite")
    print("=" * 50)
    
    tests = [
        test_unified_error_handling_import,
        test_workflow_views_import,
        test_error_class_functionality,
        test_error_handler_functionality,
        test_other_ptw_modules_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! PTW Unified Error Handling is working correctly.")
        print("\n📋 Summary:")
        print("- ✅ Unified error handling classes are properly defined")
        print("- ✅ Workflow views can import and use error classes")
        print("- ✅ Error classes have correct functionality")
        print("- ✅ Error handler utility functions work")
        print("- ✅ Other PTW modules integrate correctly")
        print("\n🚀 The unified error handling implementation is complete!")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())