# Athens Super Admin Module - Backend API Map

## API Endpoint Overview

### Base URL Structure
- **SaaS API Base**: `/api/saas/`
- **Control Plane Base**: `/api/control-plane/`

### URL Configuration Files
- **Main URLs**: `app/backend/backend/urls.py`
- **SaaS URLs**: `app/backend/control_plane/saas_urls.py`
- **Control Plane URLs**: `app/backend/control_plane/urls.py`

## Tenant Management APIs

### Tenant CRUD Operations
**ViewSet**: `SaaSTenantViewSet` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/tenants/` | `list()` | List all tenants |
| POST | `/api/saas/tenants/` | `create()` | Create new tenant |
| GET | `/api/saas/tenants/{id}/` | `retrieve()` | Get tenant details |
| PATCH | `/api/saas/tenants/{id}/` | `partial_update()` | Update tenant |
| DELETE | `/api/saas/tenants/{id}/` | `destroy()` | Delete tenant |

### Tenant Actions
| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| POST | `/api/saas/tenants/{id}/suspend/` | `suspend()` | Suspend tenant |
| POST | `/api/saas/tenants/{id}/reactivate/` | `reactivate()` | Reactivate tenant |

**Request/Response Example**:
```json
// POST /api/saas/tenants/
{
  "name": "acme-corp",
  "display_name": "ACME Corporation",
  "status": "active"
}

// Response
{
  "id": "uuid-here",
  "name": "acme-corp",
  "display_name": "ACME Corporation",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Tenant Module Management
**View**: `SaaSTenantModulesAPIView` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/tenants/{id}/modules` | `get()` | Get tenant modules |
| PATCH | `/api/saas/tenants/{id}/modules` | `patch()` | Update enabled modules |

**Request/Response Example**:
```json
// GET /api/saas/tenants/{id}/modules
{
  "tenant_id": "uuid-here",
  "enabled_modules": ["authentication", "ptw", "safetyobservation"],
  "available_modules": ["authentication", "ptw", "safetyobservation", "incidentmanagement", ...]
}

// PATCH /api/saas/tenants/{id}/modules
{
  "enabled_modules": ["authentication", "ptw", "safetyobservation", "incidentmanagement"]
}
```

### Tenant Sync
**View**: `SaaSTenantSyncAPIView` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| POST | `/api/saas/tenants/{id}/sync` | `post()` | Create AthensTenant record |

**Request/Response Example**:
```json
// POST /api/saas/tenants/{id}/sync
{
  "master_admin_id": "uuid-here",
  "tenant_name": "ACME Corporation",
  "company_id": "uuid-here"
}
```

## Master User Management APIs

### Master User CRUD
**ViewSet**: `SaaSMasterViewSet` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/masters/` | `list()` | List master users |
| POST | `/api/saas/masters/` | `create()` | Create master user |
| GET | `/api/saas/masters/{id}/` | `retrieve()` | Get master details |
| PATCH | `/api/saas/masters/{id}/` | `partial_update()` | Update master |
| DELETE | `/api/saas/masters/{id}/` | `destroy()` | Delete master |

**Query Parameters**:
- `q` - Search by username/email
- `tenant_id` - Filter by tenant
- `status` - Filter by active/disabled

## Subscription Management APIs

### Subscription Operations
**ViewSet**: `SaaSSubscriptionViewSet` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/tenants/{id}/subscription/` | `retrieve()` | Get subscription |
| PATCH | `/api/saas/tenants/{id}/subscription/` | `partial_update()` | Update subscription |

**View**: `SaaSSubscriptionListView` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/subscriptions` | `get()` | List all subscriptions |

**Request/Response Example**:
```json
// PATCH /api/saas/tenants/{id}/subscription/
{
  "plan": "enterprise",
  "status": "active",
  "seats": 50,
  "current_period_end": "2024-12-31"
}
```

## Audit Logging APIs

### Audit Log Access
**ViewSet**: `SaaSAuditLogViewSet` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/audit-logs/` | `list()` | List audit logs |
| GET | `/api/saas/audit-logs/{id}/` | `retrieve()` | Get log details |

**Query Parameters**:
- `tenant_id` - Filter by tenant
- `actor_id` - Filter by actor
- `action` - Filter by action type
- `from` - Date range start
- `to` - Date range end

## Platform Settings APIs

### Settings Management
**View**: `SaaSPlatformSettingsView` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/settings` | `get()` | Get platform settings |
| PATCH | `/api/saas/settings` | `patch()` | Update settings |

**Request/Response Example**:
```json
// GET /api/saas/settings
{
  "platform_name": "Athens",
  "platform_url": "https://athens.example.com",
  "support_email": "support@athens.example.com",
  "primary_color": "#1890ff",
  "session_timeout_minutes": 60,
  "allow_self_signup": false,
  "require_mfa": false
}
```

## Metrics & Analytics APIs

### Overview Metrics
**View**: `SaaSMetricsOverviewAPIView` in `app/backend/control_plane/saas_views.py`

| Method | Path | View Function | Purpose |
|--------|------|---------------|---------|
| GET | `/api/saas/metrics/overview` | `get()` | Get platform metrics |

**Query Parameters**:
- `range` - Time range (7d, 30d, 90d)
- `from` - Custom start date
- `to` - Custom end date

**Response Structure**:
```json
{
  "range": {"start": "2024-01-01", "end": "2024-01-31"},
  "tenants": {
    "total": 100,
    "active": 85,
    "trialing": 10,
    "suspended": 5,
    "new_in_range": 15
  },
  "masters": {
    "total": 150,
    "active": 140,
    "new_in_range": 20
  },
  "subscriptions": {
    "mrr": 50000,
    "plans_breakdown": [{"plan": "enterprise", "count": 50}],
    "status_breakdown": [{"status": "active", "count": 85}]
  },
  "activity": {
    "events_in_range": 500,
    "top_actions": [{"action": "tenant_created", "count": 15}],
    "recent": [...]
  }
}
```

## Authentication & Permissions

### Permission Requirements
All Super Admin APIs require:
- **Authentication**: Valid JWT token
- **Permission**: `IsSuperAdmin` permission class
- **User Type**: `user_type === 'superadmin'`

### Permission Class
**File**: `app/backend/authentication/permissions.py`
```python
class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   getattr(request.user, 'user_type', None) == 'superadmin')
```

## Pagination & Filtering

### Standard Pagination
Most list endpoints use `PageNumberPagination`:
- Default page size: varies by endpoint
- Query parameters: `page`, `page_size`

### Common Filters
- **Search**: `q` parameter for text search
- **Status**: `status` parameter for status filtering
- **Date Range**: `from` and `to` parameters
- **Tenant**: `tenant_id` parameter

## Error Handling

### Standard Error Responses
```json
// 400 Bad Request
{
  "detail": "enabled_modules must be a list"
}

// 404 Not Found
{
  "detail": "Tenant not found in AthensTenant. Sync tenant before managing modules."
}

// 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

### Audit Trail
All operations are automatically logged via the `_audit()` function:
- Actor (user performing action)
- Action type
- Entity type and ID
- Before/after state
- IP address and user agent