from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('meeting', 'Meeting'),
        ('meeting_response', 'Meeting Response'),
        ('action_item', 'Action Item'),
        ('general', 'General'),
        ('approval', 'Approval'),
        ('meeting_invitation', 'Meeting Invitation'),
        ('meeting_scheduled', 'Meeting Scheduled'),
        ('mom_created', 'MOM Created'),
        ('chat_message', 'Chat Message'),
        ('chat_message_delivered', 'Chat Message Delivered'),
        ('chat_message_read', 'Chat Message Read'),
        ('chat_file_shared', 'Chat File Shared'),
        ('safety_observation_assigned', 'Safety Observation Assigned'),
        ('safety_observation_commitment', 'Safety Observation Commitment'),
        ('safety_observation_completed', 'Safety Observation Completed'),
        ('safety_observation_approved', 'Safety Observation Approved'),
        ('safety_observation_closed', 'Safety Observation Closed'),
        ('ptw_verification', 'PTW Verification Required'),
        ('ptw_approval', 'PTW Approval Required'),
        ('ptw_approved', 'PTW Approved'),
        ('ptw_rejected', 'PTW Rejected'),
        ('ptw_expiring', 'PTW Expiring Soon'),
        ('permission_request', 'Permission Request'),
        ('permission_approved', 'Permission Approved'),
        ('permission_denied', 'Permission Denied'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general')
    data = models.JSONField(default=dict, blank=True)  # For storing additional data
    link = models.CharField(max_length=255,blank=True, null=True)  # Optional link for the notification
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_auth_notifications')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark this notification as read"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save(update_fields=['read', 'read_at'])
    
    def to_dict(self):
        """Convert notification to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.notification_type,
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'data': self.data,
            'link': self.link,
            'sender_id': self.sender.id if self.sender else None,
        }

class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='auth_notification_preferences')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    meeting_notifications = models.BooleanField(default=True)
    approval_notifications = models.BooleanField(default=True)
    general_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"