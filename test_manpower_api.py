#!/usr/bin/env python3

import requests
import json

# Test the manpower API endpoints
base_url = "http://127.0.0.1:8000"

def test_endpoint(endpoint, description):
    print(f"\n=== Testing {description} ===")
    print(f"URL: {base_url}{endpoint}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of items: {len(data)}")
                if len(data) > 0:
                    print(f"First item: {json.dumps(data[0], indent=2)}")
            elif isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

# Test different endpoints
test_endpoint("/man/test/", "Test Endpoint")
test_endpoint("/man/debug/", "Debug Endpoint")
test_endpoint("/man/manpower/", "Basic Manpower Endpoint")
test_endpoint("/man/manpower/individual/", "Individual Manpower Endpoint")
test_endpoint("/man/work-types/", "Work Types Endpoint")

print("\n=== Testing with authentication ===")
# Test with a simple login first
login_data = {
    "username": "test",  # Using the test user we saw in the database
    "password": "test123"  # Common test password
}

try:
    login_response = requests.post(f"{base_url}/authentication/login/", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('access_token')
        print(f"Got token: {token[:20]}..." if token else "No token received")
        
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test authenticated requests
            print(f"\n=== Testing authenticated manpower requests ===")
            auth_response = requests.get(f"{base_url}/man/manpower/", headers=headers)
            print(f"Authenticated Status: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                data = auth_response.json()
                print(f"Authenticated Response Type: {type(data)}")
                if isinstance(data, list):
                    print(f"Number of items: {len(data)}")
                    if len(data) > 0:
                        print(f"First item: {json.dumps(data[0], indent=2)}")
                else:
                    print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"Authenticated Error: {auth_response.text}")
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Authentication test error: {e}")