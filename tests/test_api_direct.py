#!/usr/bin/env python3

import os
import sys
import django
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('/var/www/athens/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import json

User = get_user_model()

def test_login():
    print("=== Testing Login Endpoint ===")
    
    try:
        # Create Django test client
        client = Client()
        
        # Test data
        test_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        print("\nTesting POST request to /authentication/login/...")
        response = client.post('/authentication/login/', test_data, content_type='application/json')
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.items())}")
        
        if response.status_code == 200:
            print("✓ Login endpoint working correctly")
            try:
                response_data = json.loads(response.content.decode('utf-8'))
                print(f"✓ Login successful. Token: {response_data.get('access', 'N/A')}")
            except json.JSONDecodeError:
                print("✓ Response received but not JSON")
        else:
            print(f"✗ Login endpoint failed: {response.status_code}")
            print(f"Response content: {response.content.decode('utf-8')}")
            
            # Try to get more details about the error
            if hasattr(response, 'context') and response.context:
                print(f"Response context: {response.context}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_login()
