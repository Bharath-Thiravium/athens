# Backend API Map

## Masters Login & Authentication

### Login Endpoints
```python
# Primary login endpoint
POST /authentication/login/
POST /authentication/login/tenant/  # Tenant-aware login

# View: SecureCompatibleLoginAPIView, TenantLoginAPIView
# File: /app/backend/authentication/views.py
# Serializer: CustomTokenObtainPairSerializer
```

### Token Management
```python
# Token refresh
POST /authentication/token/refresh/
POST /authentication/token/refresh/ws/  # WebSocket token refresh

# Logout
POST /authentication/logout/

# View: CustomTokenRefreshView, WebsocketTokenRefreshView, LogoutView
# File: /app/backend/authentication/views.py
```

## Project Management APIs

### Project CRUD Operations
```python
# Create project (Master Admin only)
POST /authentication/master-admin/projects/create/
# View: MasterAdminProjectCreateView
# Permission: @permission_classes([IsMasterAdmin])
# Request: ProjectSerializer data
# Response: Created project data

# List projects (Tenant-scoped)
GET /authentication/project/list/
# View: ProjectListView
# Permission: IsAuthenticated
# Response: Array of projects filtered by athens_tenant_id

# Update project
PUT /authentication/project/update/<int:pk>/
# View: ProjectUpdateView
# Permission: IsAuthenticated + ScopedWriteMixin
# Request: ProjectSerializer data
# Response: Updated project data

# Delete project (Master Admin only)
DELETE /authentication/project/delete/<int:pk>/
# View: ProjectDeleteView  
# Permission: IsMasterAdmin + ScopedWriteMixin
# Response: Success message or dependency error

# Get project dependencies before deletion
GET /authentication/project/delete/<int:pk>/
# View: ProjectDeleteView.get()
# Response: Dependency information and deletion feasibility
```

### Project Cleanup
```python
# Project cleanup utilities (Master Admin only)
POST /authentication/project/cleanup/<int:pk>/
# View: ProjectCleanupView
# Permission: IsMasterAdmin + ScopedWriteMixin
# Request: { "cleanup_type": "check_only|deactivate_users", "force_cleanup": boolean }
# Response: Cleanup results or dependency information
```

## Admin Creation & Management

### Project Admin Creation
```python
# Create project admins (Master Admin only)
POST /authentication/master-admin/projects/create-admins/
# View: MasterAdminCreateProjectAdminsView
# Permission: @permission_classes([IsMasterAdmin])
# Request: {
#   "project_id": int,
#   "client_username": string,
#   "client_company": string,
#   "client_residentAddress": string,
#   "epc_username": string,
#   "epc_company": string,
#   "epc_residentAddress": string,
#   "contractor_username": string,
#   "contractor_company": string,
#   "contractor_residentAddress": string,
#   "contractor_admins": [
#     {
#       "username": string,
#       "company_name": string,
#       "registered_address": string
#     }
#   ]
# }
# Response: {
#   "created_admins": [{"username": string, "password": string, "admin_type": string}],
#   "existing_admins": [string]
# }

# Alternative endpoint for specific project
POST /authentication/master-admin/projects/<int:project_id>/admins/
# Same view and functionality
```

### Admin Password Management
```python
# Reset admin password (Master Admin only)
POST /authentication/master-admin/reset-admin-password/
# View: MasterAdminResetAdminPasswordView
# Permission: @permission_classes([IsMasterAdmin])
# Request: {
#   "project_id": int,
#   "admin_type": "client|epc|contractor",
#   "new_password": string,
#   "admin_index": int  # For contractors (optional)
# }
# Response: {"success": true, "message": string, "admin_username": string}
```

### Admin Deletion
```python
# Delete project admin (Master Admin only)
DELETE /authentication/master-admin/projects/admin/delete/<int:user_id>/
# View: MasterAdminDeleteProjectAdminView
# File: /app/backend/authentication/views_delete_admin.py
# Permission: IsMasterAdmin
# Response: Success message

# Delete admin user (Master Admin only)
DELETE /authentication/master-admin/delete-admin-user/<int:user_id>/
# View: MasterAdminDeleteAdminUserView
# File: /app/backend/authentication/views_admin_delete.py
# Permission: IsMasterAdmin
# Response: Success message
```

## Master Admin Management

### Master Admin Operations
```python
# Get master admin info
GET /authentication/master-admin/
# View: MasterAdminView
# Permission: IsAuthenticated (master only)
# Response: {"id": int, "username": string}

# Create master admin (Public endpoint)
POST /authentication/master-admin/create/
# View: CreateMasterAdminView
# Permission: AllowAny (restricted to one master)
# Request: MasterAdminSerializer data
# Response: {"message": string, "username": string}
```

