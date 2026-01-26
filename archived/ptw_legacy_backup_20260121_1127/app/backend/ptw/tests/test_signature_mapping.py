"""
Tests for digital signature mapping in permit serializer for print layout
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from ptw.models import Permit, PermitType, DigitalSignature
from authentication.models import Project

User = get_user_model()


class SignatureMappingTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create project first
        self.project = Project.objects.create(
            projectName='Test Project',
            projectCategory='construction',
            capacity='100',
            location='Test Location',
            nearestPoliceStation='Test Police',
            nearestPoliceStationContact='123',
            nearestHospital='Test Hospital',
            nearestHospitalContact='456',
            commencementDate=timezone.now().date(),
            deadlineDate=(timezone.now() + timezone.timedelta(days=365)).date()
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            name='Test',
            surname='User',
            user_type='employee',
            project=self.project
        )
        self.client.force_authenticate(user=self.user)
        
        # Create permit type
        self.permit_type = PermitType.objects.create(
            name='Test Work',
            category='cold_work',
            risk_level='low'
        )
        
        # Create permit
        self.permit = Permit.objects.create(
            permit_type=self.permit_type,
            description='Test work',
            location='Test location',
            planned_start_time=timezone.now(),
            planned_end_time=timezone.now() + timezone.timedelta(hours=8),
            created_by=self.user,
            project=self.project
        )
    
    def test_signatures_by_type_field_exists(self):
        """Test that signatures_by_type field is included in serializer"""
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/', follow=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('signatures_by_type', response.data)
    
    def test_signature_mapping_with_three_types(self):
        """Test signature mapping with requestor, verifier, and approver"""
        # Create three signatures
        requestor_sig = DigitalSignature.objects.create(
            permit=self.permit,
            signature_type='requestor',
            signatory=self.user,
            signature_data='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        verifier_user = User.objects.create_user(
            username='verifier',
            email='verifier@example.com',
            password='pass',
            name='Verifier',
            surname='User',
            user_type='employee'
        )
        verifier_sig = DigitalSignature.objects.create(
            permit=self.permit,
            signature_type='verifier',
            signatory=verifier_user,
            signature_data='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        approver_user = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='pass',
            name='Approver',
            surname='User',
            user_type='employee'
        )
        approver_sig = DigitalSignature.objects.create(
            permit=self.permit,
            signature_type='approver',
            signatory=approver_user,
            signature_data='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        # Get permit details
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/', follow=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check signatures_by_type
        sig_map = response.data['signatures_by_type']
        self.assertIn('requestor', sig_map)
        self.assertIn('verifier', sig_map)
        self.assertIn('approver', sig_map)
        
        # Verify requestor signature
        self.assertEqual(sig_map['requestor']['signature_type'], 'requestor')
        self.assertIn('signatory_details', sig_map['requestor'])
        self.assertEqual(sig_map['requestor']['signatory_details']['first_name'], 'Test')
        
        # Verify verifier signature
        self.assertEqual(sig_map['verifier']['signature_type'], 'verifier')
        self.assertEqual(sig_map['verifier']['signatory_details']['first_name'], 'Verifier')
        
        # Verify approver signature
        self.assertEqual(sig_map['approver']['signature_type'], 'approver')
        self.assertEqual(sig_map['approver']['signatory_details']['first_name'], 'Approver')
    
    def test_signature_mapping_with_missing_types(self):
        """Test signature mapping when some signature types are missing"""
        # Create only requestor signature
        DigitalSignature.objects.create(
            permit=self.permit,
            signature_type='requestor',
            signatory=self.user,
            signature_data='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/', follow=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        sig_map = response.data['signatures_by_type']
        self.assertIn('requestor', sig_map)
        self.assertIsNone(sig_map.get('verifier'))
        self.assertIsNone(sig_map.get('approver'))
    
    def test_signature_data_format(self):
        """Test that signature data is properly formatted"""
        DigitalSignature.objects.create(
            permit=self.permit,
            signature_type='requestor',
            signatory=self.user,
            signature_data='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/', follow=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        sig_map = response.data['signatures_by_type']
        requestor_sig = sig_map['requestor']
        
        # Verify signature data is included
        self.assertIn('signature_data', requestor_sig)
        self.assertTrue(requestor_sig['signature_data'].startswith('data:image'))
    
    def test_no_null_name_parts(self):
        """Test that signatory names don't have null parts"""
        # Create user with only first name
        user_no_surname = User.objects.create_user(
            username='nosurname',
            email='nosurname@example.com',
            password='pass',
            name='OnlyFirst',
            surname='',
            user_type='employee'
        )
        
        DigitalSignature.objects.create(
            permit=self.permit,
            signature_type='requestor',
            signatory=user_no_surname,
            signature_data='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
        )
        
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/', follow=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        sig_map = response.data['signatures_by_type']
        requestor_sig = sig_map['requestor']
        
        # Verify name doesn't contain "null" or "None"
        signatory_details = requestor_sig['signatory_details']
        full_name = f"{signatory_details.get('first_name', '')} {signatory_details.get('last_name', '')}".strip()
        
        self.assertNotIn('null', full_name.lower())
        self.assertNotIn('none', full_name.lower())
        self.assertEqual(full_name, 'OnlyFirst')
