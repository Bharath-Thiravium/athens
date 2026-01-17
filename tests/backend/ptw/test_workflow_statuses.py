"""
Tests for PTW workflow status transitions and validation
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ptw.models import Permit, PermitType, WorkflowInstance, WorkflowStep
from ptw.workflow_manager import workflow_manager
from authentication.models import Project

User = get_user_model()


class WorkflowStatusTestCase(TestCase):
    """Test workflow status transitions and validation"""
    
    def setUp(self):
        """Set up test data"""
        # Create project
        self.project = Project.objects.create(
            name='Test Project',
            project_code='TEST001'
        )
        
        # Create users
        self.requestor = User.objects.create_user(
            username='requestor',
            email='requestor@test.com',
            password='test123',
            admin_type='contractoruser',
            grade='C',
            project=self.project
        )
        
        self.verifier = User.objects.create_user(
            username='verifier',
            email='verifier@test.com',
            password='test123',
            admin_type='epcuser',
            grade='B',
            project=self.project
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@test.com',
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
        
        # Create permit
        self.permit = Permit.objects.create(
            permit_type=self.permit_type,
            description='Test hot work permit',
            location='Test Location',
            planned_start_time=timezone.now(),
            planned_end_time=timezone.now() + timedelta(hours=8),
            created_by=self.requestor,
            project=self.project,
            status='draft'
        )
    
    def test_permit_status_choices_include_new_statuses(self):
        """Test that Permit.STATUS_CHOICES includes new workflow statuses"""
        status_values = [choice[0] for choice in Permit.STATUS_CHOICES]
        
        self.assertIn('pending_verification', status_values)
        self.assertIn('pending_approval', status_values)
        self.assertIn('draft', status_values)
        self.assertIn('submitted', status_values)
        self.assertIn('under_review', status_values)
        self.assertIn('approved', status_values)
    
    def test_workflowstep_status_choices_include_obsolete(self):
        """Test that WorkflowStep.STATUS_CHOICES includes obsolete"""
        status_values = [choice[0] for choice in WorkflowStep.STATUS_CHOICES]
        
        self.assertIn('obsolete', status_values)
        self.assertIn('pending', status_values)
        self.assertIn('approved', status_values)
        self.assertIn('rejected', status_values)
    
    def test_workflow_initiation_sets_valid_status(self):
        """Test that workflow initiation sets a valid permit status"""
        workflow = workflow_manager.initiate_workflow(self.permit, self.requestor)
        
        self.permit.refresh_from_db()
        
        # Should be pending_verification after workflow initiation
        self.assertEqual(self.permit.status, 'pending_verification')
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.permit, self.permit)
    
    def test_workflowstep_can_be_set_to_obsolete(self):
        """Test that WorkflowStep status can be set to obsolete without error"""
        workflow = WorkflowInstance.objects.create(
            permit=self.permit,
            current_step=1,
            status='active'
        )
        
        step = WorkflowStep.objects.create(
            workflow=workflow,
            step_id='test_step',
            name='Test Step',
            step_type='approval',
            assignee=self.approver,
            role='approver',
            order=1,
            status='pending'
        )
        
        # Should not raise validation error
        step.status = 'obsolete'
        step.save()
        
        step.refresh_from_db()
        self.assertEqual(step.status, 'obsolete')
    
    def test_permit_status_transitions_with_new_statuses(self):
        """Test permit status transitions include new workflow states"""
        # Draft -> Submitted
        self.assertTrue(self.permit.can_transition_to('submitted'))
        
        # Submitted -> Pending Verification
        self.permit.status = 'submitted'
        self.assertTrue(self.permit.can_transition_to('pending_verification'))
        
        # Pending Verification -> Under Review
        self.permit.status = 'pending_verification'
        self.assertTrue(self.permit.can_transition_to('under_review'))
        
        # Under Review -> Pending Approval
        self.permit.status = 'under_review'
        self.assertTrue(self.permit.can_transition_to('pending_approval'))
        
        # Pending Approval -> Approved
        self.permit.status = 'pending_approval'
        self.assertTrue(self.permit.can_transition_to('approved'))
        
        # Approved -> Active
        self.permit.status = 'approved'
        self.assertTrue(self.permit.can_transition_to('active'))
    
    def test_workflow_verification_sets_pending_approval(self):
        """Test that workflow verification sets pending_approval status"""
        # Initialize workflow
        workflow = workflow_manager.initiate_workflow(self.permit, self.requestor)
        
        # Assign verifier
        workflow_manager.assign_verifier(self.permit, self.verifier, self.requestor)
        
        # Verify permit with approver selection
        workflow_manager.verify_permit(
            self.permit,
            self.verifier,
            'approve',
            'Looks good',
            self.approver
        )
        
        self.permit.refresh_from_db()
        self.assertEqual(self.permit.status, 'pending_approval')
    
    def test_workflow_approval_sets_approved_status(self):
        """Test that workflow approval sets approved status"""
        # Initialize workflow
        workflow = workflow_manager.initiate_workflow(self.permit, self.requestor)
        
        # Assign verifier
        workflow_manager.assign_verifier(self.permit, self.verifier, self.requestor)
        
        # Verify permit
        workflow_manager.verify_permit(
            self.permit,
            self.verifier,
            'approve',
            'Verified',
            self.approver
        )
        
        # Approve permit
        workflow_manager.approve_permit(
            self.permit,
            self.approver,
            'approve',
            'Approved'
        )
        
        self.permit.refresh_from_db()
        self.assertEqual(self.permit.status, 'approved')
    
    def test_parallel_approval_marks_other_steps_obsolete(self):
        """Test that approving marks other pending approval steps as obsolete"""
        # Create workflow with multiple approval steps
        workflow = WorkflowInstance.objects.create(
            permit=self.permit,
            current_step=3,
            status='active'
        )
        
        approver2 = User.objects.create_user(
            username='approver2',
            email='approver2@test.com',
            password='test123',
            admin_type='clientuser',
            grade='A',
            project=self.project
        )
        
        step1 = WorkflowStep.objects.create(
            workflow=workflow,
            step_id='approval',
            name='Approval 1',
            step_type='approval',
            assignee=self.approver,
            role='epcuser_approver',
            order=3,
            status='pending'
        )
        
        step2 = WorkflowStep.objects.create(
            workflow=workflow,
            step_id='approval',
            name='Approval 2',
            step_type='approval',
            assignee=approver2,
            role='clientuser_approver',
            order=3,
            status='pending'
        )
        
        self.permit.status = 'pending_approval'
        self.permit.save()
        
        # First approver approves
        workflow_manager.approve_permit(
            self.permit,
            self.approver,
            'approve',
            'Approved'
        )
        
        # Check that other step is marked obsolete
        step2.refresh_from_db()
        self.assertEqual(step2.status, 'obsolete')
