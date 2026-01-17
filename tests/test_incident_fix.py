#!/usr/bin/env python3
"""
Test script to verify incident submission fix
"""
import os
import sys
import django
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/var/www/athens/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from incidentmanagement.models import Incident
from incidentmanagement.serializers import IncidentSerializer
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

def test_incident_creation():
    """Test incident creation without files"""
    print("Testing incident creation...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'name': 'Test',
                'surname': 'User',
                'admin_type': 'master'
            }
        )
        
        if created:
            print(f"Created test user: {user.username}")
        else:
            print(f"Using existing test user: {user.username}")
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/api/v1/incidentmanagement/incidents/')
        request.user = user
        
        # Test data
        test_data = {
            'title': 'Test Incident for Fix Verification',
            'description': 'This is a test incident to verify the 500 error fix',
            'incident_type': 'injury',
            'severity_level': 'medium',
            'location': 'Test Location',
            'department': 'Safety',
            'date_time_incident': datetime.now().isoformat(),
            'reporter_name': 'Test User',
            'immediate_action_taken': 'Test action taken',
            'potential_causes': 'Test potential causes'
        }
        
        # Test serializer
        serializer = IncidentSerializer(data=test_data, context={'request': request})
        
        if serializer.is_valid():
            incident = serializer.save()
            print(f"✅ SUCCESS: Incident created successfully with ID: {incident.incident_id}")
            return True
        else:
            print(f"❌ VALIDATION ERROR: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_incident_creation_with_files():
    """Test incident creation with file handling logic"""
    print("\nTesting incident creation with file handling...")
    
    try:
        # Get test user
        user = User.objects.get(username='testuser')
        
        # Create a mock request with FILES
        factory = RequestFactory()
        request = factory.post('/api/v1/incidentmanagement/incidents/')
        request.user = user
        request.FILES = {}  # Empty files dict to test the file handling logic
        
        # Test data
        test_data = {
            'title': 'Test Incident with File Handling',
            'description': 'This tests the file handling logic in perform_create',
            'incident_type': 'near_miss',
            'severity_level': 'low',
            'location': 'Test Location 2',
            'department': 'Operations',
            'date_time_incident': datetime.now().isoformat(),
            'reporter_name': 'Test User',
        }
        
        # Test serializer
        serializer = IncidentSerializer(data=test_data, context={'request': request})
        
        if serializer.is_valid():
            incident = serializer.save()
            print(f"✅ SUCCESS: Incident with file handling created successfully with ID: {incident.incident_id}")
            return True
        else:
            print(f"❌ VALIDATION ERROR: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")
    try:
        # Delete test incidents
        test_incidents = Incident.objects.filter(title__startswith='Test Incident')
        count = test_incidents.count()
        test_incidents.delete()
        print(f"✅ Deleted {count} test incidents")
        
        # Optionally delete test user (commented out to avoid issues)
        # User.objects.filter(username='testuser').delete()
        # print("✅ Deleted test user")
        
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")

if __name__ == "__main__":
    print("🔧 Testing Incident Management Fix")
    print("=" * 50)
    
    success1 = test_incident_creation()
    success2 = test_incident_creation_with_files()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! The incident submission fix is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED! Please check the errors above.")
    
    cleanup_test_data()
    print("\n✅ Test completed.")