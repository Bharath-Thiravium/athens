"""
Tests for PTW readiness endpoint (PR15)
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from authentication.models import Project
from ptw.models import Permit, PermitType, GasReading, PermitIsolationPoint, IsolationPointLibrary
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class PermitReadinessTestCase(TestCase):
    """Test permit readiness endpoint"""
    
    def setUp(self):
        self.project = Project.objects.create(name='Test Project', code='TEST')
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            project=self.project
        )
        
        # Create permit type with requirements
        self.permit_type = PermitType.objects.create(
            name='Hot Work',
            category='hot_work',
            risk_level='high',
            requires_gas_testing=True,
            requires_structured_isolation=True
        )
        
        self.permit = Permit.objects.create(
            permit_number='PTW-TEST-001',
            title='Test Permit',
            location='Test Location',
            permit_type=self.permit_type,
            project=self.project,
            created_by=self.user,
            status='under_review',
            planned_start_time=timezone.now(),
            planned_end_time=timezone.now() + timedelta(days=1)
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_readiness_endpoint_exists(self):
        """Test readiness endpoint is accessible"""
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('permit_id', response.data)
        self.assertIn('readiness', response.data)
        self.assertIn('missing', response.data)
        self.assertIn('details', response.data)
    
    def test_readiness_shows_missing_gas_readings(self):
        """Test readiness shows missing gas readings when required"""
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['requires']['gas_testing'])
        self.assertFalse(response.data['readiness']['can_approve'])
        self.assertIn('gas_readings_missing', response.data['missing']['approve'])
        self.assertFalse(response.data['details']['gas']['safe'])
    
    def test_readiness_shows_isolation_pending(self):
        """Test readiness shows isolation pending when structured isolation enabled"""
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['requires']['structured_isolation'])
        self.assertFalse(response.data['readiness']['can_approve'])
        self.assertIn('isolation_points_not_assigned', response.data['missing']['approve'])
    
    def test_readiness_with_safe_gas_reading(self):
        """Test readiness when safe gas reading exists"""
        GasReading.objects.create(
            permit=self.permit,
            gas_type='oxygen',
            reading_value=20.9,
            status='safe',
            tested_by=self.user,
            tested_at=timezone.now()
        )
        
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['details']['gas']['safe'])
        # Should still fail on isolation
        self.assertFalse(response.data['readiness']['can_approve'])
    
    def test_readiness_with_verified_isolation(self):
        """Test readiness when isolation points are verified"""
        # Add safe gas reading
        GasReading.objects.create(
            permit=self.permit,
            gas_type='oxygen',
            reading_value=20.9,
            status='safe',
            tested_by=self.user,
            tested_at=timezone.now()
        )
        
        # Create and verify isolation point
        library_point = IsolationPointLibrary.objects.create(
            project=self.project,
            point_code='ISO-001',
            point_type='valve',
            energy_type='electrical',
            location='Test Location'
        )
        
        PermitIsolationPoint.objects.create(
            permit=self.permit,
            point=library_point,
            required=True,
            status='verified',
            isolated_by=self.user,
            isolated_at=timezone.now(),
            verified_by=self.user,
            verified_at=timezone.now()
        )
        
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['readiness']['can_approve'])
        self.assertEqual(len(response.data['missing']['approve']), 0)
        self.assertEqual(response.data['details']['isolation']['verified_required'], 1)
    
    def test_readiness_respects_project_scoping(self):
        """Test readiness endpoint respects project scoping"""
        # Create another project and user
        other_project = Project.objects.create(name='Other Project', code='OTHER')
        other_user = User.objects.create_user(
            username='otheruser',
            password='pass123',
            project=other_project
        )
        
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        # Should get 404 or 403
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_readiness_response_structure(self):
        """Test readiness response has all required keys"""
        response = self.client.get(f'/api/v1/ptw/permits/{self.permit.id}/readiness/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check top-level keys
        required_keys = ['permit_id', 'permit_number', 'status', 'requires', 'readiness', 'missing', 'details']
        for key in required_keys:
            self.assertIn(key, response.data)
        
        # Check requires keys
        self.assertIn('gas_testing', response.data['requires'])
        self.assertIn('structured_isolation', response.data['requires'])
        self.assertIn('closeout', response.data['requires'])
        
        # Check readiness keys
        self.assertIn('can_verify', response.data['readiness'])
        self.assertIn('can_approve', response.data['readiness'])
        self.assertIn('can_activate', response.data['readiness'])
        self.assertIn('can_complete', response.data['readiness'])
        
        # Check missing keys
        self.assertIn('approve', response.data['missing'])
        self.assertIn('activate', response.data['missing'])
        self.assertIn('complete', response.data['missing'])
        
        # Check details keys
        self.assertIn('gas', response.data['details'])
        self.assertIn('isolation', response.data['details'])
        self.assertIn('ppe', response.data['details'])
        self.assertIn('checklist', response.data['details'])
        self.assertIn('closeout', response.data['details'])
