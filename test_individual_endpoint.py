#!/usr/bin/env python3

import requests
import json

# Test the individual endpoint specifically
base_url = "http://127.0.0.1:8000"

# Login first
login_data = {"username": "test", "password": "test123"}
login_response = requests.post(f"{base_url}/authentication/login/", json=login_data)
token = login_response.json().get('access')
headers = {"Authorization": f"Bearer {token}"}

# Test different endpoints
endpoints = [
    ("/man/manpower/", "Basic endpoint"),
    ("/man/manpower/individual/", "Individual endpoint"),
    ("/man/manpower/?format=individual", "Basic with format param"),
    ("/man/manpower/individual/?format=individual", "Individual with format param")
]

for endpoint, description in endpoints:
    print(f"\n=== Testing {description} ===")
    print(f"URL: {base_url}{endpoint}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of items: {len(data)}")
                if len(data) > 0:
                    first_item = data[0]
                    print(f"First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
                    if 'categories' in first_item:
                        print("This is GROUPED data")
                    elif 'category' in first_item:
                        print("This is INDIVIDUAL data")
                    else:
                        print("Unknown data format")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")