# Athens Super Admin Module - Backend Models & Permissions

## Core Data Models

### TenantCompany Model
**File**: `app/backend/control_plane/models.py`

**Purpose**: Represents a company/tenant in the SaaS system

**Key Fields**:
```python
class TenantCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # Slug-like identifier
    display_name = models.CharField(max_length=255, blank=True)  # Human-readable name
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DISABLED = 'disabled', 'Disabled'
```

**Relationships**:
- One-to-One: `SaaSSubscription` (billing info)
- One-to-Many: `TenantModuleSubscription` (enabled modules)
- One-to-Many: `CustomUser` (master admin users via `athens_tenant_id`)

### CustomUser Model (Superadmin)
**File**: `app/backend/authentication/models.py`

**Purpose**: User model with superadmin capabilities

**Key Fields for Superadmin**:
```python
class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('superadmin', 'Superadmin'),  # Platform-level admin
        ('master', 'Master'),          # Tenant-level admin
        ('projectadmin', 'Project Admin'),
        ('user', 'User'),
        ('adminuser', 'Admin User'),
    ]
    
    athens_tenant_id = models.UUIDField(null=True)  # Null for superadmin
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=False, null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
```

**Superadmin Characteristics**:
- `user_type = 'superadmin'`
- `athens_tenant_id = None` (not tied to specific tenant)
- Created via management command: `create_superadmin.py`

### SaaSSubscription Model
**File**: `app/backend/control_plane/models.py`

**Purpose**: Billing and subscription management

**Key Fields**:
```python
class SaaSSubscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = 'trialing', 'Trialing'
        ACTIVE = 'active', 'Active'
        PAST_DUE = 'past_due', 'Past Due'
        CANCELED = 'canceled', 'Canceled'
        SUSPENDED = 'suspended', 'Suspended'
    
    tenant = models.OneToOneField(TenantCompany, on_delete=models.CASCADE)
    plan = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    seats = models.PositiveIntegerField(default=1)
    current_period_start = models.DateField(null=True, blank=True)
    current_period_end = models.DateField(null=True, blank=True)
    renewal_at = models.DateField(null=True, blank=True)
    payment_provider = models.CharField(max_length=100, blank=True)
```

### SaaSAuditLog Model
**File**: `app/backend/control_plane/models.py`

**Purpose**: Track all platform-level administrative actions

**Key Fields**:
```python
class SaaSAuditLog(models.Model):
    class EntityType(models.TextChoices):
        TENANT = 'tenant', 'Tenant'
        USER = 'user', 'User'
        SUBSCRIPTION = 'subscription', 'Subscription'
        SETTINGS = 'settings', 'Settings'
    
    actor = models.ForeignKey('authentication.CustomUser', on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)  # e.g., 'tenant_created', 'tenant_suspended'
    entity_type = models.CharField(max_length=50, choices=EntityType.choices)
    entity_id = models.CharField(max_length=100)
    before = models.JSONField(null=True, blank=True)  # State before change
    after = models.JSONField(null=True, blank=True)   # State after change
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### SaaSPlatformSettings Model
**File**: `app/backend/control_plane/models.py`

**Purpose**: Global platform configuration

**Key Fields**:
```python
class SaaSPlatformSettings(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1)  # Singleton
    platform_name = models.CharField(max_length=200, default='Athens')
    platform_url = models.URLField(blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=50, blank=True)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=20, blank=True)
    
    # Email settings
    email_from_name = models.CharField(max_length=100, blank=True)
    email_from_address = models.EmailField(blank=True)
    email_reply_to = models.EmailField(blank=True)
    
    # Security settings
    session_timeout_minutes = models.PositiveIntegerField(default=60)
    audit_retention_days = models.PositiveIntegerField(default=365)
    allow_self_signup = models.BooleanField(default=False)
    require_mfa = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
```

### TenantModuleSubscription Model
**File**: `app/backend/control_plane/models.py`

**Purpose**: Track which modules are enabled per tenant

**Key Fields**:
```python
class TenantModuleSubscription(models.Model):
    tenant = models.ForeignKey(TenantCompany, on_delete=models.CASCADE)
    module_code = models.CharField(max_length=100)  # e.g., 'ptw', 'safetyobservation'
    enabled = models.BooleanField(default=True)
    plan_tier = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('tenant', 'module_code')
