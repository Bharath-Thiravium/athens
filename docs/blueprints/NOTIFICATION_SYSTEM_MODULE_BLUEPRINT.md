# Notification System Module – Technical Blueprint (Current Working State)

## 1. Module Overview

**Module Name:** Notification System  
**Purpose & Business Objective:** Provides real-time notification delivery and management across the Athens EHS system. Enables instant communication for approval workflows, system alerts, meeting invitations, and general notifications through WebSocket connections and REST APIs.  
**Key Users / Roles:**
- All authenticated users (notification recipients)
- Admin users (notification senders for approvals)
- Master Admin (broadcast notifications)
- System (automated notifications from workflows)

**Dependency on other modules:**
- Authentication module (user identification and permissions)
- WebSocket infrastructure (real-time communication)
- All operational modules (notification triggers)
- User Management (approval workflow notifications)

## 2. Functional Scope

**Features included:**
- Real-time notification delivery via WebSocket
- Notification CRUD operations (create, read, update, delete)
- Unread notification counting and tracking
- Notification preferences management
- Broadcast notifications to multiple users
- Approval workflow notifications
- Meeting invitation notifications
- Chat privacy controls for notifications
- Mark as read/unread functionality
- Notification history and persistence

**Features explicitly excluded:**
- Email notification delivery (WebSocket only)
- Push notifications to mobile devices
- SMS notifications
- Notification scheduling/delayed delivery
- Rich media notifications (images, videos)

**Role-based access control behavior:**
- All users can receive and manage their own notifications
- Admin users can send approval notifications
- Master Admin can broadcast to multiple users
- Chat notifications respect sender/receiver privacy
- System-generated notifications bypass user permissions

**Visibility rules:**
- Users see only their own notifications
- Chat notifications filtered by sender/receiver relationship
- Approval notifications visible to relevant approvers
- Broadcast notifications respect user permissions

## 3. End-to-End Process Flow

### Real-time Notification Delivery Flow:
1. **Trigger:** System event or user action requires notification
2. **Validation:** Check recipient user exists and permissions
3. **Processing:**
   - Create notification record in database
   - Send via WebSocket to connected clients
   - Update unread count for recipient
4. **Client Action:** Receive and display notification in UI
5. **Response:** Confirm delivery and update UI state

### Approval Workflow Notification Flow:
1. **Trigger:** User submits profile for approval
2. **Validation:** Identify appropriate approver
3. **Processing:**
   - Create approval notification with form data
   - Send to approver via WebSocket
   - Include navigation link to approval interface
4. **Approver Action:** Receive notification and navigate to approval
5. **System Action:** Update approval status and notify submitter

### Notification Management Flow:
1. **Trigger:** User interacts with notification (read, delete)
2. **Validation:** Verify notification ownership
3. **Processing:**
   - Update notification status in database
   - Broadcast status change via WebSocket
   - Update unread count
4. **Response:** Confirm action and update UI
5. **Persistence:** Maintain notification history

### WebSocket Connection Flow:
1. **Trigger:** User logs in and dashboard loads
2. **Validation:** Authenticate WebSocket connection with JWT
3. **Processing:**
   - Establish WebSocket connection
   - Request existing notifications
   - Set up real-time message handling
4. **System Action:** Send notification history to client
5. **Maintenance:** Handle connection drops and reconnection

## 4. Technical Architecture

### Backend Components:

**Views / Controllers:**
- `NotificationListView` - Get user notifications
- `NotificationCreateView` - Send notifications
- `NotificationMarkReadView` - Mark notifications as read
- `NotificationDeleteView` - Delete notifications
- `NotificationBroadcastView` - Send to multiple users
- `NotificationPreferenceView` - Manage user preferences

**Services:**
- `notification_utils.py` - Core notification functions
- WebSocket consumer for real-time delivery
- Notification filtering and privacy validation
- Unread count calculation and caching

**Models:**
- `Notification` - Main notification storage
- `NotificationPreference` - User notification settings
- WebSocket connection management

### Frontend Components:

**Pages:**
- Notification dropdown in dashboard header
- Notification detail modals
- Notification preferences interface

**Components:**
- `NotificationsContext.tsx` - React context for state management
- WebSocket service integration
- Notification list and item components
- Real-time notification display
- Unread count badge

