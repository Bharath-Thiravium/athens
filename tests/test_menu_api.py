#!/usr/bin/env python
import requests
import json

# Test menu API endpoints
BASE_URL = 'http://localhost:8001'

def test_menu_endpoints():
    print("Testing Menu Management API Endpoints...")
    
    # Test 1: Get all categories
    print("\n1. Testing /api/menu/categories/")
    try:
        response = requests.get(f"{BASE_URL}/api/menu/categories/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Categories found: {len(data)}")
            for cat in data[:2]:  # Show first 2 categories
                print(f"  - {cat['name']} ({len(cat['modules'])} modules)")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get user menu (requires authentication)
    print("\n2. Testing /api/menu/user-menu/ (without auth)")
    try:
        response = requests.get(f"{BASE_URL}/api/menu/user-menu/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nMenu API testing completed!")

if __name__ == '__main__':
    test_menu_endpoints()