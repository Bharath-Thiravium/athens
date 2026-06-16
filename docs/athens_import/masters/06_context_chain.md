# Context Chain & Enforcement

## Context Hierarchy

### Master Admin Context Chain
```
Request → Authentication → Tenant Resolution → Master Validation → Data Access
```

### Detailed Context Flow
1. **HTTP Request** arrives with JWT token
2. **Authentication Middleware** validates token and loads user
3. **Tenant Middleware** extracts and validates `athens_tenant_id`
4. **Permission Check** validates user is master admin
5. **Data Access** filtered by tenant scope

## Tenant Context Determination

### 1. Token-Based Tenant Resolution
**File**: `/app/backend/authentication/tenant_resolver.py`

```python
class TenantResolver:
    @staticmethod
    def resolve_tenant(request):
        """Extract tenant from authenticated user context"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            tenant_id = getattr(request.user, 'athens_tenant_id', None)
            if tenant_id:
                # Validate tenant exists and is active
                tenant = TenantCompany.objects.filter(
                    id=tenant_id, 
                    is_active=True
                ).first()
                return tenant_id, tenant
        return None, None
    
    @staticmethod
    def attach_tenant_context(request, tenant_id, tenant):
        """Attach tenant context to request"""
        request.athens_tenant_id = tenant_id
        request.athens_tenant = tenant
        request.scope_tenant_id = tenant_id
```

### 2. Master Admin Tenant Assignment
```python
# In CustomUser model
class CustomUser(AbstractBaseUser):
    athens_tenant_id = models.UUIDField(
        null=True,  # Nullable for master admins
        help_text="Athens tenant identifier for multi-tenant isolation"
    )
    
    # Master admin gets tenant assigned during creation
    # Either via management command or superadmin interface
```

### 3. Tenant Validation Middleware
**File**: `/app/backend/authentication/tenant_middleware.py`

```python
class AthensTenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip exempt paths
        if self._is_exempt_path(request.path):
            return None
        
        # Extract and validate tenant
        tenant_id, tenant = TenantResolver.resolve_tenant(request)
        
        if not tenant_id:
            return JsonResponse({
                'detail': 'Missing athens_tenant_id in request'
            }, status=422)
        
        if not tenant:
            return JsonResponse({
                'error': 'Invalid or inactive tenant'
            }, status=403)
        
        # Attach tenant context
        TenantResolver.attach_tenant_context(request, tenant_id, tenant)
        return None
```

## Project Context for Masters

### Masters Don't Have "Current Project"
- **Frontend**: `projectId: null` in auth store
- **Backend**: `user.project = null` for masters
- **Access Pattern**: Masters access ALL projects in their tenant

### Project Context Sources
1. **URL Parameters**: `/projects/view/:projectId`
2. **API Parameters**: `?project_id=123`
3. **Request Body**: `{ "project_id": 123 }`

### Project Validation for Masters
```python
# In master admin views
def validate_project_access(request, project_id):
    """Ensure project belongs to master's tenant"""
    try:
        project = Project.objects.get(
            id=project_id,
            athens_tenant_id=request.user.athens_tenant_id
        )
        return project
    except Project.DoesNotExist:
        raise PermissionDenied("Project not found or access denied")
```

## Write Operation Enforcement

### 1. ScopedWriteMixin
**File**: `/app/backend/authentication/tenant_scoped_utils.py`

```python
class ScopedWriteMixin:
    """Automatically enforces tenant scoping for write operations"""
    
    def perform_create(self, serializer):
        tenant_id = getattr(self.request, "scope_tenant_id", None) or \
                   getattr(self.request.user, "athens_tenant_id", None)
        save_kwargs = {}
        if tenant_id:
            save_kwargs["athens_tenant_id"] = tenant_id
        serializer.save(**save_kwargs)
    
    def perform_update(self, serializer):
        # Ensure updates maintain tenant isolation
        tenant_id = getattr(self.request, "scope_tenant_id", None) or \
                   getattr(self.request.user, "athens_tenant_id", None)
        if tenant_id:
            serializer.save(athens_tenant_id=tenant_id)
        else:
            serializer.save()
```

