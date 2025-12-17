from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.notification_utils import (
    send_websocket_notification,
    send_approval_notification,
    get_user_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_notifications_read
)
from authentication.models_notification import Notification, NotificationPreference
import json

User = get_user_model()

class Command(BaseCommand):
    help = 'Comprehensive test of the notification system'

    def add_arguments(self, parser):
        parser.add_argument('--test-user-id', type=int, help='User ID to test notifications with')
        parser.add_argument('--sender-user-id', type=int, help='Sender user ID (optional)')
        parser.add_argument('--run-all', action='store_true', help='Run all tests')

    def handle(self, *args, **options):
        test_user_id = options.get('test_user_id')
        sender_user_id = options.get('sender_user_id')
        run_all = options.get('run_all')

        if run_all:
            self.run_comprehensive_tests()
        elif test_user_id:
            self.run_user_specific_tests(test_user_id, sender_user_id)
        else:
            self.stdout.write(self.style.ERROR('Please provide --test-user-id or --run-all'))

    def run_comprehensive_tests(self):
        """Run comprehensive tests of the notification system"""
        self.stdout.write(self.style.SUCCESS('=== COMPREHENSIVE NOTIFICATION SYSTEM TEST ==='))
        
        # Test 1: Check if notification models are properly configured
        self.stdout.write('\\n1. Testing notification models...')
        try:
            # Check if we can create a notification
            users = User.objects.all()[:2]
            if len(users) < 2:
                self.stdout.write(self.style.ERROR('Need at least 2 users to test notifications'))
                return
            
            test_user = users[0]
            sender_user = users[1]
            
            notification = Notification.objects.create(
                user=test_user,
                title='Test Notification',
                message='This is a test notification',
                notification_type='general',
                sender=sender_user
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created notification: {notification.id}'))
            
            # Test notification methods
            notification_dict = notification.to_dict()
            self.stdout.write(f'✓ Notification to_dict: {json.dumps(notification_dict, indent=2)}')
            
            # Test mark as read
            notification.mark_as_read()
            self.stdout.write(f'✓ Marked notification as read: {notification.read}')
            
            # Clean up
            notification.delete()
            self.stdout.write('✓ Cleaned up test notification')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Model test failed: {str(e)}'))
        
        # Test 2: Check notification preferences
        self.stdout.write('\\n2. Testing notification preferences...')
        try:
            test_user = User.objects.first()
            preferences, created = NotificationPreference.objects.get_or_create(user=test_user)
            self.stdout.write(f'✓ Notification preferences {"created" if created else "retrieved"} for user: {test_user.username}')
            self.stdout.write(f'  - Email notifications: {preferences.email_notifications}')
            self.stdout.write(f'  - Push notifications: {preferences.push_notifications}')
            self.stdout.write(f'  - Meeting notifications: {preferences.meeting_notifications}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Preferences test failed: {str(e)}'))
        
        # Test 3: Test notification utilities
        self.stdout.write('\\n3. Testing notification utilities...')
        try:
            users = User.objects.all()[:2]
            test_user = users[0]
            sender_user = users[1] if len(users) > 1 else None
            
            # Test send_websocket_notification
            notification = send_websocket_notification(
                user_id=test_user.id,
                title='Utility Test Notification',
                message='Testing notification utilities',
                notification_type='general',
                data={'test': True},
                sender_id=sender_user.id if sender_user else None
            )
            
            if notification:
                self.stdout.write(f'✓ send_websocket_notification: Created notification {notification.id}')
                
                # Test get_user_notifications
                notifications = get_user_notifications(test_user.id)
                self.stdout.write(f'✓ get_user_notifications: Found {len(notifications)} notifications')
                
                # Test get_unread_count
                unread_count = get_unread_count(test_user.id)
                self.stdout.write(f'✓ get_unread_count: {unread_count} unread notifications')
                
                # Test mark_notification_read
                success = mark_notification_read(notification.id, test_user.id)
                self.stdout.write(f'✓ mark_notification_read: {"Success" if success else "Failed"}')
                
                # Test mark_all_notifications_read
                success = mark_all_notifications_read(test_user.id)
                self.stdout.write(f'✓ mark_all_notifications_read: {"Success" if success else "Failed"}')
                
                # Clean up
                notification.delete()
                self.stdout.write('✓ Cleaned up utility test notification')
            else:
                self.stdout.write(self.style.ERROR('✗ send_websocket_notification failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Utilities test failed: {str(e)}'))
        
        # Test 4: Test approval notifications
        self.stdout.write('\\n4. Testing approval notifications...')
        try:
            users = User.objects.all()[:2]
            test_user = users[0]
            sender_user = users[1] if len(users) > 1 else None
            
            notification = send_approval_notification(
                user_id=test_user.id,
                title='Approval Test',
                message='Testing approval notification',
                form_type='test_form',
                item_id=123,
                approved=True,
                sender_id=sender_user.id if sender_user else None
            )
            
            if notification:
                self.stdout.write(f'✓ send_approval_notification: Created notification {notification.id}')
                self.stdout.write(f'  - Type: {notification.notification_type}')
                self.stdout.write(f'  - Data: {notification.data}')
                
                # Clean up
                notification.delete()
                self.stdout.write('✓ Cleaned up approval test notification')
            else:
                self.stdout.write(self.style.ERROR('✗ send_approval_notification failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Approval notification test failed: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\\n=== NOTIFICATION SYSTEM TEST COMPLETED ==='))

    def run_user_specific_tests(self, test_user_id, sender_user_id=None):
        """Run tests for a specific user"""
        self.stdout.write(self.style.SUCCESS(f'=== TESTING NOTIFICATIONS FOR USER ID: {test_user_id} ==='))
        
        try:
            test_user = User.objects.get(id=test_user_id)
            self.stdout.write(f'Test user: {test_user.username} (ID: {test_user.id})')
            
            sender_user = None
            if sender_user_id:
                try:
                    sender_user = User.objects.get(id=sender_user_id)
                    self.stdout.write(f'Sender user: {sender_user.username} (ID: {sender_user.id})')
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Sender user ID {sender_user_id} not found'))
            
            # Send test notification
            notification = send_websocket_notification(
                user_id=test_user.id,
                title='User-Specific Test Notification',
                message=f'This is a test notification for {test_user.username}',
                notification_type='general',
                data={'test': True, 'timestamp': str(timezone.now())},
                sender_id=sender_user.id if sender_user else None
            )
            
            if notification:
                self.stdout.write(self.style.SUCCESS(f'✓ Notification sent successfully (ID: {notification.id})'))
                
                # Get user notifications
                notifications = get_user_notifications(test_user.id, limit=5)
                self.stdout.write(f'✓ User has {len(notifications)} recent notifications')
                
                for i, notif in enumerate(notifications[:3], 1):
                    self.stdout.write(f'  {i}. {notif.title} - {notif.message[:50]}{"..." if len(notif.message) > 50 else ""}')
                
                # Get unread count
                unread_count = get_unread_count(test_user.id)
                self.stdout.write(f'✓ Unread notifications: {unread_count}')
                
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to send notification'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {test_user_id} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Test failed: {str(e)}'))

    def list_available_users(self):
        """List available users for testing"""
        self.stdout.write('\\nAvailable users for testing:')
        users = User.objects.all()[:10]  # Limit to first 10 users
        
        for user in users:
            self.stdout.write(f'  ID: {user.id}, Username: {user.username}, Type: {user.user_type}')
        
        if users.count() == 0:
            self.stdout.write('  No users found in the database')
        elif users.count() > 10:
            self.stdout.write(f'  ... and {users.count() - 10} more users')