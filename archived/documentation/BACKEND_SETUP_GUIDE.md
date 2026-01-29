# Backend Setup Guide for WebSocket Notifications

## Files Created

1. **consumers.py** - WebSocket consumer handling all notification operations
2. **models_notification.py** - Notification and NotificationPreference models
3. **notification_utils.py** - Utility functions for sending notifications from Django views
4. **routing.py** - WebSocket URL routing
5. **admin_notifications.py** - Django admin configuration
6. **management/commands/test_notifications.py** - Management command for testing

## Setup Instructions

### 1. Install Required Packages

```bash
pip install channels channels-redis
```

### 2. Update Django Settings

Add to your `settings.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... your existing apps
    'channels',
    'authentication',  # Make sure your authentication app is included
]

# Add Channels configuration
ASGI_APPLICATION = 'your_project.asgi.application'

# Configure Channel Layers (using Redis)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# For development, you can use in-memory channel layer (not recommended for production)
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer'
#     }
# }
```

### 3. Create ASGI Application

Create `asgi.py` in your project root:

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from authentication import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
```

### 4. Add Models to Your Authentication App

Copy the contents of `models_notification.py` to your authentication app:

```python
# In authentication/models.py or create authentication/models_notification.py
# Copy the Notification and NotificationPreference models
```

### 5. Add Consumer to Your Authentication App

Copy `consumers.py` to your authentication app:

```python
# authentication/consumers.py
# Copy the NotificationConsumer class
```

### 6. Add Routing

Create `authentication/routing.py`:

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
```

### 7. Add Admin Configuration

In `authentication/admin.py`, add:

```python
from .admin_notifications import *
```

### 8. Add Utility Functions

Copy `notification_utils.py` to your authentication app:

```python
# authentication/notification_utils.py
# Copy all utility functions
```

### 9. Run Migrations

```bash
python manage.py makemigrations authentication
python manage.py migrate
```

### 10. Install and Start Redis (if using Redis channel layer)

```bash
# On Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# On macOS with Homebrew
brew install redis
brew services start redis

# On Windows, download from https://redis.io/download
```

## Usage Examples

### From Django Views

```python
from authentication.notification_utils import (
    send_websocket_notification,
    send_approval_notification,
    send_user_detail_approval_notification
)

# Send a general notification
send_websocket_notification(
    user_id=user.id,
    title="Welcome!",
    message="Welcome to our platform",
    notification_type="general"
)

# Send approval notification
send_approval_notification(
    user_id=user.id,
    title="Details Approved",
    message="Your details have been approved",
    form_type="userdetail",
    item_id=user.id,
    approved=True,
    sender_id=admin_user.id
)
```

### Testing the System

```bash
# Test sending a notification
python manage.py test_notifications --user-id 1 --title "Test" --message "Hello World"

# Check in Django admin
python manage.py runserver
# Go to http://localhost:8000/admin/authentication/notification/
```

## WebSocket Message Protocol

### Client → Server Messages

```javascript
// Send notification
{
  "type": "send_notification",
  "user_id": 123,
  "title": "Title",
  "message": "Message",
  "type": "approval",
  "data": {...},
  "link": "/some/url"
}

// Get all notifications
{
  "type": "get_notifications"
}

// Mark as read
{
  "type": "mark_read",
  "notification_id": 456
}

// Mark all as read
{
  "type": "mark_all_read"
}

// Delete notification
{
  "type": "delete_notification",
  "notification_id": 456
}
```

### Server → Client Messages

```javascript
// New notification
{
  "type": "notification",
  "notification": {
    "id": 123,
    "title": "Title",
    "message": "Message",
    "type": "approval",
    "read": false,
    "created_at": "2024-01-01T00:00:00Z",
    "data": {...}
  }
}

// Notifications list
{
  "type": "notifications_list",
  "notifications": [...],
  "total": 10,
  "unread_count": 3
}

// Confirmations
{
  "type": "notification_sent",
  "success": true,
  "notification_id": 123
}

{
  "type": "notification_marked_read",
  "notification_id": 456,
  "success": true
}
```

## Security Notes

1. **JWT Authentication**: The consumer validates JWT tokens from query parameters
2. **User Isolation**: Users can only access their own notifications
3. **Permission Checks**: Add additional permission checks as needed
4. **Rate Limiting**: Consider adding rate limiting for notification sending

## Production Considerations

1. **Use Redis**: Don't use InMemoryChannelLayer in production
2. **SSL/TLS**: Use WSS (WebSocket Secure) in production
3. **Load Balancing**: Configure Redis for multiple server instances
4. **Monitoring**: Add logging and monitoring for WebSocket connections
5. **Error Handling**: Implement comprehensive error handling and recovery

## Troubleshooting

1. **WebSocket Connection Issues**: Check CORS settings and WebSocket URL
2. **Redis Connection**: Ensure Redis is running and accessible
3. **JWT Token Issues**: Verify token format and expiration
4. **Database Issues**: Check model imports and migrations
5. **Channel Layer**: Verify channel layer configuration

## Integration with Frontend

The frontend WebSocket service should connect to:
```
ws://localhost:8000/ws/notifications/?token=YOUR_JWT_TOKEN
```

The frontend system you've already set up will automatically handle all the message types defined in this backend implementation.
