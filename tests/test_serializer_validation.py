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
            },
            {
                'name': 'Minimal Required Fields',
                'data': {
                    'date': '2025-01-07',
                    'time': '14:30:00',
                    'department': 'Electrical',
                    'workLocation': 'Test Location',
                    'activityPerforming': 'Test Activity',
                    'typeOfObservation': 'unsafe_act',
                    'classification': ['ppe_compliance'],
                    'safetyObservationFound': 'Test observation',
                    'severity': 2,
                    'likelihood': 2,
                    'correctivePreventiveAction': 'Test action',
                    'correctiveActionAssignedTo': user.username,
                }
            }
        ]\n        
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
        
        # Test field requirements
        print("\n=== Testing Field Requirements ===")
        
        base_data = {
            'date': '2025-01-07',
            'time': '14:30:00',
            'department': 'Electrical',
            'workLocation': 'Test Location',
            'activityPerforming': 'Test Activity',
            'typeOfObservation': 'unsafe_act',
            'classification': ['ppe_compliance'],
            'safetyObservationFound': 'Test observation',
            'severity': 2,
            'likelihood': 2,
            'correctivePreventiveAction': 'Test action',
            'correctiveActionAssignedTo': user.username,
        }
        
        # Test each field by removing it
        for field in list(base_data.keys()):
            test_data = base_data.copy()
            del test_data[field]
            
            serializer = SafetyObservationSerializer(data=test_data, context={'request': request})
            if not serializer.is_valid():
                if field in serializer.errors:
                    print(f"✓ {field} is required (correctly detected)")
                else:
                    print(f"? {field} removal caused other errors: {serializer.errors}")
            else:
                print(f"✗ {field} appears to be optional")\n        \n    except Exception as e:\n        print(f\"ERROR: {e}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == '__main__':\n    test_serializer_validation()