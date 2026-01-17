# Athens Multi-Tenant Architecture Implementation

## Overview

This implementation provides strict multi-tenant isolation for the Athens EHS system using `athens_tenant_id` as the **ONLY** isolation key. The architecture follows enterprise-grade patterns with proper security, audit trails, and module/menu control.

## Key Components

### 1. Tenant Control Plane

**File**: `authentication/tenant_models.py`

- **AthensTenant**: Central tenant control table
- **TenantAuditLog**: Audit trail for tenant operations
- Controls module enable/disable per tenant
- Controls menu enable/disable per tenant
- Tenant activation/deactivation

### 2. Multi-Tenant Middleware

**Files**: 
- `authentication/tenant_middleware.py`

**AthensTenantMiddleware**:
- Extracts `athens_tenant_id` from SAP JWT tokens
- Validates tenant exists and is active
- Attaches tenant context to requests
- Blocks access if tenant is invalid

**TenantPermissionMiddleware**:
- Enforces module permissions based on tenant configuration
- Blocks access to disabled modules

### 3. Database Schema Changes

**Migrations**:
- `authentication/migrations/0002_add_athens_tenant_id.py`
- `worker/migrations/0002_add_athens_tenant_id.py`
- `incidentmanagement/migrations/0002_add_athens_tenant_id.py`

**Changes**:
- Added `athens_tenant_id UUID` field to ALL domain tables
- Added proper indexes for performance
- Maintains backward compatibility

### 4. Tenant-Aware Base Classes

**File**: `authentication/tenant_base.py`

- **TenantAwareQuerySet**: Automatically filters by tenant
- **TenantAwareManager**: Provides tenant-specific operations
- **TenantAwareModel**: Base model for all domain models

### 5. Permission System

**File**: `authentication/tenant_permissions.py`

- **IsTenantMember**: Ensures user belongs to tenant
- **HasModulePermission**: Checks module is enabled
- **HasMenuPermission**: Checks menu is enabled
- **IsMasterAdmin**: Master admin only operations
- **TenantDataAccess**: Composite permission for data access
- **TenantDataModification**: Composite permission for data modification

### 6. API Management

**Files**:
- `authentication/tenant_views.py`
- `authentication/serializers.py`
- `authentication/tenant_urls.py`

**Features**:
- Tenant CRUD operations
- Module enable/disable
- Menu enable/disable
- Tenant activation/deactivation
- Audit log access

## CRITICAL SECURITY RULES (NON-NEGOTIABLE)

### 🔒 Production Security Enforcement

**1. JWT-Only Authentication in Production**
```python
# X-Athens-Tenant-ID header is BLOCKED in production
if not settings.DEBUG and 'X-Athens-Tenant-ID' in request.headers:
    return HttpResponseForbidden("Header blocked in production")
```

**2. SAP-Only Tenant Lifecycle**
```python
# Tenant creation/deletion LOCKED to SAP internal systems only
# Athens cannot autonomously create tenants
class IsSAPInternal(permissions.BasePermission):
    # Validates SAP internal JWT markers
```

**3. Immutable Audit Logs**
```python
# Audit logs are append-only for compliance
def save(self):
    if self.pk is not None:
        raise ValidationError("Audit logs are immutable")
```

**4. Database-Level Constraints**
```sql
-- Every domain table MUST have:
athens_tenant_id UUID NOT NULL,
CONSTRAINT fk_tenant FOREIGN KEY (athens_tenant_id) 
    REFERENCES athens_tenant(id) ON DELETE RESTRICT
```

## Implementation Rules

### 1. Database Isolation

✅ **MANDATORY**: Every domain table MUST contain `athens_tenant_id`
```sql
athens_tenant_id UUID NOT NULL
```

✅ **MANDATORY**: Every query MUST filter by `athens_tenant_id`
```python
.filter(athens_tenant_id=request.athens_tenant_id)
```

❌ **FORBIDDEN**: Never query without tenant filter
❌ **FORBIDDEN**: Never trust frontend values for tenant isolation

