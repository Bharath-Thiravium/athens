"""
Tests for PermitType requirements enforcement
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError
from ptw.models import Permit, PermitType, PermitExtension, GasReading
from ptw.validators import validate_permit_requirements, validate_extension_limit
from ptw.serializers import PermitStatusUpdateSerializer, PermitExtensionSerializer
from authentication.models import Project

User = get_user_model()


class PermitTypeRequirementsTestCase(TestCase):
    """Test PermitType requirements enforcement"""
    
    def setUp(self):
        """Set up test data"""
        # Create project
        self.project = Project.objects.create(
            name='Test Project',
            project_code='TEST001'
        )
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='test123',
            admin_type='epcuser',
            grade='A',
            project=self.project
        )
        
        # Create permit type with requirements
        self.permit_type_with_requirements = PermitType.objects.create(
            name='Confined Space',
            category='confined_space',
            risk_level='high',
            requires_gas_testing=True,
            requires_isolation=True,
            mandatory_ppe=['Helmet', 'Gloves', 'Safety Harness'],
            safety_checklist=[
                {'key': 'fire_extinguisher', 'label': 'Fire extinguisher available', 'required': True},
                {'key': 'barricading', 'label': 'Barricading done', 'required': True}
            ],
            max_validity_extensions=2
        )
        
        # Create permit type without requirements
        self.permit_type_simple = PermitType.objects.create(
            name='Cold Work',
            category='cold_work',
            risk_level='low'
        )
        
        # Create base permit
        now = timezone.now()
        self.permit = Permit.objects.create(
            permit_type=self.permit_type_with_requirements,
            description='Test permit',
            location='Test Location',
            planned_start_time=now,
            planned_end_time=now + timedelta(hours=8),
            created_by=self.user,
            project=self.project,
            status='pending_approval'
        )
    
    def test_gas_testing_required_blocks_approve_without_safe_reading(self):
        """Test that gas testing requirement blocks approval without safe reading"""
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='approval')
        
        self.assertIn('gas_readings', context.exception.detail)
        self.assertIn('Gas testing is required', str(context.exception.detail['gas_readings']))
    
    def test_gas_testing_passes_with_safe_reading(self):
        """Test that gas testing requirement passes with safe reading"""
        # Add safe gas reading
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        
        # Should not raise exception
        try:
            validate_permit_requirements(self.permit, action='approval')
        except ValidationError:
            self.fail("validate_permit_requirements raised ValidationError unexpectedly")
    
    def test_isolation_required_blocks_approve_without_details(self):
        """Test that isolation requirement blocks approval without details"""
        # Add gas reading to pass that check
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='approval')
        
        self.assertIn('isolation_details', context.exception.detail)
    
    def test_isolation_passes_with_details(self):
        """Test that isolation requirement passes with details"""
        # Add gas reading
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        
        # Add isolation details
        self.permit.isolation_details = 'Electrical isolation completed, LOTO applied'
        self.permit.save()
        
        # Should still fail on PPE and checklist
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='approval')
        
        # But isolation should not be in errors
        self.assertNotIn('isolation_details', context.exception.detail)
    
    def test_mandatory_ppe_blocks_approve_if_missing(self):
        """Test that mandatory PPE blocks approval if missing"""
        # Add gas reading and isolation
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        self.permit.isolation_details = 'Isolation completed'
        self.permit.ppe_requirements = ['Helmet']  # Missing Gloves and Safety Harness
        self.permit.save()
        
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='approval')
        
        self.assertIn('ppe_requirements', context.exception.detail)
        error_msg = str(context.exception.detail['ppe_requirements'])
        self.assertIn('Gloves', error_msg)
        self.assertIn('Safety Harness', error_msg)
    
    def test_mandatory_ppe_passes_with_all_items(self):
        """Test that mandatory PPE passes when all items present"""
        # Add gas reading and isolation
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        self.permit.isolation_details = 'Isolation completed'
        self.permit.ppe_requirements = ['Helmet', 'Gloves', 'Safety Harness']
        self.permit.save()
        
        # Should still fail on checklist
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='approval')
        
        # But PPE should not be in errors
        self.assertNotIn('ppe_requirements', context.exception.detail)
    
    def test_checklist_blocks_approve_if_incomplete(self):
        """Test that safety checklist blocks approval if incomplete"""
        # Add gas reading, isolation, and PPE
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        self.permit.isolation_details = 'Isolation completed'
        self.permit.ppe_requirements = ['Helmet', 'Gloves', 'Safety Harness']
        self.permit.safety_checklist = {'fire_extinguisher': True}  # Missing barricading
        self.permit.save()
        
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='approval')
        
        self.assertIn('safety_checklist', context.exception.detail)
        self.assertIn('Barricading done', str(context.exception.detail['safety_checklist']))
    
    def test_checklist_passes_when_complete(self):
        """Test that safety checklist passes when complete"""
        # Add all requirements
        GasReading.objects.create(
            permit=self.permit,
            gas_type='O2',
            reading=20.9,
            unit='%',
            acceptable_range='19.5-23.5',
            status='safe',
            tested_by=self.user
        )
        self.permit.isolation_details = 'Isolation completed'
        self.permit.ppe_requirements = ['Helmet', 'Gloves', 'Safety Harness']
        self.permit.safety_checklist = {
            'fire_extinguisher': True,
            'barricading': True
        }
        self.permit.save()
        
        # Should not raise exception
        try:
            validate_permit_requirements(self.permit, action='approval')
        except ValidationError:
            self.fail("validate_permit_requirements raised ValidationError unexpectedly")
    
    def test_requirements_not_enforced_on_draft_save(self):
        """Test that requirements are not enforced when saving draft"""
        # Create draft permit without any requirements met
        draft_permit = Permit.objects.create(
            permit_type=self.permit_type_with_requirements,
            description='Draft permit',
            location='Test Location',
            planned_start_time=timezone.now(),
            planned_end_time=timezone.now() + timedelta(hours=8),
            created_by=self.user,
            project=self.project,
            status='draft'
        )
        
        # Should save without error
        draft_permit.save()
        self.assertEqual(draft_permit.status, 'draft')
    
    def test_status_update_serializer_enforces_requirements_on_approve(self):
        """Test that PermitStatusUpdateSerializer enforces requirements on approve"""
        # Try to approve without meeting requirements
        serializer = PermitStatusUpdateSerializer(
            instance=self.permit,
            data={'status': 'approved'},
            partial=True
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('gas_readings', serializer.errors)
    
    def test_status_update_serializer_allows_draft_without_requirements(self):
        """Test that PermitStatusUpdateSerializer allows draft without requirements"""
        self.permit.status = 'submitted'
        self.permit.save()
        
        serializer = PermitStatusUpdateSerializer(
            instance=self.permit,
            data={'status': 'draft'},
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_max_validity_extensions_blocks_creation_when_limit_reached(self):
        """Test that max_validity_extensions blocks creation when limit reached"""
        # Create 2 extensions (reaching the limit)
        for i in range(2):
            PermitExtension.objects.create(
                permit=self.permit,
                requested_by=self.user,
                original_end_time=self.permit.planned_end_time,
                new_end_time=self.permit.planned_end_time + timedelta(hours=2),
                reason=f'Extension {i+1}',
                status='approved'
            )
        
        # Try to create third extension
        with self.assertRaises(ValidationError) as context:
            validate_extension_limit(self.permit)
        
        self.assertIn('permit', context.exception.detail)
        self.assertIn('Maximum validity extensions', str(context.exception.detail['permit']))
    
    def test_rejected_extensions_not_counted(self):
        """Test that rejected extensions are not counted toward limit"""
        # Create 2 approved extensions
        for i in range(2):
            PermitExtension.objects.create(
                permit=self.permit,
                requested_by=self.user,
                original_end_time=self.permit.planned_end_time,
                new_end_time=self.permit.planned_end_time + timedelta(hours=2),
                reason=f'Extension {i+1}',
                status='approved'
            )
        
        # Create 1 rejected extension
        PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=self.permit.planned_end_time,
            new_end_time=self.permit.planned_end_time + timedelta(hours=2),
            reason='Rejected extension',
            status='rejected'
        )
        
        # Should still block (2 approved = limit reached)
        with self.assertRaises(ValidationError):
            validate_extension_limit(self.permit)
    
    def test_pending_extensions_counted_toward_limit(self):
        """Test that pending extensions are counted toward limit"""
        # Create 1 approved and 1 pending extension
        PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=self.permit.planned_end_time,
            new_end_time=self.permit.planned_end_time + timedelta(hours=2),
            reason='Extension 1',
            status='approved'
        )
        PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=self.permit.planned_end_time,
            new_end_time=self.permit.planned_end_time + timedelta(hours=2),
            reason='Extension 2',
            status='pending'
        )
        
        # Should block (2 non-rejected = limit reached)
        with self.assertRaises(ValidationError):
            validate_extension_limit(self.permit)
    
    def test_extension_serializer_enforces_limit(self):
        """Test that PermitExtensionSerializer enforces max_validity_extensions"""
        # Create 2 extensions
        for i in range(2):
            PermitExtension.objects.create(
                permit=self.permit,
                requested_by=self.user,
                original_end_time=self.permit.planned_end_time,
                new_end_time=self.permit.planned_end_time + timedelta(hours=2),
                reason=f'Extension {i+1}',
                status='approved'
            )
        
        # Try to create third via serializer
        serializer = PermitExtensionSerializer(data={
            'permit': self.permit.id,
            'requested_by': self.user.id,
            'original_end_time': self.permit.planned_end_time,
            'new_end_time': self.permit.planned_end_time + timedelta(hours=2),
            'reason': 'Extension 3'
        })
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('permit', serializer.errors)
    
    def test_no_requirements_for_simple_permit_type(self):
        """Test that permit types without requirements don't block approval"""
        simple_permit = Permit.objects.create(
            permit_type=self.permit_type_simple,
            description='Simple permit',
            location='Test Location',
            planned_start_time=timezone.now(),
            planned_end_time=timezone.now() + timedelta(hours=8),
            created_by=self.user,
            project=self.project,
            status='pending_approval'
        )
        
        # Should not raise exception
        try:
            validate_permit_requirements(simple_permit, action='approval')
        except ValidationError:
            self.fail("validate_permit_requirements raised ValidationError unexpectedly")
    
    def test_requirements_block_activation_if_missing(self):
        """Test that requirements block activation if missing"""
        with self.assertRaises(ValidationError) as context:
            validate_permit_requirements(self.permit, action='activation')
        
        self.assertIn('gas_readings', context.exception.detail)
        self.assertIn('activation', str(context.exception.detail['gas_readings']))
