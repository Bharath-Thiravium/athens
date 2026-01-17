# Tenant/Company Isolation Module – Technical Blueprint (Current Working State)

## 1. Module Overview

**Module Name:** Tenant/Company Isolation System  
**Purpose & Business Objective:** Provides enterprise-grade multi-tenant architecture ensuring absolute data separation between companies while allowing controlled cross-company collaboration on business projects. Enforces company-level isolation using athens_tenant_id as the primary isolation key.  
**Key Users / Roles:**
- SAP Internal: Tenant lifecycle management (create/delete tenants)
- Master Admin: Cross-tenant access and tenant configuration
- Tenant Admin: Company-specific configuration management
- Regular Users: Isolated access to company data only

**Dependency on other modules:**
- Authentication module (user tenant association)
- All data modules (tenant isolation enforcement)
- Menu Management (tenant-specific feature control)

## 2. Functional Scope

**Features included:**
- Multi-tenant data isolation using athens_tenant_id
- Tenant lifecycle management (create, activate, deactivate)
- Module and menu enable/disable per tenant
- Database-level isolation enforcement
- Audit logging for all tenant operations
- Cross-tenant access control for master users
- Tenant configuration management API

**Features explicitly excluded:**
- Tenant self-registration (SAP-controlled only)
- Cross-tenant data sharing (except via explicit project roles)
- Tenant-level customization beyond module/menu control
- Tenant billing or usage tracking

**Role-based access control behavior:**
- SAP Internal: Full tenant lifecycle control
- Master Admin: Cross-tenant access, tenant configuration
- Tenant Admin: Own tenant configuration only
- Regular Users: Own tenant data access only

**Visibility rules:**
- All database queries filtered by athens_tenant_id
- Master users bypass tenant filtering
- Tenant configuration visible only to authorized users
- Audit logs accessible to tenant admins and above

## 3. End-to-End Process Flow

### Tenant Creation Flow (SAP Internal):
1. **Trigger:** SAP system creates new company tenant
2. **Validation:** Verify SAP internal permissions and tenant data
3. **Processing:**
   - Create AthensTenant record with unique UUID
   - Set default enabled modules and menus
   - Assign master admin ID from SAP
   - Create audit log entry
4. **Response:** Return tenant configuration
5. **System Action:** Tenant becomes available for user assignment

### Tenant Isolation Flow (Every Request):
1. **Trigger:** Any authenticated API request
2. **Validation:** Check user authentication and tenant assignment
3. **Processing:**
   - Extract user's athens_tenant_id
   - Apply database-level tenant isolation
   - Set request context with tenant information
4. **Database Action:** All queries filtered by tenant ID
5. **Response:** Return only tenant-specific data

### Module/Menu Configuration Flow:
1. **Trigger:** Tenant admin modifies module/menu settings
2. **Validation:** Verify tenant admin permissions
3. **Processing:**
   - Update tenant configuration in AthensTenant model
   - Create audit log entry
   - Apply changes to user sessions
4. **Response:** Confirm configuration update
5. **System Action:** Users see updated module/menu availability

### Cross-Tenant Access Flow (Master Admin):
1. **Trigger:** Master admin accesses system
2. **Validation:** Verify master admin status
3. **Processing:**
   - Bypass tenant isolation filters
   - Allow access to all tenant data
   - Log cross-tenant access for audit
4. **Response:** Return cross-tenant data view
5. **Constraint:** Still subject to module-level permissions

## 4. Technical Architecture

### Backend Components:

**Views / Controllers:**
- `AthensTenantViewSet` - Tenant CRUD operations
- `TenantConfigView` - Read-only tenant configuration
- Module/menu enable/disable actions
- Tenant activation/deactivation endpoints

**Services:**
- `CompanyTenantIsolationMiddleware` - Request-level isolation
- `TenantIsolationMixin` - ViewSet-level isolation
- `get_tenant_isolated_queryset` - Query-level filtering
- Audit logging service for tenant operations

**Models:**
- `AthensTenant` - Central tenant control table
- `TenantAuditLog` - Immutable audit trail
- Tenant-aware base models with athens_tenant_id

### Frontend Components:

**Pages:**
- Tenant configuration interface (master admin)
- Module/menu management interface
- Tenant status monitoring dashboard

**Components:**
- Tenant selector components
- Module toggle switches
- Audit log viewers
- Tenant status indicators

