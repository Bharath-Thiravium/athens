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
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

User = get_user_model()

def test_safety_observation_creation():
    print("=== Testing Safety Observation Creation ===")
    
    # Get or create a test user with project
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
        
        print(f"User project: {user.project.projectName}")
        
        # Test data that matches frontend payload
        test_data = {
            'date': '2025-01-07',
            'time': '14:30:00',
            'reportedBy': user.username,
            'department': 'Electrical',
            'workLocation': 'Test Location',
            'activityPerforming': 'Test Activity',
            'contractorName': '',
            'typeOfObservation': 'unsafe_act',
            'classification': ['ppe_compliance'],  # As JSON array
            'safetyObservationFound': 'Test observation description',
            'severity': 2,
            'likelihood': 2,
            'correctivePreventiveAction': 'Test corrective action',
            'correctiveActionAssignedTo': user.username,
            'observationStatus': 'open',
            'remarks': 'Test remarks'
        }
        
        print("\n=== Test Data ===")
        for key, value in test_data.items():
            print(f"{key}: {value} ({type(value).__name__})")
        
        # Create a mock request for serializer context
        factory = APIRequestFactory()
        request = factory.post('/api/v1/safetyobservation/')
        request.user = user
        
        # Test serializer validation
        print("\n=== Testing Serializer ===")
        serializer = SafetyObservationSerializer(data=test_data, context={'request': request})
        
        if serializer.is_valid():
            print("✓ Serializer validation passed")
            
            # Try to save
            try:
                observation = serializer.save(created_by=user, project=user.project)
                print(f"✓ Safety observation created successfully: {observation.observationID}")
                
                # Verify the saved data
                print(f"  - ID: {observation.id}")
                print(f"  - Observation ID: {observation.observationID}")
                print(f"  - Date: {observation.date}")
                print(f"  - Time: {observation.time}")
                print(f"  - Type: {observation.typeOfObservation}")
                print(f"  - Classification: {observation.classification}")
                print(f"  - Severity: {observation.severity}")
                print(f"  - Likelihood: {observation.likelihood}")
                print(f"  - Risk Score: {observation.riskScore}")
                print(f"  - Project: {observation.project}")
                print(f"  - Created by: {observation.created_by}")
                
            except Exception as e:
                print(f"✗ Error saving observation: {e}")
                import traceback
                traceback.print_exc()
                
        else:
            print("✗ Serializer validation failed")
            print("Validation errors:")
            for field, errors in serializer.errors.items():
                print(f"  {field}: {errors}")
        
        # Test with minimal required data
        print("\n=== Testing Minimal Required Data ===")
        minimal_data = {
            'date': '2025-01-07',
            'time': '14:30:00',
            'department': 'Electrical',
            'workLocation': 'Test Location',
            'activityPerforming': 'Test Activity',
            'typeOfObservation': 'unsafe_act',
            'classification': ['ppe_compliance'],
            'safetyObservationFound': 'Test observation',
            'severity': 1,
            'likelihood': 1,
            'correctivePreventiveAction': 'Test action',
            'correctiveActionAssignedTo': user.username,
        }
        
        serializer_minimal = SafetyObservationSerializer(data=minimal_data, context={'request': request})
        
        if serializer_minimal.is_valid():
            print("✓ Minimal data validation passed")
            try:
                observation_minimal = serializer_minimal.save(created_by=user, project=user.project)
                print(f"✓ Minimal safety observation created: {observation_minimal.observationID}")
            except Exception as e:
                print(f"✗ Error saving minimal observation: {e}")
        else:
            print("✗ Minimal data validation failed")
            print("Validation errors:")
            for field, errors in serializer_minimal.errors.items():
                print(f"  {field}: {errors}")
        
        # Test model field requirements
        print("\n=== Testing Model Field Requirements ===")
        model_fields = SafetyObservation._meta.get_fields()
        required_fields = []
        for field in model_fields:
            if hasattr(field, 'null') and not field.null and not hasattr(field, 'default') and field.name != 'id':
                required_fields.append(field.name)
        
        print("Model required fields (no null, no default):")
        for field in required_fields:
            print(f"  - {field}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_safety_observation_creation()