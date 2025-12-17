# authentication/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import CustomUser  # Add this import

User = get_user_model()

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.group_name = f'notifications_{self.user.id}'
        
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        
        await self.send(text_data=json.dumps({
            'type': 'connection_established', 
            'message': 'WebSocket connection established successfully', 
            'user_id': self.user.id,
            'username': self.user.username
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                handler_map = {
                    'send_notification': self.handle_send_notification,
                    'get_notifications': self.handle_get_notifications,
                    'mark_read': self.handle_mark_read,
                    'mark_all_read': self.handle_mark_all_read,
                    'delete_notification': self.handle_delete_notification,
                }
                handler = handler_map.get(data.get('type'))
                if handler:
                    await handler(data)
                else:
                    await self.send_error(f"Unknown message type: {data.get('type')}")
            except Exception as e:
                logger.error(f"Error processing message for user {self.user.id}: {e}", exc_info=True)
                await self.send_error(f'An unexpected error occurred.')

    async def handle_send_notification(self, data):
        try:
            user_id = data.get('user_id')
            if not all([user_id, data.get('title'), data.get('message')]):
                return await self.send_error('Missing required fields for notification.')

            notification_dict = await self.create_notification_and_get_dict(data, self.user.id)
            
            if notification_dict:
                target_group = f'notifications_{user_id}'
                await self.channel_layer.group_send(target_group, {'type': 'send_notification_to_user', 'notification': notification_dict})
                await self.send(text_data=json.dumps({'type': 'notification_sent', 'success': True}))
            else:
                await self.send_error('Failed to create notification. User may not exist.')
        except Exception as e:
            await self.send_error(f'Error sending notification: {str(e)}')

    async def handle_get_notifications(self, data):
        try:
            notifications_list = await self.get_user_notifications_as_dicts(self.user.id)
            await self.send(text_data=json.dumps({'type': 'notifications_list', 'notifications': notifications_list}))
        except Exception as e:
            await self.send_error(f'Error fetching notifications: {str(e)}')

    async def handle_mark_read(self, data):
        try:
            notification_id = data.get('notification_id')
            if not notification_id:
                return await self.send_error('Missing notification_id')
            
            success = await self.mark_notification_read_db(notification_id, self.user.id)
            if success:
                await self.send(text_data=json.dumps({'type': 'notification_marked_read', 'notification_id': notification_id}))
        except Exception as e:
            await self.send_error(f'Error marking notification as read: {str(e)}')

    async def handle_mark_all_read(self, data):
        try:
            success = await self.mark_all_notifications_read_db(self.user.id)
            if success:
                await self.send(text_data=json.dumps({'type': 'all_notifications_marked_read'}))
        except Exception as e:
            await self.send_error(f'Error marking all as read: {str(e)}')

    async def handle_delete_notification(self, data):
        try:
            notification_id = data.get('notification_id')
            if not notification_id:
                return await self.send_error('Missing notification_id')
            
            success = await self.delete_notification_db(notification_id, self.user.id)
            if success:
                await self.send(text_data=json.dumps({'type': 'notification_deleted', 'notification_id': notification_id}))
        except Exception as e:
            await self.send_error(f'Error deleting notification: {str(e)}')

    async def send_error(self, message):
        await self.send(text_data=json.dumps({'type': 'error', 'message': message}))

    async def send_notification_to_user(self, event):
        notification = event['notification']
        await self.send(text_data=json.dumps({'type': 'notification', 'notification': notification}))

    # --- Database Operations ---

    @database_sync_to_async
    def create_notification_and_get_dict(self, data, sender_id):
        from authentication.models_notification import Notification
        try:
            target_user = CustomUser.objects.get(id=data.get('user_id'))
            notification = Notification.objects.create(
                user=target_user, sender_id=sender_id, title=data.get('title'),
                message=data.get('message'), notification_type=data.get('notification_type', 'general'),
                data=data.get('data', {}), link=data.get('link')
            )
            return notification.to_dict()
        except CustomUser.DoesNotExist:
            return None
        except Exception:
            return None

    @database_sync_to_async
    def get_user_notifications_as_dicts(self, user_id):
        from authentication.models_notification import Notification
        notifications = Notification.objects.select_related('sender').filter(user_id=user_id).order_by('-created_at')
        return [n.to_dict() for n in notifications]

    @database_sync_to_async
    def mark_notification_read_db(self, notification_id, user_id):
        """Mark a specific notification as read."""
        from authentication.models_notification import Notification
        # --- THIS IS THE CORRECTED LINE ---
        # .update() returns an integer, not a tuple, so we assign it to one variable.
        updated_count = Notification.objects.filter(id=notification_id, user_id=user_id, read=False).update(
            read=True, read_at=timezone.now()
        )
        return updated_count > 0

    @database_sync_to_async
    def mark_all_notifications_read_db(self, user_id):
        """Mark all notifications as read for a user."""
        from authentication.models_notification import Notification
        Notification.objects.filter(user_id=user_id, read=False).update(read=True, read_at=timezone.now())
        return True

    @database_sync_to_async
    def delete_notification_db(self, notification_id, user_id):
        """Delete a notification."""
        from authentication.models_notification import Notification
        # .delete() returns a tuple, so this line is correct as is.
        deleted_count, _ = Notification.objects.filter(id=notification_id, user_id=user_id).delete()
        return deleted_count > 0

    # ==================== CHAT-SPECIFIC WEBSOCKET HANDLERS ====================

    async def send_chat_status_update(self, event):
        """
        Handle chat status updates (message delivered, read, typing, etc.)
        This is called by the channel layer when a chat status update is sent
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat_status_update',
                'data': event['data']
            }))
        except Exception as e:
            logger.error(f"Error sending chat status update: {e}")

    async def send_chat_message_notification(self, event):
        """
        Handle real-time chat message notifications
        """
        try:
            await self.send(text_data=json.dumps({
                'type': 'chat_message_notification',
                'notification': event['notification']
            }))
        except Exception as e:
            logger.error(f"Error sending chat message notification: {e}")

