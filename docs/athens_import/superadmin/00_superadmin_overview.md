# Athens Super Admin Module - Overview

## Super Admin Capabilities

The Athens Super Admin module provides platform-level administration capabilities for the multi-tenant SaaS system:

### Core Capabilities
- **Tenant Management**: Create, suspend, reactivate, and delete tenant companies
- **Module Control**: Enable/disable specific modules per tenant (safety, training, workforce, etc.)
- **Master User Management**: Create and manage master admin users for each tenant
- **Subscription Management**: Control billing plans, seats, and subscription status
- **Audit Logging**: Track all platform-level administrative actions
- **Platform Settings**: Configure global platform settings and branding

### User Types Involved

1. **Superadmin** (`user_type: 'superadmin'`)
   - Platform-level administrator
   - Can access all Super Admin functions
   - Not tied to any specific tenant
   - Created via management command: `create_superadmin.py`

2. **Master Admin** (`admin_type: 'master'`, `user_type: 'master'`)
   - Tenant-level administrator
   - Manages a specific company/tenant
   - Created by Superadmin through the Super Admin interface
   - Has `athens_tenant_id` for company isolation

3. **Regular Users** (various types)
   - Cannot access Super Admin functionality
   - Redirected to regular dashboard if they attempt access

## Authentication & Access Flow

### Login Flow for Superadmin
1. User logs in via `/login` (SigninApp component)
2. Authentication backend validates credentials
3. If `user_type === 'superadmin'`, user is redirected to `/superadmin/dashboard`
4. SuperadminLayout component validates `isSuperAdmin` flag
5. Non-superadmin users are redirected to `/dashboard`

### Route Guards
- **Frontend Guard**: `SuperadminLayout.tsx` checks `isSuperAdmin` from auth store
- **Backend Guard**: `IsSuperAdmin` permission class validates `user_type === 'superadmin'`
- **Redirect Logic**: App.tsx automatically routes superadmin users to `/superadmin/dashboard`

## Navigation Structure

### Main Menu Items
Located in `SuperadminLayout.tsx` menuItems array:

```typescript
const menuItems = [
  { key: '/superadmin/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/superadmin/tenants', icon: <ApartmentOutlined />, label: 'Tenants (Companies)' },
  { key: '/superadmin/masters', icon: <TeamOutlined />, label: 'Masters' },
  { key: '/superadmin/subscriptions', icon: <CreditCardOutlined />, label: 'Subscriptions / Billing' },
  { key: '/superadmin/audit-logs', icon: <AuditOutlined />, label: 'Audit Logs' },
  { key: '/superadmin/settings', icon: <SettingOutlined />, label: 'Settings' },
];
```

### Page Hierarchy
- **Dashboard**: Overview metrics and recent activity
- **Tenants**: Company management and module configuration
- **Masters**: Master admin user management
- **Subscriptions**: Billing and subscription management
- **Audit Logs**: Platform activity tracking
- **Settings**: Global platform configuration

## Key Files Referenced

### Frontend Components
- `app/frontend/src/features/superadmin/components/SuperadminLayout.tsx` - Main layout
- `app/frontend/src/features/superadmin/pages/SuperadminDashboard.tsx` - Dashboard page
- `app/frontend/src/features/superadmin/pages/TenantsPage.tsx` - Tenant management
- `app/frontend/src/features/superadmin/services/saasApi.ts` - API client

### Backend Models & Views
- `app/backend/control_plane/models.py` - Data models
- `app/backend/control_plane/saas_views.py` - API endpoints
- `app/backend/authentication/permissions.py` - IsSuperAdmin permission
- `app/backend/authentication/models.py` - CustomUser model

### Routing
- `app/frontend/src/app/App.tsx` - Frontend routing and guards
- `app/backend/control_plane/saas_urls.py` - Backend API routes
- `app/backend/backend/urls.py` - Main URL configuration