### 2. SAP Integration Contract

**SAP MUST send JWT with**:
```json
{
  "athens_tenant_id": "uuid",
  "master_admin_id": "uuid",
  "service": "athens",
  "service_role": "MASTER_ADMIN"
}
```

### 3. Middleware Enforcement

**Request Flow**:
1. Extract `athens_tenant_id` from JWT
2. Validate tenant exists and is active
3. Attach tenant context to request
4. Check module permissions
5. Process business logic

### 4. Backend Permission Checks

```python
# Module access check
if not request.athens_tenant.is_module_enabled('worker'):
    return 403

# Menu access check  
if not request.athens_tenant.is_menu_enabled('dashboard'):
    return 403
```

## Deployment Steps

### 1. Apply Database Migrations

```bash
# Apply all tenant-related migrations
python manage.py migrate authentication 0002_add_athens_tenant_id
python manage.py migrate worker 0002_add_athens_tenant_id
python manage.py migrate incidentmanagement 0002_add_athens_tenant_id
python manage.py migrate tbt 0002_add_athens_tenant_id
python manage.py migrate inductiontraining 0002_add_athens_tenant_id
python manage.py migrate ptw 0002_add_athens_tenant_id
python manage.py migrate safetyobservation 0002_add_athens_tenant_id
python manage.py migrate mom 0002_add_athens_tenant_id
python manage.py migrate manpower 0002_add_athens_tenant_id
python manage.py migrate environment 0002_add_athens_tenant_id
python manage.py migrate quality 0002_add_athens_tenant_id
python manage.py migrate inspection 0002_add_athens_tenant_id
```

### 2. Populate Existing Data

```bash
# Dry run first to see what will be updated
python manage.py populate_tenant_ids --dry-run

# Populate with specific tenant ID
python manage.py populate_tenant_ids --tenant-id=<your-tenant-uuid>

# Or let it create a default tenant
python manage.py populate_tenant_ids
```

### 3. Make Fields NOT NULL

```bash
# Dry run first
python manage.py make_tenant_id_not_null --dry-run

# Apply changes
python manage.py make_tenant_id_not_null
```

### 4. Create Test Tenant

```bash
# Create full-featured tenant
python manage.py create_default_tenant

# Create minimal tenant for testing
python manage.py create_default_tenant --minimal
```

### 5. Validate Implementation

```bash
# Run comprehensive validation
python manage.py validate_multi_tenant
```

### 3. API Usage

**Headers (Production)**:
```
Authorization: Bearer <sap_jwt_token>  # ONLY source in production
```

**Headers (Development Only)**:
```
Authorization: Bearer <jwt_token>
X-Athens-Tenant-ID: <tenant_id>  # BLOCKED in production
```

**Endpoints**:
- `GET /api/tenant/tenants/` - List tenants
- ~~`POST /api/tenant/tenants/`~~ - **LOCKED: SAP internal only**
- ~~`DELETE /api/tenant/tenants/{id}/`~~ - **LOCKED: SAP internal only**
- `GET /api/tenant/config/current/` - Get current tenant config
- `POST /api/tenant/tenants/{id}/enable_module/` - Enable module
- `POST /api/tenant/tenants/{id}/disable_module/` - Disable module

### 4. Model Usage

```python
# Use tenant-aware base model
from authentication.tenant_base import TenantAwareModel

class MyModel(TenantAwareModel):
    name = models.CharField(max_length=100)
    # athens_tenant_id is inherited

# Query with tenant isolation
MyModel.objects.for_tenant(request.athens_tenant_id).all()

# Create with tenant
MyModel.objects.create_for_tenant(
    request.athens_tenant_id,
    name="Test"
)
```

### 5. View Usage

```python
from authentication.tenant_permissions import TenantDataAccess
from authentication.tenant_base import require_tenant_context

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [TenantDataAccess]
    
    def get_queryset(self):
        return MyModel.objects.for_tenant(
            self.request.athens_tenant_id
        )
    
    @require_tenant_context
    def create(self, request):
        # Tenant context is guaranteed
        pass
```

