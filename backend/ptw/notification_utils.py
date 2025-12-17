from authentication.notification_utils import send_websocket_notification

def send_permit_created_notification(permit, recipient_user, sender_user):
    """
    Send notification when a new permit is created
    """
    title = f"New Permit: {permit.permit_number}"
    message = f"A new permit has been created for {permit.work_description} at {permit.location}."
    
    data = {
        'permit_id': permit.id,
        'permit_number': permit.permit_number,
        'permit_type': permit.permit_type.name if permit.permit_type else "Unknown",
        'location': permit.location,
        'action': 'permit_created'
    }
    
    link = f"/dashboard/ptw/view/{permit.id}"
    
    return send_websocket_notification(
        user_id=recipient_user.id,
        title=title,
        message=message,
        notification_type='general',
        data=data,
        link=link,
        sender_id=sender_user.id
    )

def send_permit_status_notification(permit, recipient_user, sender_user, status, comments=None):
    """
    Send notification when permit status changes
    """
    status_text = {
        'pending': 'submitted for approval',
        'approved': 'approved',
        'rejected': 'rejected',
        'in_progress': 'started',
        'completed': 'completed',
        'closed': 'closed',
        'suspended': 'suspended',
        'cancelled': 'cancelled'
    }.get(status, status)
    
    title = f"Permit Status: {permit.permit_number}"
    message = f"Permit {permit.permit_number} has been {status_text}."
    if comments:
        message += f" Comments: {comments}"
    
    data = {
        'permit_id': permit.id,
        'permit_number': permit.permit_number,
        'status': status,
        'comments': comments,
        'action': 'permit_status_change'
    }
    
    link = f"/dashboard/ptw/view/{permit.id}"
    
    notification_type = 'approval' if status in ['approved', 'rejected'] else 'general'
    
    return send_websocket_notification(
        user_id=recipient_user.id,
        title=title,
        message=message,
        notification_type=notification_type,
        data=data,
        link=link,
        sender_id=sender_user.id
    )

def send_permit_extension_notification(extension, recipient_user, sender_user, status=None):
    """
    Send notification for permit extension requests and responses
    """
    permit = extension.permit
    
    if status is None:  # This is a new extension request
        title = f"Extension Request: Permit {permit.permit_number}"
        message = f"An extension has been requested for permit {permit.permit_number} until {extension.new_end_time.strftime('%Y-%m-%d %H:%M')}."
        action = 'extension_requested'
    else:
        status_text = 'approved' if status == 'approved' else 'rejected'
        title = f"Extension {status_text.capitalize()}: Permit {permit.permit_number}"
        message = f"The extension request for permit {permit.permit_number} has been {status_text}."
        action = f'extension_{status_text}'
    
    data = {
        'permit_id': permit.id,
        'permit_number': permit.permit_number,
        'extension_id': extension.id,
        'new_end_time': extension.new_end_time.isoformat() if extension.new_end_time else None,
        'reason': extension.reason,
        'action': action
    }
    
    link = f"/dashboard/ptw/view/{permit.id}"
    
    notification_type = 'approval' if status in ['approved', 'rejected'] else 'general'
    
    return send_websocket_notification(
        user_id=recipient_user.id,
        title=title,
        message=message,
        notification_type=notification_type,
        data=data,
        link=link,
        sender_id=sender_user.id
    )

def send_permit_verification_notification(permit, recipient_user, sender_user, status, comments=None):
    """
    Send notification when permit is verified or rejected during verification
    """
    status_text = 'verified' if status == 'verified' else 'rejected during verification'
    
    title = f"Permit Verification: {permit.permit_number}"
    message = f"Permit {permit.permit_number} has been {status_text}."
    if comments:
        message += f" Comments: {comments}"
    
    data = {
        'permit_id': permit.id,
        'permit_number': permit.permit_number,
        'status': status,
        'comments': comments,
        'action': 'permit_verification'
    }
    
    link = f"/dashboard/ptw/view/{permit.id}"
    
    notification_type = 'verification'
    
    return send_websocket_notification(
        user_id=recipient_user.id,
        title=title,
        message=message,
        notification_type=notification_type,
        data=data,
        link=link,
        sender_id=sender_user.id
    )

