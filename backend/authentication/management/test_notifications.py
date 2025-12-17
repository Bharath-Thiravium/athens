from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from authentication.notification_utils import send_websocket_notification, send_approval_notification

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the WebSocket notification system'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='User ID to send notification to')
        parser.add_argument('--title', type=str, default='Test Notification', help='Notification title')
        parser.add_argument('--message', type=str, default='This is a test notification', help='Notification message')
        parser.add_argument('--type', type=str, default='general', help='Notification type')

    def handle(self, *args, **options):
        user_id = options['user_id']
        title = options['title']
        message = options['message']
        notification_type = options['type']

        if not user_id:
            self.stdout.write(self.style.ERROR('Please provide --user-id'))
            return

        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(f'Sending notification to user: {user.username} (ID: {user.id})')
            
            notification = send_websocket_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                data={'test': True, 'command': 'test_notifications'}
            )
            
            if notification:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully sent notification (ID: {notification.id})')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('Failed to send notification')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with ID {user_id} does not exist')
            )