```

## Permission System

### IsSuperAdmin Permission Class
**File**: `app/backend/authentication/permissions.py`

```python
class IsSuperAdmin(permissions.BasePermission):
    """
    Platform-level superadmin for SaaS control plane.
    Explicitly checks user_type to avoid relying only on is_staff/is_superuser.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   getattr(request.user, 'user_type', None) == 'superadmin')
```

**Usage in Views**:
```python
class SaaSTenantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    # ... rest of viewset
```

### Other Permission Classes
**File**: `app/backend/authentication/permissions.py`

```python
class IsMasterAdmin(permissions.BasePermission):
    """Allows access only to master admin users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   is_master_user(request.user))

class IsProjectAdmin(permissions.BasePermission):
    """Allows access only to users with user_type 'projectadmin'."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and 
                   getattr(request.user, 'user_type', None) == 'projectadmin')
```

## Tenancy & Isolation Rules

### Multi-Tenant Architecture
**Athens Tenant Model**: `app/backend/authentication/tenant_models.py`

```python
class AthensTenant(models.Model):
    id = models.UUIDField(primary_key=True)  # Links to TenantCompany.id
    master_admin_id = models.UUIDField()     # Master admin for this tenant
    company_id = models.UUIDField(null=True, blank=True)
    enabled_modules = models.JSONField(default=list)
    enabled_menus = models.JSONField(default=list)
    tenant_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
```

### Tenant Isolation Middleware
**File**: `app/backend/authentication/tenant_middleware.py`

**Purpose**: Automatically filter data by `athens_tenant_id`

**Key Classes**:
- `AthensTenantMiddleware` - Sets tenant context
- `CompanyTenantIsolationMiddleware` - Enforces tenant isolation

### Global vs Tenant-Scoped Data

**Global Data (No Tenant Isolation)**:
- `TenantCompany` - Platform-level tenant records
- `SaaSSubscription` - Billing information
- `SaaSAuditLog` - Platform audit trail
- `SaaSPlatformSettings` - Global settings
- `CustomUser` with `user_type='superadmin'` - Platform admins

**Tenant-Scoped Data**:
- `CustomUser` with `athens_tenant_id` - Tenant users
- `Project` - Business projects
- `UserDetail`, `AdminDetail` - User profiles
- All business domain models (PTW, Safety, etc.)

## Audit Logging Implementation

### Automatic Audit Trail
**Function**: `_audit()` in `app/backend/control_plane/saas_views.py`

```python
def _audit(actor, action, entity_type, entity_id, before=None, after=None, request=None):
    try:
        SaaSAuditLog.objects.create(
            actor=actor,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            before=before,
            after=after,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None,
        )
    except Exception:
        # Do not block main flow on audit failure
        pass
```

**Usage in ViewSets**:
```python
def perform_create(self, serializer):
    tenant = serializer.save()
    _audit(self.request.user, 'tenant_created', 'tenant', tenant.id, 
           None, SaaSTenantSerializer(tenant).data, self.request)

def perform_update(self, serializer):
    tenant = self.get_object()
    before = SaaSTenantSerializer(tenant).data
    tenant = serializer.save()
    after = SaaSTenantSerializer(tenant).data
    _audit(self.request.user, 'tenant_updated', 'tenant', tenant.id, 
           before, after, self.request)
```

## Database Routing

### Control Plane Database
**File**: `app/backend/control_plane/db_router.py`

**Purpose**: Route control plane models to separate database

**Configuration in settings.py**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'athens_ehs',
        # ... tenant data
    },
    'control_plane': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'athens_control_plane',
        # ... platform data
    }
}
```

## Security Considerations

### Password Management
**For Master Admins**:
- `can_reset_password` - Whether user can reset password
- `password_set_by_superadmin` - Whether password was set by superadmin
- `is_password_reset_required` - Force password reset on next login

### Session Management
- `session_timeout_minutes` in platform settings
- Automatic token expiration
- Audit trail for all authentication events

### Data Integrity
- UUID primary keys for all tenant-related entities
- Foreign key constraints with appropriate cascade behavior
- JSON field validation for module lists and settings