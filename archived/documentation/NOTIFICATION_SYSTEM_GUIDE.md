# WebSocket Notification System - Configuration Guide

## Overview
The authentication and WebSocket notification system has been fully configured and tested. This system provides real-time notifications through WebSocket connections and REST API endpoints.

## System Components

### 1. Models (`authentication/models_notification.py`)
- **Notification**: Stores notification data with support for different types
- **NotificationPreference**: User preferences for different notification types

### 2. WebSocket Consumer (`authentication/consumers.py`)
- **NotificationConsumer**: Handles WebSocket connections and real-time messaging
- Supports JWT authentication via query parameters
- Handles various message types: send_notification, get_notifications, mark_read, etc.

### 3. REST API Views (`authentication/notification_views.py`)
- **NotificationListView**: Get user notifications
- **NotificationCreateView**: Create and send notifications
- **NotificationMarkReadView**: Mark notifications as read
- **NotificationDeleteView**: Delete notifications
- **NotificationPreferenceView**: Manage user preferences
- **NotificationBroadcastView**: Send notifications to multiple users

### 4. Utility Functions (`authentication/notification_utils.py`)
- Helper functions for sending notifications, marking as read, etc.
- Can be used from Django views and other parts of the application

### 5. WebSocket Middleware (`authentication/websocket_middleware.py`)
- JWT authentication middleware for WebSocket connections
- Automatically authenticates users based on JWT tokens

## Configuration Files Updated

### 1. `backend/settings.py`
```python
INSTALLED_APPS = [
    # ... other apps
    'channels',  # WebSocket support
    'authentication',
]

# ASGI application for Channels
ASGI_APPLICATION = 'backend.asgi.application'

# Channel layers configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

### 2. `backend/asgi.py`
```python
from authentication.websocket_middleware import JWTAuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                authentication.routing.websocket_urlpatterns
            )
        )
    ),
})
```

### 3. `authentication/urls.py`
Added notification endpoints:
- `/notifications/` - List notifications
- `/notifications/create/` - Create notification
- `/notifications/<id>/read/` - Mark as read
- `/notifications/mark-all-read/` - Mark all as read
- `/notifications/<id>/delete/` - Delete notification
- `/notifications/unread-count/` - Get unread count
- `/notifications/preferences/` - Manage preferences
- `/notifications/broadcast/` - Broadcast to multiple users

### 4. `authentication/routing.py`
```python
websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
```

## API Endpoints

### REST API Endpoints

#### 1. Get Notifications
```
GET /auth/notifications/
```
Optional query parameters:
- `limit`: Limit number of notifications returned

Response:
```json
{
    "notifications": [...],
    "total": 10,
    "unread_count": 3
}
```

#### 2. Create Notification
```
POST /auth/notifications/create/
```
Body:
```json
{
    "user_id": 1,
    "title": "Test Notification",
    "message": "This is a test message",
    "type": "general",
    "data": {"key": "value"},
    "link": "https://example.com"
}
```

#### 3. Mark Notification as Read
```
POST /auth/notifications/{notification_id}/read/
```

#### 4. Mark All Notifications as Read
```
POST /auth/notifications/mark-all-read/
```

#### 5. Delete Notification
```
DELETE /auth/notifications/{notification_id}/delete/
```

#### 6. Get Unread Count
```
GET /auth/notifications/unread-count/
```

#### 7. Manage Preferences
```
GET /auth/notifications/preferences/
PUT /auth/notifications/preferences/
```

#### 8. Broadcast Notification
```
POST /auth/notifications/broadcast/
```
Body:
```json
{
    "user_ids": [1, 2, 3],
    "title": "Broadcast Message",
    "message": "This is a broadcast",
    "type": "general"
}
```

### WebSocket Connection

#### Connection URL
```
ws://localhost:8000/ws/notifications/?token=<JWT_TOKEN>
```

#### Message Types

##### 1. Send Notification
```json
{
    "type": "send_notification",
    "user_id": 1,
    "title": "Test",
    "message": "Test message",
    "type": "general",
    "data": {"key": "value"}
}
```

##### 2. Get Notifications
```json
{
    "type": "get_notifications"
}
```

##### 3. Mark as Read
```json
{
    "type": "mark_read",
    "notification_id": 1
}
```

##### 4. Mark All as Read
```json
{
    "type": "mark_all_read"
}
```

##### 5. Delete Notification
```json
{
    "type": "delete_notification",
    "notification_id": 1
}
```

## Testing

### 1. Management Command
```bash
python3 manage.py test_notification_system --run-all
python3 manage.py test_notification_system --test-user-id 1
```

### 2. WebSocket Test Page
Open `websocket_test.html` in a browser to test WebSocket functionality:
1. Get a JWT token by logging into the application
2. Enter the token and connect
3. Test various notification operations

### 3. Manual Testing with curl
```bash
# Create notification
curl -X POST http://localhost:8000/auth/notifications/create/ \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "title": "Test",
    "message": "Test message",
    "type": "general"
  }'

