# Athens Super Admin Module - Workflows

## 1. Create Tenant/Company Workflow

### UI Steps (TenantsPage.tsx)
1. **Navigate to Tenants Page**: `/superadmin/tenants`
2. **Click "New Tenant" Button**: Opens create modal
3. **Fill Tenant Form**:
   - Name (required): Slug-like identifier (e.g., "acme-corp")
   - Display Name: Human-readable name (e.g., "ACME Corporation")
   - Status: Active/Disabled (default: Active)
4. **Click "Create"**: Submits form and closes modal
5. **Success**: Tenant appears in table, success message shown

### Backend Calls
```typescript
// Frontend: TenantsPage.tsx -> handleSubmit()
const values = await form.validateFields();
await createTenant(values);

// API Call: saasApi.ts -> createTenant()
POST /api/saas/tenants/
{
  "name": "acme-corp",
  "display_name": "ACME Corporation", 
  "status": "active"
}

// Backend: SaaSTenantViewSet.create()
// 1. Validate data with SaaSTenantSerializer
// 2. Create TenantCompany record
// 3. Auto-create SaaSSubscription (default: trialing)
// 4. Log audit trail via _audit()
```

## 2. Enable Services/Modules Workflow

### UI Steps (TenantsPage.tsx)
1. **Click "Modules" Button**: For specific tenant in table
2. **Module Management Modal Opens**:
   - Shows categorized module list
   - Checkboxes for each available module
   - Current enabled modules are pre-checked
3. **Select/Deselect Modules**: 
   - Safety Management: safetyobservation, incidentmanagement, ptw, inspection
   - Training: inductiontraining, jobtraining, tbt
   - Workforce: worker, manpower
   - Communication: mom, voice_translator
   - Admin: permissions, system
   - Environment: environment
   - Quality: quality
4. **Click "Save Modules"**: Updates tenant configuration

### Backend Calls
```typescript
// 1. Load current modules
GET /api/saas/tenants/{id}/modules
// Response: { enabled_modules: [...], available_modules: [...] }

// 2. Update modules
PATCH /api/saas/tenants/{id}/modules
{
  "enabled_modules": ["authentication", "ptw", "safetyobservation", "incidentmanagement"]
}

// Backend: SaaSTenantModulesAPIView.patch()
// 1. Validate modules against DEFAULT_MODULES
// 2. Update AthensTenant.enabled_modules
// 3. Sync menu access via sync_company_menu_access()
// 4. Log audit trail
```

### Prerequisites
- Tenant must be "synced" first (AthensTenant record must exist)
- If not synced, shows error: "Tenant not found in AthensTenant. Sync tenant before managing modules."

## 3. User Creation/Role Assignment Workflow

### Create Master Admin User

#### UI Steps (MastersPage.tsx)
1. **Navigate to Masters Page**: `/superadmin/masters`
2. **Click "New Master" Button**: Opens create modal
3. **Fill Master User Form**:
   - Email (required)
   - Username (required)
   - Password (optional - auto-generated if empty)
   - Tenant ID (required - select from dropdown)
   - Active status
4. **Click "Create"**: Creates master admin user

#### Backend Calls
```typescript
// Frontend: MastersPage.tsx
await createMaster({
  email: "admin@acme-corp.com",
  username: "acme_admin",
  tenant_id: "uuid-here",
  is_active: true
});

// API Call
POST /api/saas/masters/
{
  "email": "admin@acme-corp.com",
  "username": "acme_admin", 
  "tenant_id": "uuid-here",
  "is_active": true
}

// Backend: SaaSMasterViewSet.create()
// 1. Create CustomUser with user_type='master'
// 2. Set athens_tenant_id to link to tenant
// 3. Set admin_type='master'
// 4. Generate password if not provided
// 5. Set is_password_reset_required=True
// 6. Log audit trail
```

### Role Assignment Logic
**Automatic Role Assignment** (in CustomUser.save()):
```python
# If created by master admin, make them project admin
if creator_admin_type in ['master', 'masteradmin']:
    self.user_type = 'projectadmin'
    # Keep the admin_type as set (client, epc, contractor)

# If created by project admin, make them regular user  
elif creator_user_type == 'projectadmin':
    self.user_type = 'user'
    # Set admin_type based on creator's admin_type
    if creator_admin_type == 'client':
        self.admin_type = 'clientuser'
    elif creator_admin_type == 'epc':
        self.admin_type = 'epcuser'
    elif creator_admin_type == 'contractor':
        self.admin_type = 'contractoruser'
```

## 4. Tenant Sync Workflow

### Purpose
Create the AthensTenant record so modules can be managed. Links TenantCompany (platform) to AthensTenant (application).

### UI Steps (TenantsPage.tsx)
1. **Click "Sync" Button**: For tenant in table
2. **Sync Modal Opens**:
   - Master Admin ID (UUID) - required
   - Tenant Name - pre-filled from display_name
   - Company ID (UUID) - optional
3. **Fill Master Admin ID**: UUID of the master admin user
4. **Click "Sync Tenant"**: Creates AthensTenant record

### Backend Calls
```typescript
// Frontend: TenantsPage.tsx -> handleSync()
await syncTenant(tenant.id, {
  master_admin_id: "uuid-here",
  tenant_name: "ACME Corporation",
  company_id: "uuid-here" // optional
});

// API Call
POST /api/saas/tenants/{id}/sync
{
  "master_admin_id": "uuid-here",
  "tenant_name": "ACME Corporation",
  "company_id": "uuid-here"
}

// Backend: SaaSTenantSyncAPIView.post()
// 1. Validate master_admin_id is valid UUID
// 2. Create AthensTenant record with:
//    - id = tenant_id (links to TenantCompany)
//    - master_admin_id = provided UUID
//    - enabled_modules = DEFAULT_MODULES (all modules enabled)
//    - enabled_menus = DEFAULT_MENUS
//    - is_active = True
// 3. Sync menu access via sync_company_menu_access()
// 4. Log audit trail
```