**State management:**
- Current tenant context
- Available modules/menus
- Tenant configuration cache

### APIs used:

**Endpoints:**
- `GET /api/tenant/` - List accessible tenants
- `PUT /api/tenant/{id}/` - Update tenant configuration
- `POST /api/tenant/{id}/enable_module/` - Enable module
- `POST /api/tenant/{id}/disable_module/` - Disable module
- `GET /api/tenant/{id}/audit_logs/` - Get audit trail
- `GET /api/tenant/available_modules/` - List available modules

**Request/Response structure:**
```json
// Tenant Configuration Response
{
  "id": "uuid",
  "enabled_modules": ["authentication", "worker", "ptw"],
  "enabled_menus": ["dashboard", "workers", "permits"],
  "is_active": true,
  "tenant_name": "Company ABC"
}

// Module Toggle Request
{
  "module_name": "incidentmanagement"
}
```

### Database entities:

**Tables:**
- `athens_tenant` - Central tenant control
- `tenant_audit_log` - Audit trail (append-only)
- All data tables include `athens_tenant_id` field

**Key fields:**
- AthensTenant: id (UUID), enabled_modules, enabled_menus, is_active
- TenantAuditLog: action, description, previous_value, new_value
- All models: athens_tenant_id (UUID, nullable for master data)

**Relationships:**
- TenantAuditLog.tenant → AthensTenant (ForeignKey)
- All user data → AthensTenant via athens_tenant_id
- Master admin can access multiple tenants

## 5. File-Level Blueprint (CRITICAL)

### Backend Files:

**`/backend/authentication/tenant_models.py`**
- **Responsibility:** Define tenant control and audit models
- **Key classes:** AthensTenant, TenantAuditLog
- **Inputs:** Tenant configuration data and audit events
- **Outputs:** Database schema for tenant management
- **Important conditions:** Immutable audit logs, UUID primary keys
- **Risk notes:** Changes affect entire multi-tenant architecture

**`/backend/authentication/tenant_views.py`**
- **Responsibility:** API endpoints for tenant management
- **Key functions:** Tenant CRUD, module/menu control, audit logging
- **Inputs:** HTTP requests with tenant operations
- **Outputs:** JSON responses with tenant data
- **Important conditions:** SAP-only tenant creation, permission enforcement
- **Risk notes:** Security-critical for tenant isolation

**`/backend/authentication/company_isolation.py`**
- **Responsibility:** Enforce database-level tenant isolation
- **Key functions:** CompanyTenantIsolationMiddleware, TenantIsolationMixin
- **Inputs:** HTTP requests and database queries
- **Outputs:** Filtered queries and isolated data access
- **Important conditions:** Master user bypass, tenant ID validation
- **Risk notes:** Core isolation logic, changes affect data security

**`/backend/authentication/tenant_permissions.py`**
- **Responsibility:** Permission classes for tenant operations
- **Key functions:** IsSAPInternal, IsTenantAdmin, IsMasterAdmin
- **Inputs:** User authentication data
- **Outputs:** Permission granted/denied decisions
- **Important conditions:** SAP authentication, tenant ownership validation
- **Risk notes:** Permission bypass could compromise isolation

**`/backend/authentication/tenant_middleware.py`**
- **Responsibility:** Request-level tenant context and isolation
- **Key functions:** Tenant ID extraction, database isolation setup
- **Inputs:** HTTP requests with user authentication
- **Outputs:** Request context with tenant information
- **Important conditions:** Exempt path handling, master user detection
- **Risk notes:** Middleware errors affect entire application

### Database Migration Files:

**`/backend/authentication/migrations/tenant_setup.py`**
- **Responsibility:** Create tenant tables and add athens_tenant_id to existing models
- **Key functions:** Table creation, field addition, data migration
- **Inputs:** Existing database schema
- **Outputs:** Multi-tenant enabled database
- **Important conditions:** Backward compatibility, data preservation
- **Risk notes:** Migration errors could cause data loss

### Configuration Files:

**`/backend/authentication/tenant_settings.py`**
- **Responsibility:** Tenant-specific configuration and defaults
- **Key functions:** Default module/menu lists, tenant settings
- **Inputs:** Configuration parameters
- **Outputs:** Tenant configuration defaults
- **Important conditions:** Module availability, security settings
- **Risk notes:** Configuration changes affect all tenants

## 6. Configuration & Setup

