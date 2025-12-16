#!/usr/bin/env python3
"""
Test script to verify backend-frontend API connectivity for incident management
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "incidents": "/api/v1/incidentmanagement/incidents/",
    "investigations": "/api/v1/incidentmanagement/investigations/",
    "capas": "/api/v1/incidentmanagement/capas/",
    "8d_processes": "/api/v1/incidentmanagement/8d-processes/",
}

def test_endpoint(endpoint_name, endpoint_path):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint_path}"
    
    print(f"\n🔍 Testing {endpoint_name}: {url}")
    
    try:
        # Test GET request (should work without authentication for basic connectivity)
        response = requests.get(url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS: Endpoint is accessible")
            try:
                data = response.json()
                print(f"   📊 Response Data Type: {type(data)}")
                if isinstance(data, dict) and 'results' in data:
                    print(f"   📋 Results Count: {len(data.get('results', []))}")
                elif isinstance(data, list):
                    print(f"   📋 Items Count: {len(data)}")
            except json.JSONDecodeError:
                print(f"   ⚠️  Response is not JSON")
                
        elif response.status_code == 401:
            print(f"   🔐 AUTHENTICATION REQUIRED: Endpoint exists but needs auth")
            
        elif response.status_code == 403:
            print(f"   🚫 FORBIDDEN: Endpoint exists but access denied")
            
        elif response.status_code == 404:
            print(f"   ❌ NOT FOUND: Endpoint does not exist")
            
        else:
            print(f"   ⚠️  UNEXPECTED STATUS: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ CONNECTION ERROR: Cannot connect to backend")
        return False
        
    except requests.exceptions.Timeout:
        print(f"   ⏰ TIMEOUT: Request timed out")
        return False
        
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False
        
    return True

def test_backend_health():
    """Test if backend is running"""
    print(f"🏥 Testing Backend Health: {BACKEND_URL}")
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/", timeout=5)
        if response.status_code in [200, 302, 401, 403]:
            print(f"   ✅ Backend is running (Status: {response.status_code})")
            return True
        else:
            print(f"   ⚠️  Backend responded with status: {response.status_code}")
            return False
    except:
        print(f"   ❌ Backend is not accessible")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 INCIDENT MANAGEMENT API CONNECTIVITY TEST")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    
    # Test backend health first
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start the Django server first.")
        sys.exit(1)
    
    # Test each endpoint
    print(f"\n📡 Testing API Endpoints:")
    print("-" * 40)
    
    success_count = 0
    total_count = len(API_ENDPOINTS)
    
    for endpoint_name, endpoint_path in API_ENDPOINTS.items():
        if test_endpoint(endpoint_name, endpoint_path):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Backend-Frontend connectivity is working.")
    elif success_count > 0:
        print("\n⚠️  PARTIAL SUCCESS: Some endpoints are working.")
    else:
        print("\n❌ ALL TESTS FAILED: Check backend configuration.")
    
    print("\n💡 NEXT STEPS:")
    print("1. Ensure Django server is running: python manage.py runserver")
    print("2. Check CORS settings in backend/settings.py")
    print("3. Verify incident management app is in INSTALLED_APPS")
    print("4. Run migrations: python manage.py migrate")
    print("5. Check frontend .env file for correct VITE_BACKEND_URL")

if __name__ == "__main__":
    main()
