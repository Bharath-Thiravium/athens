#!/usr/bin/env python
"""
Test script to verify ESG implementation
Run this after starting the Django server
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_esg_endpoints():
    """Test ESG API endpoints"""
    
    # Test endpoints (without authentication for now)
    endpoints = [
        '/api/v1/environment/aspects/',
        '/api/v1/environment/generation/',
        '/api/v1/environment/ghg-activities/',
        '/api/v1/environment/waste-manifests/',
        '/api/v1/environment/biodiversity-events/',
        '/api/v1/environment/policies/',
        '/api/v1/environment/grievances/',
        '/api/v1/environment/emission-factors/',
    ]
    
    print("Testing ESG API endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✓ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ {endpoint} - Connection failed (server not running?)")
        except Exception as e:
            print(f"✗ {endpoint} - Error: {e}")

def test_environment_app():
    """Test if environment app is properly configured"""
    try:
        import django
        import os
        import sys
        
        # Add the backend directory to Python path
        sys.path.append('/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project/backend')
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
        django.setup()
        
        # Import models
        from environment.models import (
            EnvironmentAspect, GenerationData, GHGActivity, 
            WasteManifest, BiodiversityEvent, ESGPolicy, Grievance
        )
        
        print("✓ Environment app models imported successfully")
        
        # Test model creation (without saving)
        aspect = EnvironmentAspect(
            aspect_type='energy',
            description='Test aspect',
            severity=2,
            likelihood=3
        )
        print("✓ EnvironmentAspect model can be instantiated")
        
        return True
        
    except Exception as e:
        print(f"✗ Environment app test failed: {e}")
        return False

if __name__ == '__main__':
    print("ESG Implementation Test")
    print("=" * 50)
    
    # Test Django app
    if test_environment_app():
        print("\n" + "=" * 50)
        # Test API endpoints
        test_esg_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo fully test the implementation:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Start the React frontend: npm run dev")
    print("3. Navigate to /dashboard/esg in your browser")
    print("4. Run: python manage.py seed_esg_data")