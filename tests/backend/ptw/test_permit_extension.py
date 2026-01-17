"""
Tests for PermitExtension model and work nature change logic
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, time, datetime
from ptw.models import Permit, PermitType, PermitExtension
from authentication.models import Project

User = get_user_model()


class PermitExtensionTestCase(TestCase):
    """Test PermitExtension model behavior"""
    
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
        
        # Create permit type
        self.permit_type = PermitType.objects.create(
            name='Hot Work',
            category='hot_work',
            risk_level='high'
        )
        
        # Create base permit
        now = timezone.now()
        self.permit = Permit.objects.create(
            permit_type=self.permit_type,
            description='Test permit',
            location='Test Location',
            planned_start_time=now,
            planned_end_time=now + timedelta(hours=8),
            created_by=self.user,
            project=self.project,
            status='active',
            work_nature='day'
        )
    
    def test_extension_save_does_not_crash(self):
        """Test that PermitExtension.save() does not crash with non-existent fields"""
        original_end = self.permit.planned_end_time
        new_end = original_end + timedelta(hours=4)
        
        extension = PermitExtension(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Need more time'
        )
        
        # Should not raise exception
        extension.save()
        
        # Verify extension_hours calculated correctly
        self.assertEqual(extension.extension_hours, 4)
    
    def test_extension_hours_calculated_correctly(self):
        """Test that extension_hours is auto-calculated"""
        original_end = self.permit.planned_end_time
        new_end = original_end + timedelta(hours=6)
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Extended work'
        )
        
        self.assertEqual(extension.extension_hours, 6)
    
    def test_affects_work_nature_day_to_night(self):
        """Test affects_work_nature when extending from day into night hours"""
        # Day work ending at 7 PM (19:00) - after day_end (18:00)
        base_date = timezone.now().date()
        original_end = timezone.make_aware(datetime.combine(base_date, time(17, 0)))
        new_end = timezone.make_aware(datetime.combine(base_date, time(19, 0)))
        
        self.permit.work_nature = 'day'
        self.permit.planned_end_time = original_end
        self.permit.save()
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Extended into night'
        )
        
        # Should detect work nature change (day work extending past 6 PM)
        self.assertTrue(extension.affects_work_nature)
    
    def test_no_affects_work_nature_within_same_window(self):
        """Test affects_work_nature stays False when extension within same work window"""
        # Day work: 10 AM to 2 PM (both within day hours 8 AM - 6 PM)
        base_date = timezone.now().date()
        original_end = timezone.make_aware(datetime.combine(base_date, time(14, 0)))
        new_end = timezone.make_aware(datetime.combine(base_date, time(16, 0)))
        
        self.permit.work_nature = 'day'
        self.permit.planned_end_time = original_end
        self.permit.save()
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Extended within day'
        )
        
        # Should NOT detect work nature change (still within day hours)
        self.assertFalse(extension.affects_work_nature)
    
    def test_affects_work_nature_night_to_day(self):
        """Test affects_work_nature when night work extends into day hours"""
        # Night work ending at 9 AM (within day hours 8 AM - 6 PM)
        base_date = timezone.now().date()
        original_end = timezone.make_aware(datetime.combine(base_date, time(5, 0)))
        new_end = timezone.make_aware(datetime.combine(base_date, time(9, 0)))
        
        self.permit.work_nature = 'night'
        self.permit.planned_end_time = original_end
        self.permit.save()
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Extended into day'
        )
        
        # Should detect work nature change (night work extending into day hours)
        self.assertTrue(extension.affects_work_nature)
    
    def test_both_work_nature_no_change(self):
        """Test that 'both' work nature does not trigger affects_work_nature"""
        base_date = timezone.now().date()
        original_end = timezone.make_aware(datetime.combine(base_date, time(17, 0)))
        new_end = timezone.make_aware(datetime.combine(base_date, time(22, 0)))
        
        self.permit.work_nature = 'both'
        self.permit.planned_end_time = original_end
        self.permit.save()
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Extended work'
        )
        
        # 'both' work nature should not trigger affects_work_nature
        self.assertFalse(extension.affects_work_nature)
    
    def test_extension_with_new_work_nature_field(self):
        """Test extension with explicit new_work_nature field"""
        original_end = self.permit.planned_end_time
        new_end = original_end + timedelta(hours=4)
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            new_work_nature='night',
            reason='Changing to night work'
        )
        
        # Should save without error
        self.assertEqual(extension.new_work_nature, 'night')
        self.assertEqual(extension.extension_hours, 4)
    
    def test_extension_status_workflow(self):
        """Test extension status transitions"""
        original_end = self.permit.planned_end_time
        new_end = original_end + timedelta(hours=2)
        
        extension = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=new_end,
            reason='Need extension',
            status='pending'
        )
        
        self.assertEqual(extension.status, 'pending')
        
        # Approve extension
        extension.status = 'approved'
        extension.approved_by = self.user
        extension.approved_at = timezone.now()
        extension.save()
        
        self.assertEqual(extension.status, 'approved')
        self.assertIsNotNone(extension.approved_at)
    
    def test_multiple_extensions_for_same_permit(self):
        """Test that multiple extensions can be created for same permit"""
        original_end = self.permit.planned_end_time
        
        # First extension
        ext1 = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end,
            new_end_time=original_end + timedelta(hours=2),
            reason='First extension'
        )
        
        # Second extension
        ext2 = PermitExtension.objects.create(
            permit=self.permit,
            requested_by=self.user,
            original_end_time=original_end + timedelta(hours=2),
            new_end_time=original_end + timedelta(hours=4),
            reason='Second extension'
        )
        
        self.assertEqual(self.permit.extensions.count(), 2)
        self.assertEqual(ext1.extension_hours, 2)
        self.assertEqual(ext2.extension_hours, 2)
