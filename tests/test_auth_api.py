#!/usr/bin/env python3
import requests
import json

def test_login():
    print("=== Testing Authentication API ===")
    
    # Test data
    test_users = [
        {"username": "master", "password": "admin123"},
        {"username": "test", "password": "admin123"},
        {"username": "admin", "password": "admin123"}
    ]
    
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/auth/login/"
    
    for user_data in test_users:
        print(f"\nTesting login for: {user_data['username']}")
        
        try:
            response = requests.post(login_url, json=user_data, timeout=10)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                print("✅ Login successful!")
            else:
                print("❌ Login failed!")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - server may not be running")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_login()