#!/usr/bin/env python3
"""
Test script to verify permit creation functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Add the project directory to Python path
sys.path.append('/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ptw.models import PermitType, Permit
from authentication.models import CustomUser, Project
from django.utils import timezone

def test_permit_creation():
    """Test permit creation with proper validation"""
    
    print("Testing Permit Creation...")
    
    # Check if permit types exist
    permit_types = PermitType.objects.filter(is_active=True)
    print(f"Found {permit_types.count()} active permit types")
    
    if permit_types.count() == 0:
        print("No permit types found. Creating sample permit types...")
        # Create sample permit types
        sample_types = [
            {
                'name': 'Hot Work - Arc Welding',
                'category': 'hot_work',
                'description': 'Arc welding operations',
                'risk_level': 'medium'
            },
            {
                'name': 'Confined Space - Entry',
                'category': 'confined_space', 
                'description': 'Confined space entry work',
                'risk_level': 'high'
            }
        ]
        
        for type_data in sample_types:
            permit_type = PermitType.objects.create(**type_data)
            print(f"Created permit type: {permit_type.name}")
    
    # Get first permit type
    permit_type = permit_types.first()
    print(f"Using permit type: {permit_type.name} (ID: {permit_type.id})")
    
    # Check if users exist
    users = CustomUser.objects.filter(is_active=True)
    if users.count() == 0:
        print("No users found. Please create a user first.")
        return False
    
    user = users.first()
    print(f"Using user: {user.username}")
    
    # Test permit creation data
    permit_data = {
        'permit_type': permit_type,
        'description': 'Test permit creation',
        'location': 'Test Location',
        'planned_start_time': timezone.now() + timedelta(hours=1),
        'planned_end_time': timezone.now() + timedelta(hours=8),
        'work_nature': 'day',
        'created_by': user,
        'probability': 2,
        'severity': 2,
        'control_measures': 'Test control measures',
        'ppe_requirements': ['helmet', 'gloves', 'shoes'],
        'safety_checklist': {'item1': True, 'item2': False}
    }
    
    try:
        # Create permit
        permit = Permit.objects.create(**permit_data)
        print(f"✅ Successfully created permit: {permit.permit_number}")
        print(f"   - Type: {permit.permit_type.name}")
        print(f"   - Status: {permit.status}")
        print(f"   - Risk Level: {permit.risk_level}")
        print(f"   - Risk Score: {permit.risk_score}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create permit: {str(e)}")
        return False

def test_api_serializer():
    """Test the API serializer validation"""
    from ptw.serializers import PermitCreateUpdateSerializer
    from rest_framework.test import APIRequestFactory
    from django.contrib.auth import get_user_model
    
    print("\nTesting API Serializer...")
    
    User = get_user_model()
    user = User.objects.filter(is_active=True).first()
    
    if not user:
        print("No user found for API test")
        return False
    
    permit_type = PermitType.objects.filter(is_active=True).first()
    if not permit_type:
        print("No permit type found for API test")
        return False
    
    # Create mock request
    factory = APIRequestFactory()
    request = factory.post('/api/permits/')
    request.user = user
    
    # Test data
    test_data = {
        'permit_type': permit_type.id,
        'description': 'API Test permit',
        'location': 'API Test Location',
        'planned_start_time': (timezone.now() + timedelta(hours=1)).isoformat(),
        'planned_end_time': (timezone.now() + timedelta(hours=8)).isoformat(),
        'work_nature': 'day',
        'probability': 2,
        'severity': 2,
        'control_measures': 'API test control measures',
        'ppe_requirements': ['helmet', 'gloves'],
        'safety_checklist': {}
    }
    
    try:
        serializer = PermitCreateUpdateSerializer(data=test_data, context={'request': request})
        
        if serializer.is_valid():
            permit = serializer.save()
            print(f"✅ API Serializer test passed: {permit.permit_number}")
            return True
        else:
            print(f"❌ API Serializer validation failed: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ API Serializer test failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("PERMIT CREATION TEST")
    print("=" * 50)
    
    # Test direct model creation
    model_test = test_permit_creation()
    
    # Test API serializer
    api_test = test_api_serializer()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Model Creation Test: {'✅ PASSED' if model_test else '❌ FAILED'}")
    print(f"API Serializer Test: {'✅ PASSED' if api_test else '❌ FAILED'}")
    
    if model_test and api_test:
        print("\n🎉 All tests passed! Permit creation should work properly.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")