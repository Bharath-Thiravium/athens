#!/usr/bin/env python3

"""
Test script to verify permit types API is working correctly
"""

import requests
import json

def test_permit_types_api():
    """Test the permit types API endpoint"""
    
    # Test the API endpoint - try common uvicorn ports
    ports_to_try = [8000, 8080, 3000, 5000]
    api_url = None
    
    for port in ports_to_try:
        test_url = f"http://localhost:{port}/api/v1/ptw/permit-types/"
        try:
            response = requests.get(test_url, timeout=2)
            if response.status_code in [200, 401, 403]:  # Server is responding
                api_url = test_url
                break
        except:
            continue
    
    if not api_url:
        print("Could not find running server on common ports (8000, 8080, 3000, 5000)")
        print("Make sure your uvicorn server is running")
        return
    
    try:
        print(f"Testing API endpoint: {api_url}")
        response = requests.get(api_url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response type: {type(data)}")
            
            if isinstance(data, dict) and 'results' in data:
                permit_types = data['results']
                print(f"Found {len(permit_types)} permit types in 'results' field")
            elif isinstance(data, list):
                permit_types = data
                print(f"Found {len(permit_types)} permit types in direct list")
            else:
                print(f"Unexpected response format: {data}")
                return
            
            if permit_types:
                print(f"\\nFirst permit type:")
                print(json.dumps(permit_types[0], indent=2))
                
                print(f"\\nAll permit type names:")
                for i, pt in enumerate(permit_types, 1):
                    print(f"{i:2d}. {pt.get('name', 'No name')} ({pt.get('category', 'No category')})")
                
                categories = set(pt.get('category') for pt in permit_types)
                print(f"\\nCategories found: {sorted(categories)}")
            else:
                print("No permit types found in response")
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection error - make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_permit_types_api()