**State management:**
- Notification list state
- Unread count tracking
- WebSocket connection status
- Notification preferences
- Real-time message handling

### APIs used:

**REST Endpoints:**
- `GET /authentication/notifications/` - List notifications
- `POST /authentication/notifications/create/` - Send notification
- `POST /authentication/notifications/{id}/read/` - Mark as read
- `DELETE /authentication/notifications/{id}/delete/` - Delete notification
- `POST /authentication/notifications/mark-all-read/` - Mark all read
- `GET /authentication/notifications/unread-count/` - Get unread count

**WebSocket Messages:**
```json
// Notification Message
{
  "type": "notification",
  "notification": {
    "id": 123,
    "title": "Profile Approved",
    "message": "Your profile has been approved",
    "type": "approval",
    "read": false,
    "created_at": "2024-01-01T10:00:00Z",
    "data": {"formType": "userdetail"},
    "link": "/dashboard/profile"
  }
}

// Mark as Read Message
{
  "type": "mark_as_read",
  "notification_id": 123
}
```

### Database entities:

**Tables:**
- `authentication_notification`
- `authentication_notificationpreference`

**Key fields:**
- Notification: user, title, message, type, read, data, link
- NotificationPreference: user, email_notifications, push_notifications

**Relationships:**
- Notification.user → CustomUser (ForeignKey)
- NotificationPreference.user → CustomUser (OneToOne)
- Notification.sender → CustomUser (ForeignKey, optional)

## 5. File-Level Blueprint (CRITICAL)

### Backend Files:

**`/backend/authentication/notification_views.py`**
- **Responsibility:** Handle notification REST API endpoints
- **Key functions:** CRUD operations, broadcast, preferences management
- **Inputs:** HTTP requests with notification data
- **Outputs:** JSON responses with notification information
- **Important conditions:** User authentication, privacy validation, permission checking
- **Risk notes:** Privacy leaks, unauthorized access, broadcast abuse

**`/backend/authentication/notification_utils.py`**
- **Responsibility:** Core notification business logic and WebSocket integration
- **Key functions:** send_websocket_notification, mark_notification_read, get_user_notifications
- **Inputs:** User IDs, notification data, WebSocket messages
- **Outputs:** Notification objects, WebSocket messages, status confirmations
- **Important conditions:** WebSocket connection validation, user existence checking
- **Risk notes:** Message delivery failures, connection handling, data consistency

**`/backend/authentication/models_notification.py`**
- **Responsibility:** Define notification data models and relationships
- **Key classes:** Notification, NotificationPreference
- **Inputs:** Notification data and user preferences
- **Outputs:** Database schema for notification storage
- **Important conditions:** Privacy validation, data serialization
- **Risk notes:** Data model changes affect API compatibility

**`/backend/authentication/consumers.py`**
- **Responsibility:** WebSocket consumer for real-time notification delivery
- **Key functions:** WebSocket connection handling, message routing, authentication
- **Inputs:** WebSocket connections and messages
- **Outputs:** Real-time notification delivery
- **Important conditions:** JWT authentication, connection management
- **Risk notes:** Connection security, message validation, scalability

### Frontend Files:

**`/frontend/src/common/contexts/NotificationsContext.tsx`**
- **Responsibility:** React context for notification state management
- **Key functions:** WebSocket integration, state management, API calls
- **Inputs:** WebSocket messages, user interactions
- **Outputs:** Notification state and management functions
- **Important conditions:** WebSocket connection handling, error recovery
- **Risk notes:** State synchronization, memory leaks, connection failures

**`/frontend/src/common/utils/webSocketNotificationService.ts`**
- **Responsibility:** WebSocket service for real-time communication
- **Key functions:** Connection management, message handling, authentication
- **Inputs:** WebSocket messages and connection events
- **Outputs:** Notification delivery and status updates
- **Important conditions:** JWT token validation, reconnection logic
- **Risk notes:** Connection security, token expiry, message ordering

**Dashboard notification components:**
- **Responsibility:** Display notifications in dashboard interface
- **Key functions:** Notification dropdown, unread count, click handling
- **Inputs:** Notification data from context
- **Outputs:** User interface for notification management
- **Important conditions:** Real-time updates, user interactions
- **Risk notes:** UI performance, notification overflow, click handling

