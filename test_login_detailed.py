#!/usr/bin/env python3

import requests
import json

# Test login and get the actual response structure
base_url = "http://127.0.0.1:8000"

login_data = {
    "username": "test",
    "password": "test123"
}

try:
    login_response = requests.post(f"{base_url}/authentication/login/", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    print(f"Login Response: {json.dumps(login_response.json(), indent=2)}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        # Try different possible token field names
        token = (login_result.get('access_token') or 
                login_result.get('token') or 
                login_result.get('access') or
                login_result.get('jwt'))
        
        print(f"Token found: {token[:20]}..." if token else "No token found")
        
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test authenticated manpower request
            print(f"\n=== Testing authenticated manpower request ===")
            auth_response = requests.get(f"{base_url}/man/manpower/", headers=headers)
            print(f"Status: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                data = auth_response.json()
                print(f"Response Type: {type(data)}")
                if isinstance(data, list):
                    print(f"Number of items: {len(data)}")
                    for i, item in enumerate(data[:3]):  # Show first 3 items
                        print(f"Item {i+1}: {json.dumps(item, indent=2)}")
                else:
                    print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"Error: {auth_response.text}")
                
except Exception as e:
    print(f"Error: {e}")