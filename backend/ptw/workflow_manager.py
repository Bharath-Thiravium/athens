from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Permit, WorkflowInstance, WorkflowStep, PermitAudit
from authentication.models import CustomUser
from authentication.models_notification import Notification
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class PTWWorkflowManager:
    """
    Manages PTW workflow with 3 stages: Creator → Verifier → Approver
    
    Workflow Rules:
    1. Contractor (any grade) creates PTW → Auto-sends to EPC C-grade for verification
    2. EPC/Client creates PTW → Can select verifier (EPC/Client with grade selection)
    3. Verifier verifies → Selects approver (EPC/Client with grade selection)
    4. Approver approves → PTW becomes active
    5. Rejection at any stage → Returns to previous stage
    """
    
    WORKFLOW_STAGES = {
        'CREATED': 'created',
        'VERIFICATION': 'verification',
        'APPROVAL': 'approval',
        'APPROVED': 'approved',
        'REJECTED': 'rejected',
        'ACTIVE': 'active'
    }
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    @transaction.atomic
    def initiate_workflow(self, permit, creator):
        """Initialize workflow based on creator's role"""
        try:
            # Create workflow instance
            workflow = WorkflowInstance.objects.create(
                permit=permit,
                template=None,  # We'll use dynamic workflow
                current_step=1,
                status='active'
            )
            
            # Determine workflow path based on creator type
            if creator.admin_type == 'contractoruser':
                # Contractor creates → Auto-send to EPC C-grade for verification
                self._create_contractor_workflow(workflow, creator)
            else:
                # EPC/Client creates → Manual selection for verification
                self._create_admin_workflow(workflow, creator)
            
            # Update permit status
            permit.status = 'submitted'
            permit.submitted_at = timezone.now()
            permit.save()
            
            # Create audit log
            self._create_audit_log(permit, 'workflow_initiated', creator, 
                                 f"Workflow initiated by {creator.get_full_name()}")
            
            return workflow
            
        except Exception as e:
            logger.error(f"Error initiating workflow for permit {permit.permit_number}: {str(e)}")
            raise
    
    def _create_contractor_workflow(self, workflow, creator):
        """Create workflow for contractor-created permits"""
        # Step 1: Auto-assign to EPC C-grade users for verification
        epc_c_users = self._get_epc_c_grade_users(creator.project)
        
        if not epc_c_users.exists():
            # Fallback: assign to any EPC user if no C-grade users exist
            epc_c_users = CustomUser.objects.filter(
                project=creator.project,
                admin_type='epcuser',
                is_active=True
            )
            
            if not epc_c_users.exists():
                raise ValueError("No EPC users available for verification")
        
        # Create verification step - assign to all EPC C-grade users
        for user in epc_c_users:
            WorkflowStep.objects.create(
                workflow=workflow,
                step_id='verification',
                name='Permit Verification',
                step_type='verification',
                assignee=user,
                role='epc_c_verifier',
                order=1,
                escalation_time=4,  # 4 hours
                required=True
            )
        
        # Send notifications
        self._send_verification_notifications(workflow.permit, epc_c_users, creator)
    
    def _create_admin_workflow(self, workflow, creator):
        """Create workflow for EPC/Client created permits - requires manual selection"""
        # Create pending verification step - will be assigned when user selects verifier
        WorkflowStep.objects.create(
            workflow=workflow,
            step_id='verification_pending',
            name='Select Verifier',
            step_type='selection',
            assignee=creator,
            role='creator',
            order=1,
            required=True,
            status='pending'
        )
    
    @transaction.atomic
    def assign_verifier(self, permit, verifier, assigned_by):
        """Assign verifier to permit (for EPC/Client created permits)"""
        try:
            workflow = permit.workflow
            
            # Update or create verification step
            verification_step, created = WorkflowStep.objects.get_or_create(
                workflow=workflow,
                step_id='verification',
                defaults={
                    'name': 'Permit Verification',
                    'step_type': 'verification',
                    'assignee': verifier,
                    'role': f"{verifier.admin_type}_{verifier.grade}_verifier",
                    'order': 1,
                    'escalation_time': 4,
                    'required': True
                }
            )
            
            if not created:
                verification_step.assignee = verifier
                verification_step.role = f"{verifier.admin_type}_{verifier.grade}_verifier"
                verification_step.status = 'pending'
                verification_step.save()
            
            # Remove pending selection step
            WorkflowStep.objects.filter(
                workflow=workflow,
                step_id='verification_pending'
            ).delete()
            
            # Update permit status
            permit.status = 'under_review'
            permit.save()
            
            # Send notification to verifier
            self._send_verification_notifications(permit, [verifier], assigned_by)
            
            # Create audit log
            self._create_audit_log(permit, 'verifier_assigned', assigned_by,
                                 f"Verifier assigned: {verifier.get_full_name()}")
            
            return verification_step
            
        except Exception as e:
            logger.error(f"Error assigning verifier for permit {permit.permit_number}: {str(e)}")
            raise
    
    @transaction.atomic
    def verify_permit_to_grade(self, permit, verifier, action, comments='', user_type=None, grade=None):
        """Handle permit verification and send to all users of selected grade"""
        try:
            workflow = permit.workflow
            verification_step = WorkflowStep.objects.get(
                workflow=workflow,
                step_id='verification',
                assignee=verifier
            )
            
            if action == 'approve':
                # Verification approved
                verification_step.status = 'approved'
                verification_step.completed_at = timezone.now()
                verification_step.comments = comments
                verification_step.save()
                
                # Get all users of selected grade
                approvers = CustomUser.objects.filter(
                    project=permit.project,
                    admin_type=user_type,
                    grade=grade,
                    is_active=True
                )
                
                if not approvers.exists():
                    raise ValueError(f"No {user_type} Grade {grade} users found for approval")
                
                # Create approval steps for all users of the grade
                for approver in approvers:
                    WorkflowStep.objects.create(
                        workflow=workflow,
                        step_id='approval',
                        name='Permit Approval',
                        step_type='approval',
                        assignee=approver,
                        role=f"{approver.admin_type}_{approver.grade}_approver",
                        order=2,
                        escalation_time=2,  # 2 hours
                        required=True
                    )
                
                # Update workflow current step
                workflow.current_step = 2
                workflow.save()
                
                # Send notifications to all approvers
                self._send_approval_notifications(permit, approvers, verifier)
                
                # Update permit status and verifier info
                permit.status = 'pending_approval'
                permit.verifier = verifier
                permit.verified_at = timezone.now()
                permit.verification_comments = comments
                permit.save()
                
                # Create audit log
                self._create_audit_log(permit, 'verified', verifier,
                                     f"Permit verified and sent to all {user_type} Grade {grade} users for approval")
            
            elif action == 'reject':
                # Verification rejected
                verification_step.status = 'rejected'
                verification_step.completed_at = timezone.now()
                verification_step.comments = comments
                verification_step.save()
                
                # Update permit status
                permit.status = 'rejected'
                permit.save()
                
                # Send rejection notification to creator
                self._send_rejection_notifications(permit, permit.created_by, verifier, comments)
                
                # Create audit log
                self._create_audit_log(permit, 'verification_rejected', verifier,
                                     f"Permit verification rejected: {comments}")
            
            return verification_step
            
        except Exception as e:
            logger.error(f"Error verifying permit {permit.permit_number}: {str(e)}")
            raise
    
    @transaction.atomic
    def verify_permit(self, permit, verifier, action, comments='', selected_approver=None):
        """Handle permit verification"""
        try:
            workflow = permit.workflow
            verification_step = WorkflowStep.objects.get(
                workflow=workflow,
                step_id='verification',
                assignee=verifier
            )
            
            if action == 'approve':
                # Verification approved
                verification_step.status = 'approved'
                verification_step.completed_at = timezone.now()
                verification_step.comments = comments
                verification_step.save()
                
                if selected_approver:
                    # Create approval step
                    approval_step = WorkflowStep.objects.create(
                        workflow=workflow,
                        step_id='approval',
                        name='Permit Approval',
                        step_type='approval',
                        assignee=selected_approver,
                        role=f"{selected_approver.admin_type}_{selected_approver.grade}_approver",
                        order=2,
                        escalation_time=2,  # 2 hours
                        required=True
                    )
                    
                    # Update workflow current step
                    workflow.current_step = 2
                    workflow.save()
                    
                    # Send notification to approver
                    self._send_approval_notifications(permit, [selected_approver], verifier)
                    
                    # Update permit status
                    permit.status = 'pending_approval'
                    permit.save()
                    
                    # Create audit log
                    self._create_audit_log(permit, 'verified', verifier,
                                         f"Permit verified and sent to {selected_approver.get_full_name()} for approval")
                else:
                    # No approver selected - create pending approval selection
                    WorkflowStep.objects.create(
                        workflow=workflow,
                        step_id='approval_pending',
                        name='Select Approver',
                        step_type='selection',
                        assignee=verifier,
                        role='verifier',
                        order=2,
                        required=True
                    )
                    
                    permit.status = 'verified_pending_approver'
                    permit.save()
            
            elif action == 'reject':
                # Verification rejected
                verification_step.status = 'rejected'
                verification_step.completed_at = timezone.now()
                verification_step.comments = comments
                verification_step.save()
                
                # Update permit status
                permit.status = 'rejected'
                permit.save()
                
                # Send rejection notification to creator
                self._send_rejection_notifications(permit, permit.created_by, verifier, comments)
                
                # Create audit log
                self._create_audit_log(permit, 'verification_rejected', verifier,
                                     f"Permit verification rejected: {comments}")
            
            return verification_step
            
        except Exception as e:
            logger.error(f"Error verifying permit {permit.permit_number}: {str(e)}")
            raise
    
    @transaction.atomic
    def assign_approver(self, permit, approver, assigned_by):
        """Assign approver to verified permit"""
        try:
            workflow = permit.workflow
            
            # Create or update approval step
            approval_step, created = WorkflowStep.objects.get_or_create(
                workflow=workflow,
                step_id='approval',
                defaults={
                    'name': 'Permit Approval',
                    'step_type': 'approval',
                    'assignee': approver,
                    'role': f"{approver.admin_type}_{approver.grade}_approver",
                    'order': 2,
                    'escalation_time': 2,
                    'required': True
                }
            )
            
            if not created:
                approval_step.assignee = approver
                approval_step.role = f"{approver.admin_type}_{approver.grade}_approver"
                approval_step.status = 'pending'
                approval_step.save()
            
            # Remove pending selection step
            WorkflowStep.objects.filter(
                workflow=workflow,
                step_id='approval_pending'
            ).delete()
            
            # Update workflow and permit
            workflow.current_step = 2
            workflow.save()
            
            permit.status = 'pending_approval'
            permit.save()
            
            # Send notification to approver
            self._send_approval_notifications(permit, [approver], assigned_by)
            
            # Create audit log
            self._create_audit_log(permit, 'approver_assigned', assigned_by,
                                 f"Approver assigned: {approver.get_full_name()}")
            
            return approval_step
            
        except Exception as e:
            logger.error(f"Error assigning approver for permit {permit.permit_number}: {str(e)}")
            raise
    
    @transaction.atomic
    def approve_permit(self, permit, approver, action, comments=''):
        """Handle permit approval - first approver wins"""
        try:
            workflow = permit.workflow
            
            # Check if already approved by someone else
            existing_approval = WorkflowStep.objects.filter(
                workflow=workflow,
                step_id='approval',
                status='approved'
            ).first()
            
            if existing_approval:
                # Already approved by someone else
                return {
                    'status': 'already_approved',
                    'approved_by': existing_approval.assignee.get_full_name(),
                    'approved_at': existing_approval.completed_at
                }
            
            # Get current user's approval step
            approval_step = WorkflowStep.objects.get(
                workflow=workflow,
                step_id='approval',
                assignee=approver
            )
            
            if action == 'approve':
                # Approval granted - mark all other approval steps as obsolete
                WorkflowStep.objects.filter(
                    workflow=workflow,
                    step_id='approval',
                    status='pending'
                ).exclude(assignee=approver).update(status='obsolete')
                
                approval_step.status = 'approved'
                approval_step.completed_at = timezone.now()
                approval_step.comments = comments
                approval_step.save()
                
                # Complete workflow
                workflow.status = 'completed'
                workflow.completed_at = timezone.now()
                workflow.save()
                
                # Update permit status
                permit.status = 'approved'
                permit.approved_at = timezone.now()
                permit.approved_by = approver
                permit.approval_comments = comments
                permit.save()
                
                # Send success notification to creator
                self._send_approval_success_notifications(permit, permit.created_by, approver)
                
                # Create audit log
                self._create_audit_log(permit, 'approved', approver,
                                     f"Permit approved: {comments}")
            
            elif action == 'reject':
                # Approval rejected
                approval_step.status = 'rejected'
                approval_step.completed_at = timezone.now()
                approval_step.comments = comments
                approval_step.save()
                
                # Update permit status
                permit.status = 'rejected'
                permit.save()
                
                # Send rejection notification to creator
                self._send_rejection_notifications(permit, permit.created_by, approver, comments)
                
                # Create audit log
                self._create_audit_log(permit, 'approval_rejected', approver,
                                     f"Permit approval rejected: {comments}")
            
            return approval_step
            
        except Exception as e:
            logger.error(f"Error approving permit {permit.permit_number}: {str(e)}")
            raise
    
    def get_available_verifiers(self, project, user_type=None, grade=None):
        """Get available verifiers based on criteria"""
        query = Q(project=project, is_active=True)
        
        if user_type:
            query &= Q(admin_type=user_type)
        if grade:
            query &= Q(grade=grade)
        
        return CustomUser.objects.filter(query)
    
    def get_available_approvers(self, project, user_type=None, grade=None):
        """Get available approvers based on criteria"""
        query = Q(project=project, is_active=True)
        
        if user_type:
            query &= Q(admin_type=user_type)
        if grade:
            query &= Q(grade=grade)
        
        # Approvers should be higher grade than verifiers
        if grade == 'C':
            query &= Q(grade__in=['A', 'B'])
        elif grade == 'B':
            query &= Q(grade='A')
        
        return CustomUser.objects.filter(query)
    
    def _get_epc_c_grade_users(self, project):
        """Get all EPC C-grade users for auto-assignment"""
        return CustomUser.objects.filter(
            project=project,
            admin_type='epcuser',
            grade='C',
            is_active=True
        )
    
    def _send_verification_notifications(self, permit, users, sender):
        """Send verification notifications"""
        for user in users:
            # Create database notification
            Notification.objects.create(
                user=user,
                title='PTW Verification Required',
                message=f'Permit {permit.permit_number} requires your verification',
                notification_type='ptw_verification',
                data={
                    'permit_id': permit.id,
                    'permit_number': permit.permit_number,
                    'sender': sender.get_full_name(),
                    'location': permit.location
                },
                link=f'/dashboard/ptw/view/{permit.id}'
            )
            
            # Send real-time notification
            self._send_realtime_notification(user, {
                'type': 'ptw_verification',
                'permit_id': permit.id,
                'permit_number': permit.permit_number,
                'message': f'New permit verification required: {permit.permit_number}'
            })
    
    def _send_approval_notifications(self, permit, users, sender):
        """Send approval notifications"""
        for user in users:
            # Create database notification
            Notification.objects.create(
                user=user,
                title='PTW Approval Required',
                message=f'Permit {permit.permit_number} requires your approval',
                notification_type='ptw_approval',
                data={
                    'permit_id': permit.id,
                    'permit_number': permit.permit_number,
                    'sender': sender.get_full_name(),
                    'location': permit.location
                },
                link=f'/dashboard/ptw/view/{permit.id}'
            )
            
            # Send real-time notification
            self._send_realtime_notification(user, {
                'type': 'ptw_approval',
                'permit_id': permit.id,
                'permit_number': permit.permit_number,
                'message': f'New permit approval required: {permit.permit_number}'
            })
    
    def _send_rejection_notifications(self, permit, user, rejector, comments):
        """Send rejection notifications"""
        # Create database notification
        Notification.objects.create(
            user=user,
            title='PTW Rejected',
            message=f'Permit {permit.permit_number} has been rejected',
            notification_type='ptw_rejected',
            data={
                'permit_id': permit.id,
                'permit_number': permit.permit_number,
                'rejector': rejector.get_full_name(),
                'comments': comments
            },
            link=f'/dashboard/ptw/view/{permit.id}'
        )
        
        # Send real-time notification
        self._send_realtime_notification(user, {
            'type': 'ptw_rejected',
            'permit_id': permit.id,
            'permit_number': permit.permit_number,
            'message': f'Permit {permit.permit_number} has been rejected'
        })
    
    def _send_approval_success_notifications(self, permit, user, approver):
        """Send approval success notifications"""
        # Create database notification
        Notification.objects.create(
            user=user,
            title='PTW Approved',
            message=f'Permit {permit.permit_number} has been approved',
            notification_type='ptw_approved',
            data={
                'permit_id': permit.id,
                'permit_number': permit.permit_number,
                'approver': approver.get_full_name(),
                'approved_at': permit.approved_at.isoformat()
            },
            link=f'/dashboard/ptw/view/{permit.id}'
        )
        
        # Send real-time notification
        self._send_realtime_notification(user, {
            'type': 'ptw_approved',
            'permit_id': permit.id,
            'permit_number': permit.permit_number,
            'message': f'Permit {permit.permit_number} has been approved and is ready for work'
        })
    
    def _send_realtime_notification(self, user, data):
        """Send real-time notification via WebSocket"""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f"user_{user.id}",
                {
                    'type': 'notification_message',
                    'data': data
                }
            )
    
    def _create_audit_log(self, permit, action, user, comments):
        """Create audit log entry"""
        PermitAudit.objects.create(
            permit=permit,
            action=action,
            user=user,
            comments=comments,
            timestamp=timezone.now()
        )
    
    def check_expiring_permits(self):
        """Check for permits nearing expiration and send alerts"""
        from datetime import timedelta
        
        # Get permits expiring in next 2 hours
        expiring_soon = Permit.objects.filter(
            status='active',
            planned_end_time__lte=timezone.now() + timedelta(hours=2),
            planned_end_time__gt=timezone.now()
        )
        
        for permit in expiring_soon:
            # Send expiration alert
            Notification.objects.create(
                user=permit.created_by,
                title='PTW Expiring Soon',
                message=f'Permit {permit.permit_number} expires in less than 2 hours',
                notification_type='ptw_expiring',
                data={
                    'permit_id': permit.id,
                    'permit_number': permit.permit_number,
                    'expires_at': permit.planned_end_time.isoformat()
                },
                link=f'/dashboard/ptw/view/{permit.id}'
            )
            
            # Send real-time alert
            self._send_realtime_notification(permit.created_by, {
                'type': 'ptw_expiring',
                'permit_id': permit.id,
                'permit_number': permit.permit_number,
                'message': f'Permit {permit.permit_number} expires soon!'
            })
    
    def get_workflow_status(self, permit):
        """Get current workflow status"""
        try:
            workflow = permit.workflow
            current_step = workflow.steps.filter(status='pending').first()
            
            return {
                'current_stage': workflow.current_step,
                'status': workflow.status,
                'current_step': current_step.name if current_step else None,
                'assignee': current_step.assignee.get_full_name() if current_step and current_step.assignee else None,
                'steps': [
                    {
                        'name': step.name,
                        'status': step.status,
                        'assignee': step.assignee.get_full_name() if step.assignee else None,
                        'completed_at': step.completed_at,
                        'comments': step.comments
                    }
                    for step in workflow.steps.all().order_by('order')
                ]
            }
        except:
            return {'status': 'no_workflow'}

# Singleton instance
workflow_manager = PTWWorkflowManager()