def notify_verifiers(permit, sender_user):
    """
    Notify all potential verifiers about a new permit that needs verification

    WORKFLOW ROUTING:
    1. Contractor (any grade) → EPC (C grade) for verification
    2. EPC User (C grade) → EPC (B grade) for verification
    3. Client User (C grade) → Client (B grade) for verification
    """
    from authentication.models import CustomUser
    from django.db.models import Q


    # Find all users who can verify this permit based on creator's type
    if hasattr(permit.created_by, 'admin_type'):
        if permit.created_by.admin_type == 'contractoruser':
            # Contractor created → Notify EPC C grade users for verification
            verifiers = CustomUser.objects.filter(
                user_type='adminuser',
                admin_type='epcuser',
                grade='C'
            )
            for v in verifiers:
        elif permit.created_by.admin_type == 'epcuser' and hasattr(permit.created_by, 'grade') and permit.created_by.grade == 'C':
            # EPC C grade created → Notify EPC B grade users for verification
            verifiers = CustomUser.objects.filter(
                user_type='adminuser',
                admin_type='epcuser',
                grade='B'
            ).exclude(id=permit.created_by.id)  # Exclude the creator
        elif permit.created_by.admin_type == 'clientuser' and hasattr(permit.created_by, 'grade') and permit.created_by.grade == 'C':
            # Client C grade created → Notify Client B grade users for verification
            verifiers = CustomUser.objects.filter(
                user_type='adminuser',
                admin_type='clientuser',
                grade='B'
            ).exclude(id=permit.created_by.id)  # Exclude the creator
        else:
            # Invalid creator type for PTW creation
            return []
    else:
        # Default case - no verifiers found
        return []
    

    notifications_sent = []
    for verifier in verifiers:
        # Create workflow-specific notification messages
        if permit.created_by.admin_type == 'contractoruser':
            title = f"PTW Verification Required: {permit.permit_number}"
            message = f"Contractor permit needs EPC verification: {permit.title} at {permit.location}. Please review and verify or reject with comments."
        elif permit.created_by.admin_type == 'epcuser':
            title = f"PTW Verification Required: {permit.permit_number}"
            message = f"EPC permit needs internal verification: {permit.title} at {permit.location}. Please review and verify or reject with comments."
        elif permit.created_by.admin_type == 'clientuser':
            title = f"PTW Verification Required: {permit.permit_number}"
            message = f"Client permit needs internal verification: {permit.title} at {permit.location}. Please review and verify or reject with comments."
        else:
            title = f"PTW Verification Required: {permit.permit_number}"
            message = f"Permit needs verification: {permit.title} at {permit.location}."

        data = {
            'permit_id': permit.id,
            'permit_number': permit.permit_number,
            'permit_type': permit.permit_type.name if permit.permit_type else "Unknown",
            'location': permit.location,
            'creator_type': permit.created_by.admin_type,
            'creator_grade': getattr(permit.created_by, 'grade', None),
            'action': 'permit_needs_verification',
            'workflow_stage': 'verification'
        }

        # Use correct PTW route structure (ptw/view/:id, not ptw/permits/view/:id)
        link = f"/dashboard/ptw/view/{permit.id}"

        notification = send_websocket_notification(
            user_id=verifier.id,
            title=title,
            message=message,
            notification_type='verification',
            data=data,
            link=link,
            sender_id=sender_user.id
        )

        if notification:
            notifications_sent.append(notification)
        else:

    return notifications_sent