# Get notifications
curl -X GET http://localhost:8000/auth/notifications/ \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

## Notification Types

The system supports the following notification types:
- `meeting` - Meeting-related notifications
- `meeting_response` - Meeting response notifications
- `action_item` - Action item notifications
- `general` - General notifications
- `approval` - Approval notifications
- `meeting_invitation` - Meeting invitation notifications
- `meeting_scheduled` - Meeting scheduled notifications
- `mom_created` - MOM (Minutes of Meeting) created notifications

## Usage in Django Views

### Send a notification from a view:
```python
from authentication.notification_utils import send_websocket_notification

def some_view(request):
    # Send notification
    notification = send_websocket_notification(
        user_id=target_user_id,
        title="New Task Assigned",
        message="You have been assigned a new task",
        notification_type="general",
        data={"task_id": 123},
        sender_id=request.user.id
    )
    
    if notification:
        # Notification sent successfully
        pass
```

### Send approval notification:
```python
from authentication.notification_utils import send_approval_notification

def approve_document(request, document_id):
    # ... approval logic ...
    
    # Send approval notification
    send_approval_notification(
        user_id=document.created_by.id,
        title="Document Approved",
        message="Your document has been approved",
        form_type="document",
        item_id=document_id,
        approved=True,
        sender_id=request.user.id
    )
```

## Security Considerations

1. **JWT Authentication**: WebSocket connections are authenticated using JWT tokens
2. **User Isolation**: Users can only see their own notifications
3. **Permission Checks**: API endpoints check user permissions
4. **Input Validation**: All inputs are validated before processing

## Troubleshooting

### Common Issues:

1. **WebSocket Connection Fails**
   - Check if JWT token is valid and not expired
   - Ensure the token is passed in the query string: `?token=<JWT_TOKEN>`
   - Check server logs for authentication errors

2. **Notifications Not Received**
   - Verify WebSocket connection is established
   - Check if the target user is connected
   - Verify notification was created in the database

3. **Database Errors**
   - Ensure migrations are applied: `python3 manage.py migrate`
   - Check for model conflicts with other apps

### Debug Commands:
```bash
# Check system configuration
python3 manage.py check

# Test notification system
python3 manage.py test_notification_system --run-all

# Check migrations
python3 manage.py showmigrations authentication

# Run development server with WebSocket support
python3 manage.py runserver
```

## Production Considerations

1. **Channel Layers**: Replace InMemoryChannelLayer with Redis for production:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

2. **WebSocket Scaling**: Use Redis or RabbitMQ for multi-server deployments
3. **SSL/TLS**: Use `wss://` instead of `ws://` for secure connections
4. **Rate Limiting**: Implement rate limiting for WebSocket connections
5. **Monitoring**: Add logging and monitoring for WebSocket connections

## Files Created/Modified

### New Files:
- `authentication/models_notification.py`
- `authentication/notification_views.py`
- `authentication/notification_utils.py`
- `authentication/websocket_middleware.py`
- `authentication/admin_notifications.py`
- `authentication/management/commands/test_notification_system.py`
- `websocket_test.html`

### Modified Files:
- `backend/asgi.py`
- `backend/settings.py`
- `authentication/urls.py`
- `authentication/consumers.py`
- `authentication/routing.py`
- `authentication/views.py`

The notification system is now fully configured and ready for use!
