from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import Project

User = get_user_model()

class DeprecatedSignatureEndpointTest(TestCase):
    """Test that deprecated signature endpoint returns 410 Gone"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.project = Project.objects.create(
            projectName='Test Project',
            projectCategory='test',
            capacity='100MW',
            location='Test Location',
            latitude=0.0,
            longitude=0.0,
            nearestPoliceStation='Test Police',
            nearestPoliceStationContact='123456789',
            nearestHospital='Test Hospital',
            nearestHospitalContact='987654321',
            commencementDate='2024-01-01',
            deadlineDate='2024-12-31'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            project=self.project,
            user_type='admin'
        )
    
    def test_deprecated_signature_generate_returns_410(self):
        """Test that /authentication/signature/generate/ returns 410 Gone"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post('/authentication/signature/generate/', {})
        
        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertIn('error', response.data)
        self.assertIn('Deprecated', response.data['error'])
        self.assertIn('JSON-only', response.data['error'])
        
        # Verify migration guide is provided
        self.assertIn('migration_guide', response.data)
        self.assertIn('new_endpoint', response.data['migration_guide'])
        self.assertIn('/api/v1/ptw/permits/', response.data['migration_guide']['new_endpoint'])
        
        print("✅ Deprecated signature endpoint correctly returns 410 Gone")