def notify_approvers(permit, sender_user):
    """
    Notify all potential approvers about a verified permit that needs approval

    WORKFLOW ROUTING:
    1. Contractor created → Verified by EPC C grade → Client C grade for approval
    2. EPC User (C grade) created → Verified by EPC B grade → Client C grade for approval
    3. Client User (C grade) created → Verified by Client B grade → Client A grade for approval
    """
    from authentication.models import CustomUser
    from django.db.models import Q

    # Find all users who can approve this permit based on creator's type
    if hasattr(permit.created_by, 'admin_type'):
        if permit.created_by.admin_type == 'contractoruser':
            # Contractor created → Client C grade users for approval
            approvers = CustomUser.objects.filter(
                user_type='adminuser',
                admin_type='clientuser',
                grade='C'
            )
        elif permit.created_by.admin_type == 'epcuser' and hasattr(permit.created_by, 'grade') and permit.created_by.grade == 'C':
            # EPC C grade created → Client C grade users for approval
            approvers = CustomUser.objects.filter(
                user_type='adminuser',
                admin_type='clientuser',
                grade='C'
            )
        elif permit.created_by.admin_type == 'clientuser' and hasattr(permit.created_by, 'grade') and permit.created_by.grade == 'C':
            # Client C grade created → Client A grade users for approval
            approvers = CustomUser.objects.filter(
                user_type='adminuser',
                admin_type='clientuser',
                grade='A'
            ).exclude(id=permit.created_by.id)  # Exclude the creator
        else:
            # Invalid creator type for PTW creation
            return []
    else:
        # Default case - no approvers found
        return []
    
    notifications_sent = []
    for approver in approvers:
        # Create workflow-specific approval notification messages
        if permit.created_by.admin_type == 'contractoruser':
            title = f"PTW Approval Required: {permit.permit_number}"
            message = f"Contractor permit verified by EPC, needs Client approval: {permit.title} at {permit.location}. Please review and approve or reject with comments."
        elif permit.created_by.admin_type == 'epcuser':
            title = f"PTW Approval Required: {permit.permit_number}"
            message = f"EPC permit verified internally, needs Client approval: {permit.title} at {permit.location}. Please review and approve or reject with comments."
        elif permit.created_by.admin_type == 'clientuser':
            title = f"PTW Approval Required: {permit.permit_number}"
            message = f"Client permit verified internally, needs final approval: {permit.title} at {permit.location}. Please review and approve or reject with comments."
        else:
            title = f"PTW Approval Required: {permit.permit_number}"
            message = f"Verified permit needs approval: {permit.title} at {permit.location}."

        data = {
            'permit_id': permit.id,
            'permit_number': permit.permit_number,
            'permit_type': permit.permit_type.name if permit.permit_type else "Unknown",
            'location': permit.location,
            'creator_type': permit.created_by.admin_type,
            'creator_grade': getattr(permit.created_by, 'grade', None),
            'verifier': permit.verifier.username if permit.verifier else None,
            'action': 'permit_needs_approval',
            'workflow_stage': 'approval'
        }

        link = f"/dashboard/ptw/view/{permit.id}"

        notification = send_websocket_notification(
            user_id=approver.id,
            title=title,
            message=message,
            notification_type='approval',
            data=data,
            link=link,
            sender_id=sender_user.id
        )

        if notification:
            notifications_sent.append(notification)

    return notifications_sent

def notify_permit_stakeholders(permit, notification_func, sender_user, **kwargs):
    """
    Helper function to send notifications to all stakeholders of a permit
    """
    notifications_sent = []
    failed_notifications = []
    
    # Identify stakeholders (approvers, supervisors, workers, etc.)
    stakeholders = set()
    
    # Add permit creator
    if permit.created_by:
        stakeholders.add(permit.created_by)
    
    # Add permit approver
    if permit.approved_by:
        stakeholders.add(permit.approved_by)
    
    # Add permit supervisor
    if permit.supervisor:
        stakeholders.add(permit.supervisor)
    
    # Add safety officer
    if permit.safety_officer:
        stakeholders.add(permit.safety_officer)
    
    # Add assigned workers (if applicable)
    for worker_assignment in permit.permit_workers.all():
        if worker_assignment.worker:
            user = worker_assignment.worker.user
            if user:
                stakeholders.add(user)
    
    # Send notifications to all stakeholders
    for stakeholder in stakeholders:
        # Skip sending notification to the sender
        if sender_user and stakeholder.id == sender_user.id:
            continue
            
        try:
            notification = notification_func(permit, stakeholder, sender_user, **kwargs)
            if notification:
                notifications_sent.append({
                    'user_id': stakeholder.id,
                    'notification_id': notification.id
                })
            else:
                failed_notifications.append({
                    'user_id': stakeholder.id,
                    'error': 'Failed to create notification'
                })
        except Exception as e:
            failed_notifications.append({
                'user_id': stakeholder.id,
                'error': str(e)
            })
    
    return {
        'sent': notifications_sent,
        'failed': failed_notifications
    }
