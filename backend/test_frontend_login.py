#!/usr/bin/env python
import requests
import json

# Test the exact payload format the frontend will send
payload = {
    "username": "ilaiaraja",
    "password": "admin123"
}

try:
    response = requests.post(
        'http://localhost:8000/authentication/login/',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"Access token: {data.get('access', 'N/A')[:50]}...")
        print(f"Refresh token: {data.get('refresh', 'N/A')[:50]}...")
        print(f"Username: {data.get('username')}")
        print(f"User type: {data.get('usertype')}")
        print(f"Project ID: {data.get('project_id')}")
    else:
        print("❌ Login failed:")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")