#!/usr/bin/env python3

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append('/var/www/athens/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.urls import reverse, resolve
from django.test import Client
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

def test_url_routing():
    print("=== Testing URL Routing ===")
    
    try:
        # Test URL resolution
        print("\\n1. Testing URL Resolution...")
        try:
            url = reverse('safetyobservation-list')
            print(f"✓ URL resolved: {url}")
        except Exception as e:
            print(f"✗ URL resolution failed: {e}")
            
            # Try alternative URL patterns
            try:
                from django.urls import get_resolver
                resolver = get_resolver()
                print("Available URL patterns:")
                for pattern in resolver.url_patterns:
                    print(f"  {pattern}")
            except Exception as e2:
                print(f"Could not get URL patterns: {e2}")
        
        # Test direct URL access
        print("\\n2. Testing Direct URL Access...")
        client = Client()
        
        # Test without authentication first
        response = client.get('/api/v1/safetyobservation/')
        print(f"Unauthenticated GET status: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Authentication required (expected)")
        elif response.status_code == 400:
            print("✗ Bad Request - possible URL or middleware issue")
            print(f"Response content: {response.content.decode('utf-8')[:200]}...")
        
        # Test with authentication
        user = User.objects.filter(is_active=True).first()
        if user:
            client.force_login(user)
            auth_response = client.get('/api/v1/safetyobservation/')
            print(f"Authenticated GET status: {auth_response.status_code}")
            
            if auth_response.status_code == 200:
                print("✓ Authenticated access working")
            elif auth_response.status_code == 400:
                print("✗ Bad Request with authentication")
                print(f"Response content: {auth_response.content.decode('utf-8')[:200]}...")
        
        # Test other endpoints for comparison
        print("\\n3. Testing Other Endpoints...")
        test_endpoints = [
            '/authentication/login/',
            '/api/v1/ptw/',
            '/health/',
        ]
        
        for endpoint in test_endpoints:
            try:
                response = client.get(endpoint)
                print(f"{endpoint}: {response.status_code}")
            except Exception as e:
                print(f"{endpoint}: ERROR - {e}")
        
        # Check Django settings
        print("\\n4. Checking Django Settings...")
        print(f"DEBUG: {settings.DEBUG}")
        print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # Check middleware
        print("\\nMiddleware:")
        for middleware in settings.MIDDLEWARE:
            print(f"  {middleware}")
        
        # Check if there are any custom error handlers
        print("\\n5. Checking Error Handling...")
        if hasattr(settings, 'HANDLER400'):
            print(f"Custom 400 handler: {settings.HANDLER400}")
        else:
            print("No custom 400 handler")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_url_routing()