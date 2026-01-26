"""
Canonical PTW Workflow Manager - Single source of truth for all status transitions
"""
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Permit, PermitAudit
from .validators import validate_permit_requirements, validate_structured_isolation, validate_closeout_completion, validate_deisolation_completion
from .unified_error_handling import PTWWorkflowError, PTWValidationError, PTWPermissionError
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class CanonicalWorkflowManager:
    """
    Canonical workflow manager - ALL status transitions must go through this
    """
    
    VALID_TRANSITIONS = {
        'draft': ['submitted', 'cancelled'],
        'submitted': ['under_review', 'rejected', 'draft'],
        'under_review': ['approved', 'rejected', 'submitted'],
        'approved': ['active', 'cancelled'],
        'active': ['completed', 'suspended'],
        'suspended': ['active', 'cancelled'],
        'completed': [],
        'cancelled': [],
        'expired': [],
        'rejected': ['draft']
    }
    
    @transaction.atomic
    def transition(self, permit, target_status, actor, *, comments=None, context=None):
        """
        Canonical status transition method - ONLY entry point for status changes
        
        Args:
            permit: Permit instance
            target_status: Target status
            actor: User performing transition
            comments: Optional comments
            context: Optional context dict
            
        Returns:
            Updated permit instance
            
        Raises:
            PTWWorkflowError: Invalid transition
            PTWValidationError: Validation failed
            PTWPermissionError: Permission denied
        """
        # Lock permit row during transition to prevent race conditions
        permit = Permit.objects.select_for_update().get(pk=permit.pk)
        
        if not self._can_transition_to(permit, target_status):
            raise PTWWorkflowError(
                f"Invalid transition from {permit.status} to {target_status}",
                current_status=permit.status,
                target_status=target_status
            )
        
        if not self._has_permission(permit, target_status, actor):
            raise PTWPermissionError(
                f"User {actor.username} cannot transition permit to {target_status}",
                action=f"transition_to_{target_status}"
            )
        
        # Apply validators based on target status
        self._validate_transition(permit, target_status, actor)
        
        # Store old status for audit
        old_status = permit.status
        
        # Apply transition
        permit.status = target_status
        self._update_timestamps(permit, target_status)
        permit.save()
        
        # Create audit log
        self._create_audit_log(permit, target_status, actor, comments, old_status)
        
        # Trigger notifications/webhooks
        self._trigger_notifications(permit, old_status, target_status, actor, context)
        
        logger.info(f"Status transition: {old_status} -> {target_status} for permit {permit.permit_number} by {actor.username}")
        
        return permit
    
    def _can_transition_to(self, permit, target_status):
        """Check if transition is valid"""
        return target_status in self.VALID_TRANSITIONS.get(permit.status, [])
    
    def _has_permission(self, permit, target_status, actor):
        """Check if actor has permission for transition"""
        from .unified_permissions import UnifiedPTWPermissions
        
        # Map status to action
        action_map = {
            'submitted': 'submit',
            'under_review': 'verify',
            'approved': 'approve',
            'active': 'activate',
            'completed': 'complete',
            'suspended': 'suspend',
            'cancelled': 'cancel',
            'rejected': 'reject'
        }
        
        action = action_map.get(target_status, 'edit')
        return UnifiedPTWPermissions.can_perform_action(actor, permit, action)
    
    def _validate_transition(self, permit, target_status, actor):
        """Apply validation rules for transition"""
        try:
            if target_status in ['approved', 'active']:
                validate_permit_requirements(permit, action='approve' if target_status == 'approved' else 'activate')
                validate_structured_isolation(permit, action='approve' if target_status == 'approved' else 'activate')
            
            elif target_status == 'completed':
                validate_closeout_completion(permit)
                validate_deisolation_completion(permit)
                
        except Exception as e:
            raise PTWValidationError(str(e), details={'target_status': target_status})
    
    def _update_timestamps(self, permit, target_status):
        """Update relevant timestamps"""
        now = timezone.now()
        
        if target_status == 'submitted':
            permit.submitted_at = now
        elif target_status == 'approved':
            permit.approved_at = now
        elif target_status == 'active':
            permit.actual_start_time = now
        elif target_status == 'completed':
            permit.actual_end_time = now
    
    def _create_audit_log(self, permit, action, user, comments, old_status):
        """Create audit log entry"""
        PermitAudit.objects.create(
            permit=permit,
            action=action,
            user=user,
            comments=comments or f"Status changed from {old_status} to {action}",
            old_values={'status': old_status},
            new_values={'status': action},
            timestamp=timezone.now()
        )
    
    def _trigger_notifications(self, permit, old_status, new_status, actor, context):
        """Trigger notifications and webhooks"""
        try:
            from .notification_utils import create_ptw_notification
            
            # Notify based on new status
            if new_status == 'submitted':
                if permit.verifier:
                    create_ptw_notification(
                        user_id=permit.verifier.id,
                        event_type='ptw_verification',
                        permit=permit,
                        sender_id=actor.id
                    )
            
            elif new_status == 'under_review':
                if permit.approver:
                    create_ptw_notification(
                        user_id=permit.approver.id,
                        event_type='ptw_approval',
                        permit=permit,
                        sender_id=actor.id
                    )
            
            elif new_status == 'approved':
                create_ptw_notification(
                    user_id=permit.created_by.id,
                    event_type='ptw_approved',
                    permit=permit,
                    sender_id=actor.id
                )
            
            elif new_status == 'rejected':
                create_ptw_notification(
                    user_id=permit.created_by.id,
                    event_type='ptw_rejected',
                    permit=permit,
                    sender_id=actor.id
                )
            
            # Trigger webhooks
            from .webhook_dispatcher import trigger_webhooks
            trigger_webhooks(f'permit_{new_status}', permit)
            
        except Exception as e:
            logger.error(f"Notification/webhook error: {str(e)}")
            # Don't fail the transition for notification errors

# Singleton instance
canonical_workflow_manager = CanonicalWorkflowManager()