## 5. Tenant Suspension/Reactivation Workflow

### Suspend Tenant

#### UI Steps (TenantsPage.tsx)
1. **Click "Suspend" Button**: For active tenant
2. **Confirmation**: Action executes immediately (no modal)
3. **Status Update**: Tenant status changes to "disabled", button changes to "Reactivate"

#### Backend Calls
```typescript
// Frontend: TenantsPage.tsx -> handleSuspend()
await suspendTenant(tenant.id);

// API Call
POST /api/saas/tenants/{id}/suspend/

// Backend: SaaSTenantViewSet.suspend()
// 1. Get tenant object
// 2. Capture before state
// 3. Set status = 'disabled'
// 4. Save with update_fields=['status']
// 5. Log audit trail with before/after state
```

### Reactivate Tenant

#### UI Steps (TenantsPage.tsx)
1. **Click "Reactivate" Button**: For suspended tenant
2. **Status Update**: Tenant status changes to "active", button changes to "Suspend"

#### Backend Calls
```typescript
// Frontend: TenantsPage.tsx -> handleReactivate()
await reactivateTenant(tenant.id);

// API Call  
POST /api/saas/tenants/{id}/reactivate/

// Backend: SaaSTenantViewSet.reactivate()
// 1. Get tenant object
// 2. Capture before state
// 3. Set status = 'active'
// 4. Save with update_fields=['status']
// 5. Log audit trail with before/after state
```

## 6. Tenant Deletion Workflow

### UI Steps (TenantsPage.tsx)
1. **Click "Delete" Button**: For any tenant
2. **Confirmation Modal**: 
   - Title: "Delete tenant?"
   - Content: "This will permanently remove the tenant and its subscription data."
   - Buttons: "Cancel" / "Delete" (danger style)
3. **Confirm Deletion**: Permanently removes tenant

### Backend Calls
```typescript
// Frontend: TenantsPage.tsx -> handleDelete()
Modal.confirm({
  title: 'Delete tenant?',
  content: 'This will permanently remove the tenant and its subscription data.',
  okText: 'Delete',
  okType: 'danger',
  onOk: async () => {
    await deleteTenant(tenant.id);
  },
});

// API Call
DELETE /api/saas/tenants/{id}/

// Backend: SaaSTenantViewSet.destroy()
// 1. Get tenant object
// 2. Cascade delete related records:
//    - SaaSSubscription
//    - TenantModuleSubscription
//    - Related audit logs
// 3. Delete TenantCompany record
// 4. Log audit trail
```

## 7. Platform Settings Management Workflow

### UI Steps (SuperadminSettings.tsx)
1. **Navigate to Settings Page**: `/superadmin/settings`
2. **Settings Form Loads**: Pre-populated with current values
3. **Update Settings**:
   - Platform branding (name, URL, logo)
   - Support contact information
   - Email configuration
   - Security settings (MFA, session timeout)
   - Billing configuration
4. **Click "Save Settings"**: Updates platform configuration

### Backend Calls
```typescript
// 1. Load current settings
GET /api/saas/settings
// Response: { platform_name: "Athens", support_email: "...", ... }

// 2. Update settings
PATCH /api/saas/settings
{
  "platform_name": "Athens EHS Platform",
  "support_email": "support@athens.example.com",
  "require_mfa": true,
  "session_timeout_minutes": 120
}

// Backend: SaaSPlatformSettingsView.patch()
// 1. Get or create singleton settings record (id=1)
// 2. Validate data with SaaSPlatformSettingsSerializer
// 3. Update settings with partial data
// 4. Log audit trail with before/after state
```

## 8. Audit Log Review Workflow

### UI Steps (AuditLogsPage.tsx)
1. **Navigate to Audit Logs Page**: `/superadmin/audit-logs`
2. **Filter Options**:
   - Date range picker
   - Actor (user) filter
   - Action type filter
   - Tenant filter
3. **Review Activity**:
   - Chronological list of all platform actions
   - Actor, action, entity details
   - Before/after state changes
   - IP address and timestamp

### Backend Calls
```typescript
// Load audit logs with filters
GET /api/saas/audit-logs/?from=2024-01-01&to=2024-01-31&action=tenant_created

// Backend: SaaSAuditLogViewSet.get_queryset()
// 1. Apply date range filters
// 2. Apply actor/action/tenant filters
// 3. Order by created_at descending
// 4. Paginate results
// 5. Include related actor information
```

## Error Handling Patterns

### Frontend Error Handling
```typescript
try {
  await apiCall();
  message.success('Operation completed');
} catch (err: any) {
  message.error(err?.response?.data?.detail || 'Operation failed');
} finally {
  setLoading(false);
}
```

### Backend Error Responses
- **400 Bad Request**: Validation errors, invalid data
- **404 Not Found**: Tenant not found, resource missing
- **403 Forbidden**: Permission denied
- **500 Internal Server Error**: Unexpected server errors

### Audit Trail Resilience
```python
def _audit(...):
    try:
        SaaSAuditLog.objects.create(...)
    except Exception:
        # Do not block main flow on audit failure
        pass
```

All operations continue even if audit logging fails, ensuring system reliability.