### Master Password Management
```python
# Master admin reset own password
PUT /authentication/master-admin/reset-password/
# View: MasterAdminResetPasswordView
# Permission: IsAuthenticated (master only)
# Request: {"new_password": string}
# Response: {"success": true, "message": string, "warning": string}

# Check master password status
GET /authentication/master-admin/password-status/
# View: MasterAdminPasswordStatusView
# Permission: IsAuthenticated (master only)
# Response: {
#   "can_reset_password": boolean,
#   "password_set_by_superadmin": boolean,
#   "is_password_reset_required": boolean,
#   "message": string
# }

# Superadmin reset master password
POST /authentication/superadmin/reset-master-password/
# View: SuperAdminResetMasterPasswordView
# Permission: AllowAny (requires superadmin_key)
# Request: {
#   "superadmin_key": string,
#   "username": string,
#   "new_password": string
# }
# Response: {"success": true, "message": string, "username": string}
```

## Approval Workflows

### Admin Detail Approvals
```python
# Get pending admin details (Master Admin only)
GET /authentication/admin/pending-details/
# View: PendingAdminDetailsView
# Permission: IsAuthenticated (master only)
# Response: {"pending_approvals": [...], "count": int}

# Get specific admin detail for approval
GET /authentication/admin/pending/<int:user_id>/
# View: AdminPendingDetailView
# Permission: IsAuthenticated
# Response: Admin detail data for approval

# Approve admin details
POST /authentication/admin/detail/approve/<int:user_id>/
# View: AdminDetailApproveView
# Permission: IsAuthenticated + ScopedWriteMixin
# Response: {"detail": "Admin details approved successfully."}

# Alternative approval endpoint
POST /authentication/admin/detail/approve/<int:admin_detail_id>/
# View: AdminDetailApprovalView
# Permission: IsAuthenticated + ScopedWriteMixin
# Response: {"message": string, "admin_detail_id": int, "user": string}
```

### User Detail Approvals
```python
# Get pending user details for admin
GET /authentication/userdetail/pending/
# View: PendingUserDetailsForAdminView
# Permission: IsAuthenticated
# Response: Array of pending UserDetail objects

# Get specific user detail for approval
GET /authentication/userdetail/pending/<int:user_id>/
# View: UserDetailPendingView
# Permission: IsAuthenticated
# Response: User detail data for approval

# Approve user details
POST /authentication/userdetail/approve/<int:pk>/
# View: UserDetailApproveView
# Permission: IsAuthenticated + ScopedWriteMixin
# Response: {"detail": "UserDetail approved successfully."}
```

## Dashboard & Statistics

### Master Dashboard Data
```python
# Consolidated admin dashboard (Master Admin only)
GET /authentication/admin/dashboard/consolidated/
# View: MenuManagementStatsView (consolidated method)
# Permission: IsAuthenticated (master only)
# Response: {
#   "success": true,
#   "kpis": [...],
#   "statistics": {...},
#   "charts": {...},
#   "project_data": [...]
# }

# Menu management statistics
GET /authentication/menu/dashboard/stats/
# View: MenuManagementStatsView
# Permission: IsAuthenticated (master only)
# Response: Menu configuration statistics
```

### User Overview
```python
# Users by type overview
GET /authentication/users-overview/
# View: UsersByTypeOverviewAPIView
# Permission: IsAuthenticated
# Query Params: ?project_id=<int>
# Response: Comprehensive user breakdown by type and admin_type
```

## Request/Response Formats

### Common Request Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Standard Response Format
```json
// Success Response
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}

// Error Response
{
  "error": "ERROR_CODE",
  "detail": "Human readable error message",
  "code": 400
}
```

### Pagination Convention
```json
// Paginated responses (where applicable)
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

## Status Codes

### Success Codes
- **200 OK**: Successful GET, PUT operations
- **201 Created**: Successful POST operations (creation)
- **204 No Content**: Successful DELETE operations

### Error Codes
- **400 Bad Request**: Invalid request data, validation errors
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions, tenant access denied
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Missing required tenant context
- **500 Internal Server Error**: Server-side errors

### Master-Specific Error Scenarios
```json
// Not a master admin
{
  "detail": "Only master admin can use this endpoint.",
  "code": 403
}

// Tenant isolation violation
{
  "error": "TENANT_ERROR",
  "message": "Invalid or inactive tenant",
  "code": 403
}

// Project dependency blocking deletion
{
  "error": "Cannot delete project with associated data.",
  "details": {
    "users": {"count": 5, "message": "5 user(s) associated with this project"},
    "permits": {"count": 12, "message": "12 PTW permit(s) associated with this project"}
  },
  "total_dependencies": 17
}
```

## Filter & Sort Conventions

### Query Parameters
```http
# Filtering
GET /api/endpoint/?admin_type=client&is_active=true&project_id=123

# Sorting
GET /api/endpoint/?ordering=created_at&ordering=-name

# Pagination
GET /api/endpoint/?page=2&page_size=20

# Search
GET /api/endpoint/?search=project_name
```

### Master-Specific Filters
- **athens_tenant_id**: Automatic tenant filtering (middleware)
- **project_id**: Project-specific filtering (when applicable)
- **admin_type**: Filter by admin type (client, epc, contractor)
- **user_type**: Filter by user type (projectadmin, adminuser)
- **is_active**: Filter by active status