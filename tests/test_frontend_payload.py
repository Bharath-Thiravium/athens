#!/usr/bin/env python3

import os
import sys
import django
import json
from datetime import datetime, date, time

# Add the backend directory to Python path
sys.path.append('/var/www/athens/backend')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from safetyobservation.models import SafetyObservation
from safetyobservation.serializers import SafetyObservationSerializer
from authentication.models import Project
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.request import Request
from django.test import RequestFactory
from django.http import QueryDict
import io

User = get_user_model()

def test_frontend_payload():
    print("=== Testing Frontend Payload Format ===")
    
    try:
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("ERROR: No active users found")
            return
        
        print(f"Using user: {user.username} (ID: {user.id})")
        
        # Ensure user has a project
        if not user.project:
            project = Project.objects.first()
            if project:
                user.project = project
                user.save()
                print(f"Assigned user to project: {project.projectName}")
            else:
                print("ERROR: No projects found")
                return
        
        # Create API client to test the actual endpoint
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Test data that exactly matches what frontend sends
        frontend_payload = {
            'observationID': f'SO-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'date': '2025-01-07',
            'time': '14:30:00',
            'reportedBy': user.username,
            'department': 'Electrical',
            'workLocation': 'Test Location',
            'activityPerforming': 'Test Activity',
            'contractorName': '',
            'typeOfObservation': 'unsafe_act',
            'classification': json.dumps(['ppe_compliance']),  # Frontend sends as JSON string
            'safetyObservationFound': 'Test observation description',
            'severity': '2',  # Frontend sends as string
            'likelihood': '2',  # Frontend sends as string
            'correctivePreventiveAction': 'Test corrective action',
            'correctiveActionAssignedTo': user.username,
            'observationStatus': 'open',
            'remarks': 'Test remarks'
        }
        
        print("\n=== Frontend Payload ===")
        for key, value in frontend_payload.items():
            print(f"{key}: {value} ({type(value).__name__})")
        
        # Test the actual API endpoint
        print("\n=== Testing API Endpoint ===")
        response = client.post('/api/v1/safetyobservation/', frontend_payload, format='multipart')
        
        print(f"Response Status: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"Response Data: {response.data}")
        else:
            print(f"Response Content: {response.content.decode('utf-8') if response.content else 'No content'}")
        
        if response.status_code == 201:
            print("✓ API endpoint test passed")
        else:
            print("✗ API endpoint test failed")
            if hasattr(response, 'data') and response.data:
                print("Error details:")
                if isinstance(response.data, dict):
                    for field, errors in response.data.items():
                        print(f"  {field}: {errors}")
                else:
                    print(f"  {response.data}")
            elif response.content:
                print(f"Error content: {response.content.decode('utf-8')}")
        
        # Test with different classification formats
        print("\n=== Testing Classification Formats ===")
        
        # Test 1: JSON string (what frontend sends)
        test_data_1 = frontend_payload.copy()
        test_data_1['observationID'] = f'SO-{datetime.now().strftime("%Y%m%d-%H%M%S")}-1'
        test_data_1['classification'] = json.dumps(['ppe_compliance'])
        
        response_1 = client.post('/api/v1/safetyobservation/', test_data_1, format='multipart')
        print(f"JSON string classification - Status: {response_1.status_code}")
        if response_1.status_code != 201:
            print(f"  Error: {response_1.data}")
        
        # Test 2: List (what serializer expects)
        test_data_2 = frontend_payload.copy()
        test_data_2['observationID'] = f'SO-{datetime.now().strftime("%Y%m%d-%H%M%S")}-2'
        test_data_2['classification'] = ['ppe_compliance']
        
        response_2 = client.post('/api/v1/safetyobservation/', test_data_2, format='multipart')
        print(f"List classification - Status: {response_2.status_code}")
        if response_2.status_code != 201:
            print(f"  Error: {response_2.data}")
        
        # Test 3: Single string
        test_data_3 = frontend_payload.copy()
        test_data_3['observationID'] = f'SO-{datetime.now().strftime("%Y%m%d-%H%M%S")}-3'
        test_data_3['classification'] = 'ppe_compliance'
        
        response_3 = client.post('/api/v1/safetyobservation/', test_data_3, format='multipart')
        print(f"Single string classification - Status: {response_3.status_code}")
        if response_3.status_code != 201:
            print(f"  Error: {response_3.data}")
        
        # Test with missing required fields
        print("\n=== Testing Missing Required Fields ===")
        
        required_fields = ['date', 'time', 'department', 'workLocation', 'activityPerforming', 
                          'typeOfObservation', 'classification', 'safetyObservationFound', 
                          'severity', 'likelihood', 'correctivePreventiveAction', 'correctiveActionAssignedTo']
        
        for field in required_fields:
            test_data = frontend_payload.copy()
            test_data['observationID'] = f'SO-{datetime.now().strftime("%Y%m%d-%H%M%S")}-missing-{field}'
            del test_data[field]  # Remove the field
            
            response = client.post('/api/v1/safetyobservation/', test_data, format='multipart')
            if response.status_code != 201:
                print(f"Missing {field} - Status: {response.status_code}")
                if field in str(response.data):
                    print(f"  ✓ Correctly identified missing field: {field}")
                else:
                    print(f"  ✗ Unexpected error: {response.data}")
            else:
                print(f"Missing {field} - Status: {response.status_code} (Unexpected success)")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_frontend_payload()