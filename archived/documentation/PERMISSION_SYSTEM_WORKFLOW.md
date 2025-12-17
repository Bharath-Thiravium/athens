# AdminUser Permission Control System - Implementation Guide

## Overview
This system implements one-time permission control where adminusers must request permission from their creating projectadmin for each edit/delete operation.

## Workflow Process

### 1. AdminUser Creates Record
- AdminUser can CREATE and VIEW records normally
- No permission required for these operations

### 2. AdminUser Attempts Edit/Delete
- System checks if user is adminuser
- If adminuser tries to edit/delete, system blocks the action
- Returns permission request prompt with object details

### 3. Permission Request Process
- AdminUser fills permission request form with reason
- System identifies the projectadmin who created this adminuser
- Permission request is sent to that specific projectadmin
- Real-time notification sent to projectadmin

### 4. ProjectAdmin Approval
- ProjectAdmin receives notification about permission request
- Can view request details: requester, item, reason, timestamp
- Can approve or deny the request
- System creates one-time permission grant (24-hour expiry)

### 5. One-Time Permission Usage
- AdminUser can now perform the requested operation ONCE
- After use, permission is marked as used and cannot be reused
- For next edit/delete, adminuser must request permission again

### 6. Audit Trail
- All permission requests are logged
- All permission grants and usage are tracked
- Complete audit trail for compliance

## Implementation Steps

### Backend Setup

1. **Run Migrations**
```bash
cd backend
python manage.py makemigrations permissions
python manage.py migrate
```

2. **Update Authentication Model**
- The `created_by` field links adminusers to their creating projectadmin
- This relationship is used to determine approval authority

3. **Apply Decorators to Views**
- Add `@require_permission('edit')` to update methods
- Add `@require_permission('delete')` to delete methods
- Set `model = YourModel` attribute on ViewSet classes

### Frontend Integration

1. **Use Permission Hook**
```typescript
import { usePermissionControl } from '../hooks/usePermissionControl';

const { executeWithPermission, PermissionRequestModal } = usePermissionControl();

// For edit operations
const handleEdit = () => {
  executeWithPermission(
    () => api.put(`/api/endpoint/${id}/`, data),
    'edit record'
  );
};

// For delete operations  
const handleDelete = () => {
  executeWithPermission(
    () => api.delete(`/api/endpoint/${id}/`),
    'delete record'
  );
};
```

2. **Add Permission Modal**
```jsx
return (
  <div>
    {/* Your component content */}
    {PermissionRequestModal}
  </div>
);
```

### API Endpoints

- `POST /api/v1/permissions/request/` - Request permission
- `POST /api/v1/permissions/approve/{id}/` - Approve/deny permission
- `GET /api/v1/permissions/my-requests/` - Get user's requests

### Database Tables

1. **permissions_permissionrequest**
   - Stores all permission requests
   - Links requester to approver
   - Contains reason and object details

2. **permissions_permissiongrant**
   - Stores approved permissions
   - Tracks usage and expiry
   - One-time use enforcement

## Usage Examples

### PTW Module Integration
```python
# In ptw/views.py
from permissions.decorators import require_permission

class PermitViewSet(viewsets.ModelViewSet):
    model = Permit  # Required for decorator
    
    @require_permission('edit')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @require_permission('delete')
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
```

### Frontend PTW Integration
```typescript
// In PTW edit component
const handleEditPermit = () => {
  executeWithPermission(
    () => api.put(`/api/v1/ptw/permits/${permitId}/`, formData),
    'edit permit'
  );
};
```

## Security Features

1. **One-Time Usage**: Each permission can only be used once
2. **Time Expiry**: Permissions expire after 24 hours
3. **Audit Trail**: Complete logging of all requests and usage
4. **Hierarchical Control**: Only creating projectadmin can approve
5. **Reason Tracking**: All requests must include justification

## Notifications

- Real-time WebSocket notifications to projectadmins
- Email notifications (if configured)
- In-app notification system integration

## Testing Workflow

1. **Create ProjectAdmin**: Login as master admin, create projectadmin
2. **Create AdminUser**: Login as projectadmin, create adminuser
3. **Test Create/View**: AdminUser can create and view records
4. **Test Edit Request**: AdminUser attempts edit, gets permission prompt
5. **Test Approval**: ProjectAdmin receives notification and approves
6. **Test One-Time Use**: AdminUser can edit once, then needs new permission
7. **Test Audit**: Check all actions are logged in database

## Monitoring & Analytics

- Permission request frequency
- Approval/denial rates
- Most requested operations
- User behavior patterns
- Compliance reporting

This system ensures complete control over edit/delete operations while maintaining audit compliance and user accountability.