# Masters Module Overview

## What are "Masters"?

Masters are the highest-level administrative users in the Athens EHS system. They represent the **company owners/administrators** who manage multiple business projects and their associated teams.

### User Type Hierarchy
```
Master Admin (user_type='master', admin_type='master')
├── Project Admins (user_type='projectadmin')
│   ├── Client Admin (admin_type='client')
│   ├── EPC Admin (admin_type='epc')
│   └── Contractor Admin(s) (admin_type='contractor')
└── Admin Users (user_type='adminuser')
    ├── Client Users (admin_type='clientuser')
    ├── EPC Users (admin_type='epcuser')
    └── Contractor Users (admin_type='contractoruser')
```

## Master Capabilities

### 1. Project Management
- **Create Projects**: `/authentication/master-admin/projects/create/`
- **List Projects**: `/authentication/project/list/` (tenant-scoped)
- **Update Projects**: `/authentication/project/update/<id>/`
- **Delete Projects**: `/authentication/project/delete/<id>/` (with dependency checks)
- **Project Cleanup**: `/authentication/project/cleanup/<id>/`

### 2. Admin Creation & Assignment
- **Create Project Admins**: `/authentication/master-admin/projects/create-admins/`
  - Client Admin (1 per project)
  - EPC Admin (1 per project)  
  - Contractor Admin(s) (multiple per project)
- **Reset Admin Passwords**: `/authentication/master-admin/reset-admin-password/`
- **Delete Project Admins**: `/authentication/master-admin/projects/admin/delete/<user_id>/`

### 3. Approval Workflows
- **Approve Admin Details**: `/authentication/admin/detail/approve/<user_id>/`
- **View Pending Approvals**: `/authentication/admin/pending-details/`
- **Approve User Details**: `/authentication/userdetail/approve/<pk>/`

### 4. System Oversight
- **Dashboard Stats**: `/authentication/admin/dashboard/consolidated/`
- **Menu Management**: `/authentication/menu/dashboard/stats/`
- **User Overview**: `/authentication/users-overview/`

## Authentication Method

### Token-Based Authentication (JWT)
- **Login Endpoint**: `/authentication/login/` or `/authentication/login/tenant/`
- **Token Storage**: JWT access + refresh tokens
- **Token Claims**: Include `user_type`, `admin_type`, `athens_tenant_id`, `project_id`

### Master Admin Identification
```python
# Backend identification
def is_master_user(user):
    return (
        user.user_type in ['master', 'masteradmin'] or 
        user.admin_type in ['master', 'masteradmin']
    )

# Frontend identification  
const isMaster = usertype === 'masteradmin' || django_user_type === 'masteradmin'
```

## Tenant/Company Relationship

### Multi-Tenant Architecture
- **athens_tenant_id**: UUID field linking master to their company/tenant
- **Tenant Isolation**: Masters only see data within their tenant scope
- **Project Ownership**: Projects belong to a tenant (`Project.athens_tenant_id`)

### Master ↔ Tenant ↔ Projects Chain
```
Master Admin
├── athens_tenant_id: UUID (company identifier)
├── Projects (filtered by athens_tenant_id)
│   ├── Project 1 (athens_tenant_id matches)
│   ├── Project 2 (athens_tenant_id matches)
│   └── Project N (athens_tenant_id matches)
└── Company Details (CompanyDetail model)
```

## Current Project Context

### Context Storage
- **Backend**: `request.user.project` (for non-masters)
- **Frontend**: `projectId` in auth store (localStorage)
- **Masters**: Can access ALL projects in their tenant, no single "current" project

### Context Enforcement
- **Middleware**: `AthensTenantMiddleware` enforces tenant isolation
- **Project Isolation**: `ProjectIsolationMiddleware` enforces project-level access
- **Scoped Queries**: `ScopedWriteMixin` and `enforce_scope_or_403()` utilities

### How Masters Switch Context
Masters don't have a "current project" - they operate at the tenant level and can:
1. View all projects in their tenant
2. Create new projects
3. Manage admins across all projects
4. Access consolidated dashboards

## Password Management

### Master Admin Password Control
- **Initial Setup**: Created via management command or superadmin
- **Self-Reset**: Limited one-time reset capability
- **Superadmin Reset**: `/authentication/superadmin/reset-master-password/`
- **Status Check**: `/authentication/master-admin/password-status/`

### Password Reset Flow
```python
# Master can reset once if password was set by superadmin
user.can_reset_password = True/False
user.password_set_by_superadmin = True/False
user.is_password_reset_required = True/False
```

## Session Storage & Persistence

### Frontend Auth Store (Zustand)
```typescript
interface AuthState {
  token: string | null;
  refreshToken: string | null;
  projectId: number | null;  // null for masters
  username: string | null;
  usertype: string | null;   // 'masteradmin'
  django_user_type: string | null; // 'masteradmin'
  isSuperAdmin: boolean;
  userId: number | null;
  // ... other fields
}
```

### Storage Location
- **Primary**: `localStorage` (persistent across sessions)
- **Keys**: `auth-storage` (Zustand persist)
- **Token Refresh**: Automatic via axios interceptors

## Key Model References

### Primary Models
- **CustomUser**: `/app/backend/authentication/models.py#CustomUser`
- **Project**: `/app/backend/authentication/models.py#Project`
- **AdminDetail**: `/app/backend/authentication/models.py#AdminDetail`
- **CompanyDetail**: `/app/backend/authentication/models.py#CompanyDetail`

### Key Fields
```python
# CustomUser model
user_type = 'master'  # or 'masteradmin'
admin_type = 'master'  # or 'masteradmin'
athens_tenant_id = UUID  # Company/tenant identifier
project = ForeignKey(Project)  # null for masters
can_reset_password = Boolean
password_set_by_superadmin = Boolean
```

## Security & Isolation

### Tenant Isolation
- **Middleware**: `AthensTenantMiddleware` validates `athens_tenant_id`
- **Scoped Queries**: All data queries filtered by tenant
- **Cross-Tenant Prevention**: Masters cannot access other tenants' data

### Permission Decorators
- **@permission_classes([IsMasterAdmin])**: View-level master restriction
- **@require_master_admin**: Function-level master restriction
- **ScopedWriteMixin**: Automatic tenant/project scoping for writes