## Security Features

### 1. Strict Isolation
- No cross-tenant data access
- Automatic tenant filtering
- Validation at middleware level

### 2. Audit Trail
- All tenant operations logged
- IP address and user agent tracking
- Change history with before/after values

### 3. Module Control
- Granular module enable/disable
- API endpoint protection
- Frontend menu control

### 4. Master Admin Controls
- Tenant creation/deletion
- Cross-tenant access for management
- System-wide configuration

## Performance Considerations

### 1. Database Indexes
- `athens_tenant_id` indexed on all tables
- Composite indexes for common queries
- Optimized for tenant-filtered operations

### 2. Query Optimization
- Automatic tenant filtering
- Reduced query complexity
- Efficient data access patterns

### 3. Caching Strategy
- Tenant configuration caching
- Module/menu permission caching
- Reduced database hits

## Migration Strategy

### 1. Backward Compatibility
- `company_id` field preserved
- Gradual migration support
- No breaking changes

### 2. Data Migration
- Populate existing records
- Validate data integrity
- Rollback capability

### 3. Testing
- Comprehensive test coverage
- Multi-tenant test scenarios
- Performance testing

## Monitoring and Maintenance

### 1. Audit Logs
- Track all tenant operations
- Monitor access patterns
- Security incident detection

### 2. Health Checks
- Tenant status monitoring
- Module availability checks
- Performance metrics

### 3. Maintenance Tasks
- Tenant cleanup
- Audit log rotation
- Performance optimization

## Production Deployment Checklist

### 🔥 P0 - MANDATORY Security Fixes
- [ ] **X-Athens-Tenant-ID header blocked in production**
- [ ] **Tenant creation/deletion locked to SAP internal only**
- [ ] **Database foreign key constraints added**
- [ ] **Audit logs made immutable**
- [ ] **All athens_tenant_id fields are NOT NULL**

### Pre-Deployment
- [ ] All migrations created and tested
- [ ] Existing data backed up
- [ ] SAP JWT integration configured
- [ ] Middleware order verified
- [ ] Permission classes implemented
- [ ] **Security validation passed**

### Deployment
- [ ] Apply all migrations
- [ ] Populate existing data with tenant IDs
- [ ] Make athens_tenant_id NOT NULL with FK constraints
- [ ] Validate implementation
- [ ] **Test production security blocks**

### Post-Deployment
- [ ] Monitor tenant isolation
- [ ] Verify module/menu controls
- [ ] Check audit logs immutability
- [ ] Performance testing
- [ ] **Security penetration testing**

### SAP Integration
- [ ] JWT token structure validated
- [ ] **SAP internal tenant creation tested**
- [ ] Master admin controls verified
- [ ] Module enable/disable tested
- [ ] **Production header blocking verified**

## Monitoring and Maintenance

### Health Checks
```bash
# Daily validation
python manage.py validate_multi_tenant

# Check for orphaned data
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT COUNT(*) FROM authentication_project WHERE athens_tenant_id IS NULL')
    print(f'Orphaned projects: {cursor.fetchone()[0]}')
"
```

### Performance Monitoring
- Monitor query performance with tenant filters
- Check index usage on athens_tenant_id columns
- Validate tenant data distribution

### Security Auditing
- Review tenant access logs
- Monitor cross-tenant access attempts
- Validate JWT token processing

## Conclusion

This implementation provides enterprise-grade multi-tenant isolation for Athens with:

✅ **Strict Security**: No cross-tenant data access
✅ **Granular Control**: Module and menu level permissions  
✅ **Audit Trail**: Complete operation tracking
✅ **Performance**: Optimized queries and indexes
✅ **Scalability**: Supports unlimited tenants
✅ **Maintainability**: Clean architecture and documentation

The system is ready for production deployment with proper SAP integration and provides a solid foundation for multi-tenant SaaS operations.