### 2. Scope Enforcement Functions
```python
def enforce_scope_or_403(request):
    """Ensure request has valid tenant scope"""
    if not hasattr(request, 'scope_tenant_id'):
        tenant_id = getattr(request.user, 'athens_tenant_id', None)
        if not tenant_id:
            raise PermissionDenied("Missing tenant context")
        request.scope_tenant_id = tenant_id

def enforce_object_scope_or_403(request, obj, tenant_attr="athens_tenant_id", project_attr=None):
    """Ensure object belongs to user's tenant scope"""
    user_tenant_id = getattr(request.user, "athens_tenant_id", None)
    obj_tenant_id = getattr(obj, tenant_attr, None)
    
    if user_tenant_id and obj_tenant_id:
        if str(user_tenant_id) != str(obj_tenant_id):
            raise PermissionDenied("Access denied: Object belongs to different tenant")
    
    # Additional project-level validation if needed
    if project_attr and hasattr(obj, project_attr):
        project_id = getattr(obj, project_attr, None)
        if project_id:
            # Validate project belongs to tenant
            try:
                Project.objects.get(
                    id=project_id,
                    athens_tenant_id=user_tenant_id
                )
            except Project.DoesNotExist:
                raise PermissionDenied("Access denied: Project belongs to different tenant")
```

## Read Operation Filtering

### 1. Automatic Tenant Filtering
```python
# In views that list data
class ProjectListView(APIView):
    def get(self, request):
        user = request.user
        
        # Masters see all projects in their tenant
        if is_master_user(user):
            if user.athens_tenant_id:
                projects = Project.objects.filter(
                    athens_tenant_id=user.athens_tenant_id
                )
            else:
                projects = Project.objects.all()  # Legacy fallback
        else:
            # Non-masters see only their assigned project
            if user.project:
                projects = Project.objects.filter(id=user.project.id)
            else:
                projects = Project.objects.none()
        
        return Response(ProjectSerializer(projects, many=True).data)
```

### 2. QuerySet Filtering Utilities
```python
def get_tenant_isolated_queryset(model_class, user):
    """Get tenant-isolated queryset for any model"""
    queryset = model_class.objects.all()
    
    if hasattr(model_class, 'athens_tenant_id'):
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if user_tenant_id:
            queryset = queryset.filter(athens_tenant_id=user_tenant_id)
        else:
            # No tenant - return empty for safety
            queryset = queryset.none()
    
    return queryset

def apply_project_isolation(queryset, user):
    """Apply project isolation (masters bypass this)"""
    if is_master_user(user):
        # Masters see all data in their tenant
        return queryset
    
    user_project = getattr(user, 'project', None)
    if not user_project:
        return queryset.none()
    
    # Apply project filtering
    if hasattr(queryset.model, 'project'):
        return queryset.filter(project=user_project)
    elif hasattr(queryset.model, 'project_id'):
        return queryset.filter(project_id=user_project.id)
    
    return queryset
```

## Sequence Diagram: Request → Response

### Master Admin Project Creation
```
Client                 Middleware              View                   Database
  |                        |                    |                        |
  |-- POST /master-admin/projects/create/ ---->|                        |
  |    Authorization: Bearer <jwt>              |                        |
  |                        |                    |                        |
  |                   [Auth Middleware]         |                        |
  |                        |-- validate JWT -->|                        |
  |                        |<-- user object ---|                        |
  |                        |                    |                        |
  |                   [Tenant Middleware]       |                        |
  |                        |-- extract tenant ->|                        |
  |                        |-- validate tenant->|                        |
  |                        |<-- tenant context--|                        |
  |                        |                    |                        |
  |                        |-- request + context -> MasterAdminProjectCreateView
  |                        |                    |                        |
  |                        |              [Permission Check]             |
  |                        |                    |-- IsMasterAdmin -->    |
  |                        |                    |                        |
  |                        |              [Data Validation]              |
  |                        |                    |-- ProjectSerializer -> |
  |                        |                    |                        |
  |                        |              [Tenant Assignment]            |
  |                        |                    |-- set athens_tenant_id->|
  |                        |                    |                        |
  |                        |              [Database Write]               |
  |                        |                    |-- Project.objects.create()
  |                        |                    |<-- project object -----|
  |                        |                    |                        |
  |                        |<-- Response(201) --|                        |
  |<-- 201 Created + project data -------------|                        |
```

