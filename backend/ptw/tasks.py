from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .workflow_manager import workflow_manager
from .models import Permit
try:
    from authentication.models import Notification
except ImportError:
    # Fallback if Notification model doesn't exist
    Notification = None
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_expiring_permits():
    """
    Celery task to check for permits nearing expiration and send alerts
    Runs every 30 minutes
    """
    try:
        workflow_manager.check_expiring_permits()
        logger.info("Expiring permits check completed successfully")
    except Exception as e:
        logger.error(f"Error checking expiring permits: {str(e)}")

@shared_task
def check_overdue_workflow_tasks():
    """
    Celery task to check for overdue workflow tasks and send escalation notifications
    Runs every hour
    """
    try:
        from .models import WorkflowStep
        from authentication.models import AdminUser
        
        # Get overdue workflow steps
        overdue_steps = WorkflowStep.objects.filter(
            status='pending',
            workflow__permit__status__in=['submitted', 'under_review', 'pending_approval'],
            created_at__lt=timezone.now() - timedelta(hours=4)  # 4 hours overdue
        ).select_related('workflow__permit', 'assignee')
        
        for step in overdue_steps:
            permit = step.workflow.permit
            
            # Send escalation notification to assignee
            if Notification:
                Notification.objects.create(
                    user=step.assignee.user,
                    title='Overdue PTW Task',
                    message=f'Permit {permit.permit_number} task is overdue',
                    notification_type='ptw_overdue',
                    data={
                        'permit_id': permit.id,
                        'permit_number': permit.permit_number,
                        'step_name': step.name,
                        'overdue_hours': int((timezone.now() - step.created_at).total_seconds() / 3600)
                    }
                )
            
            # Send notification to higher authority if very overdue (8+ hours)
            if step.created_at < timezone.now() - timedelta(hours=8):
                # Find higher grade users in same organization
                higher_grade_users = AdminUser.objects.filter(
                    project=permit.project,
                    admin_user_type=step.assignee.admin_user_type,
                    grade__lt=step.assignee.grade,  # Lower grade value = higher authority
                    is_active=True
                ).select_related('user')
                
                for higher_user in higher_grade_users:
                    if Notification:
                        Notification.objects.create(
                            user=higher_user.user,
                            title='Escalated PTW Task',
                            message=f'Permit {permit.permit_number} task is severely overdue',
                            notification_type='ptw_escalated',
                            data={
                                'permit_id': permit.id,
                                'permit_number': permit.permit_number,
                                'step_name': step.name,
                                'assignee': step.assignee.user.get_full_name(),
                                'overdue_hours': int((timezone.now() - step.created_at).total_seconds() / 3600)
                            }
                        )
        
        logger.info(f"Processed {overdue_steps.count()} overdue workflow tasks")
        
    except Exception as e:
        logger.error(f"Error checking overdue workflow tasks: {str(e)}")

@shared_task
def auto_expire_permits():
    """
    Celery task to automatically expire permits that have passed their end time
    Runs every hour
    """
    try:
        expired_permits = Permit.objects.filter(
            status='active',
            planned_end_time__lt=timezone.now()
        )
        
        for permit in expired_permits:
            permit.status = 'expired'
            permit.save()
            
            # Send expiration notification to creator
            if Notification:
                Notification.objects.create(
                    user=permit.created_by,
                    title='PTW Expired',
                    message=f'Permit {permit.permit_number} has expired',
                    notification_type='ptw_expired',
                    data={
                        'permit_id': permit.id,
                        'permit_number': permit.permit_number,
                        'expired_at': permit.planned_end_time.isoformat()
                    }
                )
        
        logger.info(f"Auto-expired {expired_permits.count()} permits")
        
    except Exception as e:
        logger.error(f"Error auto-expiring permits: {str(e)}")

@shared_task
def generate_daily_ptw_report():
    """
    Celery task to generate daily PTW summary report
    Runs daily at 6 AM
    """
    try:
        from django.db.models import Count, Q
        from datetime import date
        
        today = date.today()
        
        # Get daily statistics
        stats = {
            'total_permits': Permit.objects.filter(created_at__date=today).count(),
            'active_permits': Permit.objects.filter(status='active').count(),
            'pending_verification': Permit.objects.filter(status='under_review').count(),
            'pending_approval': Permit.objects.filter(status='pending_approval').count(),
            'expired_permits': Permit.objects.filter(status='expired', planned_end_time__date=today).count(),
            'completed_permits': Permit.objects.filter(status='completed', actual_end_time__date=today).count(),
        }
        
        # Send summary to all project admins
        from authentication.models import AdminUser
        project_admins = AdminUser.objects.filter(
            grade='a',  # Grade A users
            is_active=True
        ).select_related('user')
        
        for admin in project_admins:
            if Notification:
                Notification.objects.create(
                    user=admin.user,
                    title='Daily PTW Summary',
                    message=f'Daily PTW report for {today.strftime("%B %d, %Y")}',
                    notification_type='ptw_daily_report',
                    data=stats
                )
        
        logger.info(f"Generated daily PTW report with stats: {stats}")
        
    except Exception as e:
        logger.error(f"Error generating daily PTW report: {str(e)}")

@shared_task
def cleanup_old_notifications():
    """
    Celery task to cleanup old PTW notifications
    Runs weekly
    """
    try:
        # Delete notifications older than 30 days
        if Notification:
            old_notifications = Notification.objects.filter(
                notification_type__startswith='ptw_',
                created_at__lt=timezone.now() - timedelta(days=30)
            )

            count = old_notifications.count()
            old_notifications.delete()

            logger.info(f"Cleaned up {count} old PTW notifications")
        else:
            logger.info("Notification model not available, skipping cleanup")
        
    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {str(e)}")