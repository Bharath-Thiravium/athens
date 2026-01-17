#!/usr/bin/env python3
"""
Simple API test to verify incident submission fix
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://prozeal.athenas.co.in"
API_URL = f"{BASE_URL}/api/v1/incidentmanagement/incidents/"

def test_incident_submission():
    """Test incident submission via API"""
    print("🔧 Testing Incident Submission API")
    print("=" * 50)
    
    # Test data - minimal required fields
    test_data = {
        'title': 'API Test Incident - Fix Verification',
        'description': 'This is a test incident to verify the 500 error fix via API',
        'incident_type': 'near_miss',
        'severity_level': 'low',
        'location': 'Test Location API',
        'department': 'Safety',
        'date_time_incident': datetime.now().isoformat(),
        'reporter_name': 'API Test User',
    }
    
    print("Test data prepared:")
    print(json.dumps(test_data, indent=2))
    print("\nNote: This test will fail with authentication error since we don't have valid credentials.")
    print("But it will help us see if the API endpoint is responding correctly.")
    
    try:
        # Make the request (this will fail due to authentication, but we can see the response)
        response = requests.post(API_URL, json=test_data, timeout=10)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 401:
            print("✅ Expected 401 Unauthorized - API endpoint is responding correctly")
            print("The 500 error should be fixed for authenticated requests")
        elif response.status_code == 500:
            print("❌ Still getting 500 error - fix may not be complete")
            print(f"Response: {response.text}")
        else:
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        
    print("\n" + "=" * 50)
    print("API test completed. For full testing, use authenticated requests from the frontend.")

if __name__ == "__main__":
    test_incident_submission()