## 6. Configuration & Setup

### Environment variables used:
- `WS_URL` - WebSocket server URL for real-time connections
- WebSocket authentication configuration
- Notification retention settings
- Connection timeout and retry parameters

### Feature flags:
- Real-time notifications enabled/disabled
- Notification preferences available
- Broadcast notifications for admins
- Chat notification privacy controls

### Permissions & roles mapping:
- All users: Receive and manage own notifications
- Admin users: Send approval notifications
- Master Admin: Broadcast notifications to multiple users
- System: Send automated notifications

### Project / tenant / company isolation logic:
- Notifications respect user project associations
- Chat notifications filtered by sender/receiver relationship
- Approval notifications sent to appropriate project admins
- Broadcast notifications respect user permissions

### Default values & assumptions:
- All notification types enabled by default
- WebSocket connections auto-reconnect on failure
- Notifications persist until explicitly deleted
- Unread count updates in real-time

## 7. Integration Points

### Modules this depends on:
- Authentication module (user identification)
- WebSocket infrastructure (real-time delivery)
- Database system (notification persistence)
- JWT authentication (WebSocket security)

### Modules that depend on this:
- User Management (approval workflow notifications)
- All operational modules (system notifications)
- Dashboard (notification display)
- Meeting Management (meeting invitations)

### External services:
- WebSocket server (real-time communication)
- Database system (notification storage)
- JWT service (authentication)

### Auth / token / session usage:
- JWT tokens for WebSocket authentication
- User context for notification filtering
- Session persistence for connection management
- Token refresh for long-lived connections

## 8. Current Working State Validation

### Expected UI behavior:
- Notifications appear in real-time without page refresh
- Unread count updates immediately when notifications arrive
- Mark as read functionality works instantly
- Notification dropdown shows recent notifications
- Click handling navigates to appropriate modules

### Expected API responses:
- Notification list loads within acceptable time
- WebSocket connections establish successfully
- Mark as read operations update status immediately
- Delete operations remove notifications from UI
- Broadcast notifications reach all intended recipients

### Expected DB state:
- Notifications stored with correct user associations
- Read/unread status tracked accurately
- Notification preferences saved correctly
- Privacy controls enforced for chat notifications
- Notification history maintained properly

### Logs or indicators of success:
- WebSocket connection logs show successful authentication
- Notification delivery logs confirm message routing
- Database logs show notification CRUD operations
- Client logs show real-time message reception
- Error logs capture connection failures and recovery

## 9. Known Constraints & Design Decisions

### Why certain approaches were used:
- WebSocket for real-time delivery to avoid polling overhead
- Database persistence for notification history and reliability
- Privacy controls for chat notifications to prevent data leaks
- React context for state management across components
- JWT authentication for WebSocket security

### Intentional limitations:
- No email delivery (WebSocket only for real-time experience)
- No rich media support (text-only notifications)
- No notification scheduling (immediate delivery only)
- No cross-tenant notification delivery (security requirement)

### Performance or scalability considerations:
- WebSocket connection pooling for scalability
- Notification list pagination for large datasets
- Unread count caching to reduce database queries
- Connection retry logic for reliability
- Message queuing for delivery guarantees

## 10. Future Reference Notes

### What must NOT be changed casually:
- WebSocket message format (affects client compatibility)
- Notification data model structure (affects API responses)
- Privacy validation logic (security critical)
- Authentication mechanism (security requirement)
- Database relationships (affects data integrity)

### Files that are high-risk:
- `notification_utils.py` - Core notification logic
- `consumers.py` - WebSocket security and connection handling
- `NotificationsContext.tsx` - State management and UI updates
- WebSocket service - Real-time communication logic
- Notification models - Data structure and relationships

### Areas where bugs are likely if modified:
- WebSocket connection handling and reconnection logic
- Notification privacy validation and filtering
- Real-time state synchronization between client and server
- Unread count calculation and caching
- JWT token validation and refresh in WebSocket connections

### Recommended debugging entry points:
- Check WebSocket connection status and authentication
- Verify notification delivery logs and message routing
- Examine database notification records and relationships
- Test real-time message handling and state updates
- Validate privacy controls and user filtering
- Monitor connection failures and recovery mechanisms