### Master Admin Data Access
```
Client                 Middleware              View                   Database
  |                        |                    |                        |
  |-- GET /project/list/ ->|                    |                        |
  |    Authorization: Bearer <jwt>              |                        |
  |                        |                    |                        |
  |                   [Auth + Tenant Middleware]                         |
  |                        |-- validate & attach context -->             |
  |                        |                    |                        |
  |                        |-- request + context -> ProjectListView     |
  |                        |                    |                        |
  |                        |              [Master Check]                 |
  |                        |                    |-- is_master_user() --> |
  |                        |                    |                        |
  |                        |              [Tenant Filtering]             |
  |                        |                    |-- filter by athens_tenant_id
  |                        |                    |<-- tenant projects ----|
  |                        |                    |                        |
  |                        |<-- Response(200) --|                        |
  |<-- 200 OK + projects data ----------------|                        |
```

## Weak Points & Inconsistencies

### 1. Legacy Master Type Handling
**Issue**: Inconsistent handling of `user_type='master'` vs `admin_type='master'`
```python
# Current normalization in multiple places
def is_master_user(user):
    return (
        user.user_type in ['master', 'masteradmin'] or 
        user.admin_type in ['master', 'masteradmin']
    )

# Frontend normalization
const normalizedUserType = rawUserType === 'master' ? 'masteradmin' : rawUserType;
```

**Risk**: Inconsistent master identification across codebase

### 2. Tenant ID Nullable for Masters
**Issue**: `athens_tenant_id` is nullable for masters
```python
athens_tenant_id = models.UUIDField(
    null=True,  # Nullable for master admins
    help_text="Athens tenant identifier"
)
```

**Risk**: Masters without tenant ID can access all data
**Mitigation**: Fallback logic in views, but should be enforced at model level

### 3. Project Context Bypass
**Issue**: Masters bypass project isolation completely
```python
if is_master_user(user):
    # Masters see all data in their tenant
    return queryset  # No project filtering
```

**Risk**: Masters can access data from all projects in tenant
**Note**: This is intentional design, but could be security risk if master account is compromised

### 4. Mixed Permission Patterns
**Issue**: Some views use decorators, others use permission_classes
```python
# Pattern 1: Decorator
@permission_classes([IsMasterAdmin])
class SomeView(APIView): pass

# Pattern 2: Method decorator
@method_decorator(require_master_admin)
def some_method(self, request): pass

# Pattern 3: Manual check
if not is_master_user(request.user):
    raise PermissionDenied()
```

**Risk**: Inconsistent permission enforcement
**Recommendation**: Standardize on permission_classes for consistency

### 5. Tenant Middleware Exemptions
**Issue**: Broad path exemptions in tenant middleware
```python
EXEMPT_PATHS = [
    '/admin/',
    '/api/auth/',
    '/authentication/',  # Exempts ALL auth endpoints
    # ...
]
```

**Risk**: Some endpoints that should be tenant-scoped might be exempt
**Recommendation**: More granular exemptions

## Security Recommendations

### 1. Enforce Tenant ID for Masters
```python
# In model validation
def clean(self):
    if self.user_type in ['master', 'masteradmin']:
        if not self.athens_tenant_id:
            raise ValidationError("Master admin must have athens_tenant_id")
```

### 2. Audit Master Actions
```python
# Add audit logging for master operations
class MasterActionAuditLog(models.Model):
    master_user = models.ForeignKey(CustomUser)
    action = models.CharField(max_length=100)
    target_object = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
```

### 3. Standardize Permission Checks
```python
# Use consistent permission pattern
class BaseMasterView(APIView):
    permission_classes = [IsAuthenticated, IsMasterAdmin]
    
    def dispatch(self, request, *args, **kwargs):
        # Additional master-specific validation
        return super().dispatch(request, *args, **kwargs)
```

### 4. Validate Cross-Tenant Access
```python
# Add explicit cross-tenant access prevention
def validate_no_cross_tenant_access(user, target_object):
    user_tenant = getattr(user, 'athens_tenant_id', None)
    obj_tenant = getattr(target_object, 'athens_tenant_id', None)
    
    if user_tenant and obj_tenant and str(user_tenant) != str(obj_tenant):
        raise PermissionDenied("Cross-tenant access denied")
```