# WebSocket-Only Notification System

## Overview
This system uses **WebSocket only** for all notification operations - both sending and receiving. No HTTP API calls are used for notifications.

## Architecture

### 1. **useWebSocket.ts** - Core WebSocket Hook
- Manages WebSocket connection lifecycle
- Provides methods for sending different types of messages
- Handles connection states and reconnection
- **New Methods Added:**
  - `sendNotification(userId, payload)` - Send notification via WebSocket
  - `markNotificationAsRead(notificationId)` - Mark as read via WebSocket
  - `markAllNotificationsAsRead()` - Mark all as read via WebSocket
  - `deleteNotification(notificationId)` - Delete notification via WebSocket
  - `requestNotifications()` - Request all notifications via WebSocket

### 2. **webSocketNotificationService.ts** - Service Layer
- Singleton service that wraps the WebSocket hook
- Provides a clean API for notification operations
- Includes convenience methods like `sendApprovalNotification()`
- **Main Hook:** `useWebSocketNotificationService()`

### 3. **NotificationsContext.tsx** - Global State Management
- Provides notifications to the entire app via React Context
- Handles all WebSocket message types:
  - `notification` - New notification received
  - `notifications_list` - Full list of notifications
  - `notification_marked_read` - Confirmation of read status
  - `all_notifications_marked_read` - All marked as read
  - `notification_deleted` - Notification deleted
  - `notification_sent` - Confirmation of sent notification
  - `error` - Error messages
- Automatically requests notifications when WebSocket connects

### 4. **App.tsx** - Provider Setup
- Wraps the entire app with `<NotificationsProvider>`
- No longer needs WebSocket URL parameter (handled internally)

## WebSocket Message Protocol

### Outgoing Messages (Client → Server)
```typescript
// Send notification
{
  type: 'send_notification',
  user_id: 123,
  title: 'Notification Title',
  message: 'Notification message',
  type: 'approval',
  data: { ... }
}

// Mark as read
{
  type: 'mark_read',
  notification_id: 456
}

// Mark all as read
{
  type: 'mark_all_read'
}

// Delete notification
{
  type: 'delete_notification',
  notification_id: 456
}

// Request all notifications
{
  type: 'get_notifications'
}
```

### Incoming Messages (Server → Client)
```typescript
// New notification
{
  type: 'notification',
  notification: {
    id: 123,
    title: 'Title',
    message: 'Message',
    type: 'approval',
    read: false,
    created_at: '2024-01-01T00:00:00Z',
    data: { ... }
  }
}

// Notifications list
{
  type: 'notifications_list',
  notifications: [...]
}

// Confirmation messages
{
  type: 'notification_marked_read',
  notification_id: 456
}

{
  type: 'notification_sent',
  success: true
}
```

## Usage Examples

### In Components
```typescript
// Get notification context
const {
  notifications,
  unreadCount,
  isConnected,
  sendNotification,
  sendApprovalNotification,
  markAsRead,
  markAllAsRead
} = useNotificationsContext();

// Send a notification
await sendNotification(userId, {
  title: 'User Approved',
  message: 'Your details have been approved',
  type: 'approval',
  data: { formType: 'userdetail', approved: true }
});

// Mark as read
await markAsRead(notificationId);
```

### In UserDetail Component
```typescript
// Send approval notification to user
await sendNotification(userToApprove.user, {
  title: 'Your Details Approved',
  message: 'Your user details have been approved by the administrator.',
  type: 'approval',
  data: {
    formType: 'userdetail',
    approved: true,
    userDetailId: userToApprove.id
  }
});

// Send confirmation to admin
await sendNotification(currentUserId, {
  title: 'User Details Approved Successfully',
  message: `You have successfully approved the user details for ${userToApprove.name}.`,
  type: 'approval',
  data: {
    formType: 'userdetail',
    approved: true,
    userDetailId: userToApprove.id,
    adminAction: true
  }
});
```

## Key Benefits

1. **Single Source of Truth**: All notifications go through WebSocket
2. **Real-time**: Instant delivery and updates
3. **Simplified Architecture**: No dual HTTP/WebSocket system
4. **Automatic State Management**: Context handles all state updates
5. **Connection Management**: Automatic reconnection and error handling
6. **Type Safety**: Full TypeScript support

## Backend Requirements

The backend WebSocket consumer needs to handle these message types:
- `send_notification` - Create and broadcast notification
- `mark_read` - Mark notification as read
- `mark_all_read` - Mark all notifications as read
- `delete_notification` - Delete notification
- `get_notifications` - Send all notifications for user

## Migration Notes

- **Removed**: Old `notificationService.ts` HTTP-based functions
- **Removed**: Dual WebSocket connections in Dashboard
- **Removed**: `useNotifications.ts` hook (replaced by context)
- **Added**: Single unified WebSocket-only system
- **Added**: Comprehensive message type handling
- **Added**: Automatic notification fetching on connection

## Connection Status

The system provides connection status via `isConnected` boolean, allowing components to show connection state to users.