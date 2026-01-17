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
from safetyobservation.serializers import SafetyObservationSerializer
from rest_framework.test import APIRequestFactory

User = get_user_model()

def test_serializer_validation():
    print("=== Testing Serializer Validation Issues ===")
    
    try:
        user = User.objects.filter(is_active=True).first()
        if not user or not user.project:
            print("ERROR: No active user with project found")
            return
        
        print(f"Using user: {user.username} with project: {user.project.projectName}")
        
        # Create a mock request
        factory = APIRequestFactory()
        request = factory.post('/api/v1/safetyobservation/')
        request.user = user
        
        # Test different payload formats that frontend might send
        test_cases = [
            {
                'name': 'Frontend Format (strings)',
                'data': {
                    'date': '2025-01-07',
                    'time': '14:30:00',
                    'reportedBy': user.username,
                    'department': 'Electrical',
                    'workLocation': 'Test Location',
                    'activityPerforming': 'Test Activity',
                    'contractorName': '',
                    'typeOfObservation': 'unsafe_act',
                    'classification': json.dumps(['ppe_compliance']),  # JSON string
                    'safetyObservationFound': 'Test observation',
                    'severity': '2',  # String
                    'likelihood': '2',  # String
                    'correctivePreventiveAction': 'Test action',
                    'correctiveActionAssignedTo': user.username,
                    'observationStatus': 'open',
                    'remarks': ''
                }
            },
            {
                'name': 'Backend Format (proper types)',
                'data': {
                    'date': '2025-01-07',
                    'time': '14:30:00',
                    'reportedBy': user.username,
                    'department': 'Electrical',
                    'workLocation': 'Test Location',
                    'activityPerforming': 'Test Activity',
                    'contractorName': '',
                    'typeOfObservation': 'unsafe_act',
                    'classification': ['ppe_compliance'],  # List
                    'safetyObservationFound': 'Test observation',
                    'severity': 2,  # Integer
                    'likelihood': 2,  # Integer
                    'correctivePreventiveAction': 'Test action',
                    'correctiveActionAssignedTo': user.username,
                    'observationStatus': 'open',
                    'remarks': ''
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n=== {test_case['name']} ===")
            
            serializer = SafetyObservationSerializer(data=test_case['data'], context={'request': request})
            
            if serializer.is_valid():
                print("✓ Validation passed")
                try:
                    observation = serializer.save(created_by=user, project=user.project)
                    print(f"✓ Created observation: {observation.observationID}")
                except Exception as e:
                    print(f"✗ Save failed: {e}")
            else:
                print("✗ Validation failed")
                print("Errors:")
                for field, errors in serializer.errors.items():
                    print(f"  {field}: {errors}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_serializer_validation()