### Environment variables used:
- `ATHENS_TENANT_ISOLATION_ENABLED` - Enable/disable tenant isolation
- `SAP_INTEGRATION_KEY` - Authentication key for SAP operations
- `TENANT_AUDIT_RETENTION_DAYS` - Audit log retention period
- Database configuration for tenant isolation

### Feature flags:
- Tenant isolation enforcement (always enabled in production)
- Cross-tenant access logging
- Module/menu availability per tenant
- Audit log immutability enforcement

### Permissions & roles mapping:
- SAP Internal: `is_sap_internal=True` (tenant lifecycle)
- Master Admin: `admin_type='master'` (cross-tenant access)
- Tenant Admin: `is_tenant_admin=True` (own tenant config)
- Regular User: Standard tenant isolation

### Project / tenant / company isolation logic:
- athens_tenant_id represents Company (primary isolation)
- project_id represents Business Project (secondary grouping)
- Companies can participate in multiple projects
- Projects can involve multiple companies with defined roles

### Default values & assumptions:
- New tenants get all modules enabled by default
- Audit logs are immutable and cannot be deleted
- Master users bypass all tenant restrictions
- Inactive tenants block all user access

## 7. Integration Points

### Modules this depends on:
- Django ORM (database isolation)
- Authentication system (user tenant association)
- Middleware framework (request processing)
- Audit logging system (change tracking)

### Modules that depend on this:
- All data modules (tenant isolation required)
- Menu Management (tenant-specific features)
- User Management (tenant-based user filtering)
- Project Management (cross-tenant project participation)

### External services:
- SAP system (tenant lifecycle management)
- Database system (isolation enforcement)
- Audit system (compliance logging)

### Auth / token / session usage:
- JWT tokens include athens_tenant_id
- Session context includes tenant information
- Request middleware enforces tenant isolation
- Master user tokens bypass tenant restrictions

## 8. Current Working State Validation

### Expected UI behavior:
- Master admin sees tenant management interface
- Tenant admin sees module/menu configuration options
- Regular users see only their tenant's data
- Tenant status affects user access immediately
- Module toggles update user interface dynamically

### Expected API responses:
- Tenant endpoints return filtered data based on user permissions
- Module/menu operations return success/failure status
- Audit logs show complete change history
- Cross-tenant access blocked for non-master users
- SAP operations require proper authentication

### Expected DB state:
- All data tables include athens_tenant_id field
- Tenant isolation enforced at query level
- Audit logs are append-only and immutable
- Master users can access all tenant data
- Inactive tenants block user access

### Logs or indicators of success:
- Tenant isolation applied in middleware logs
- Database queries include tenant filtering
- Audit logs created for all tenant operations
- Cross-tenant access logged for master users
- Module/menu changes reflected in user sessions

## 9. Known Constraints & Design Decisions

### Why certain approaches were used:
- athens_tenant_id chosen as UUID for SAP integration
- Database-level isolation for security and performance
- Immutable audit logs for compliance requirements
- SAP-controlled tenant lifecycle for governance
- Master user bypass for administrative operations

### Intentional limitations:
- No tenant self-registration (SAP governance)
- No cross-tenant data sharing (security requirement)
- No tenant-level UI customization (standardization)
- No tenant billing integration (out of scope)

### Performance or scalability considerations:
- Database indexes on athens_tenant_id for query performance
- Middleware caching of tenant context
- Audit log partitioning for large-scale deployments
- Query optimization for tenant-filtered data

## 10. Future Reference Notes

### What must NOT be changed casually:
- athens_tenant_id field structure (affects all data)
- Tenant isolation middleware logic (security critical)
- Audit log immutability (compliance requirement)
- SAP integration authentication (governance)
- Master user bypass logic (administrative access)

### Files that are high-risk:
- `tenant_models.py` - Core tenant data structure
- `company_isolation.py` - Isolation enforcement logic
- `tenant_middleware.py` - Request-level isolation
- Migration files - Database schema changes
- `tenant_permissions.py` - Access control logic

### Areas where bugs are likely if modified:
- Tenant ID extraction and validation
- Database query filtering logic
- Master user permission bypass
- Audit log creation and immutability
- Module/menu availability checking

### Recommended debugging entry points:
- Check middleware logs for tenant isolation application
- Verify athens_tenant_id in database queries
- Examine audit logs for tenant operations
- Test master user cross-tenant access
- Validate module/menu availability per tenant
- Use Django admin to verify tenant data isolation