# Gap Analysis for SAP Clone

## What Maps Cleanly to SAP

### 1. User Hierarchy Patterns
**Athens Pattern**:
```
Master Admin → Project Admins → Admin Users
```

**SAP Equivalent**:
```
MasterAdmin → CompanyUser → ServiceUserSession
```

**Mapping**:
- Athens `Master Admin` → SAP `MasterAdmin`
- Athens `Project Admin` → SAP `CompanyUser` 
- Athens `Admin User` → SAP `ServiceUserSession`

### 2. Multi-Tenant Architecture
**Athens Pattern**:
```python
athens_tenant_id = models.UUIDField()  # Company isolation
```

**SAP Equivalent**:
```python
company_id = models.ForeignKey(Company)  # Company isolation
```

**Direct Mapping**: Both use company-level isolation with UUID/FK references

### 3. Permission Decorators
**Athens Pattern**:
```python
@permission_classes([IsMasterAdmin])
class MasterView(APIView): pass
```

**SAP Equivalent**:
```python
@permission_classes([IsMasterAdmin])  # Same decorator name
class MasterView(APIView): pass
```

**Direct Mapping**: Permission decorator patterns are identical

### 4. JWT Authentication
**Athens Pattern**:
```python
# JWT with user_type, admin_type claims
{
  'user_id': user.id,
  'user_type': 'masteradmin',
  'admin_type': 'masteradmin',
  'athens_tenant_id': str(tenant_id)
}
```

**SAP Equivalent**:
```python
# JWT with role, company claims
{
  'user_id': user.id,
  'role': 'master_admin',
  'company_id': company.id
}
```

**Mapping**: Token structure similar, field names need adjustment

## What Needs Adaptation

### 1. Masters Login Method

#### Athens Implementation
```python
# Single login endpoint for all user types
POST /authentication/login/
{
  "username": "string",
  "password": "string"
}

# Response includes user_type differentiation
{
  "access": "jwt_token",
  "user_type": "master",
  "admin_type": "master",
  "project_id": null
}
```

#### SAP Adaptation Needed
```python
# Separate login endpoints by role
POST /auth/master-login/     # Master-specific login
POST /auth/company-login/    # Company user login
POST /auth/service-login/    # Service user login

# Or unified with role detection
POST /auth/login/
{
  "username": "string",
  "password": "string",
  "login_type": "master|company|service"  # Explicit type
}
```

**Changes Required**:
- Add role-specific login endpoints or role parameter
- Update token claims to use SAP field names
- Modify frontend login flow to handle SAP response format

### 2. Project Context Storage

#### Athens Implementation
```typescript
// Masters have no project context
interface AuthState {
  projectId: number | null;  // Always null for masters
  usertype: 'masteradmin';
  athens_tenant_id: string;
}

// Masters access all projects in tenant
const projects = await api.get('/project/list/');  // Tenant-scoped
```

#### SAP Adaptation Needed
```typescript
// SAP may use different context structure
interface AuthState {
  companyId: number;           // Company context instead of tenant
  serviceId: number | null;    // Service context instead of project
  role: 'master_admin';        // Role instead of user_type
}

// Masters access all services in company
const services = await api.get('/services/list/');  // Company-scoped
```

**Changes Required**:
- Replace `athens_tenant_id` with `company_id`
- Replace `projectId` with `serviceId` (if applicable)
- Update auth store field names
- Modify API endpoints to use SAP terminology

### 3. Assignment Rules

#### Athens Assignment Logic
```python
# Masters create and assign project admins to projects
# Project admins create admin users
# Automatic tenant inheritance

class CustomUser(models.Model):
    athens_tenant_id = models.UUIDField()  # Inherited from creator
    project = models.ForeignKey(Project)   # Assigned by master
    created_by = models.ForeignKey('self') # Hierarchy tracking
```

#### SAP Adaptation Needed
```python
# Masters create and assign company users to services
# Company users create service user sessions
# Company-based inheritance

class User(models.Model):
    company = models.ForeignKey(Company)      # Company assignment
    service = models.ForeignKey(Service)      # Service assignment
    created_by = models.ForeignKey('self')    # Hierarchy tracking
    role = models.CharField()                 # Role-based access
```

**Changes Required**:
- Replace Project model with Service model
- Update assignment logic to use company/service hierarchy
- Modify user creation workflows
- Update permission checks to use SAP role system

## Dependencies to Implement in SAP

### 1. Core Models
**Required Models**:
```python
# SAP equivalent of Athens models
class MasterAdmin(AbstractUser):
    company = models.ForeignKey(Company)
    role = models.CharField(default='master_admin')

class CompanyUser(AbstractUser):
    company = models.ForeignKey(Company)
    service = models.ForeignKey(Service)
    created_by = models.ForeignKey(MasterAdmin)
    role = models.CharField(default='company_user')

class ServiceUserSession(AbstractUser):
    company = models.ForeignKey(Company)
    service = models.ForeignKey(Service)
    created_by = models.ForeignKey(CompanyUser)
    role = models.CharField(default='service_user')

class Service(models.Model):  # SAP equivalent of Project
    company = models.ForeignKey(Company)
    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=50)
    # ... other service fields

class Company(models.Model):  # SAP equivalent of Tenant
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    # ... other company fields
```

### 2. Permission System
**Required Permissions**:
```python
# SAP permission classes
class IsMasterAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'master_admin'

class IsCompanyUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'company_user'

class IsServiceUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'service_user'

# Company isolation mixin
class CompanyIsolationMixin:
    def get_queryset(self):
        return super().get_queryset().filter(
            company=self.request.user.company
        )
```

### 3. Middleware Stack
**Required Middleware**:
```python
# SAP middleware equivalents
class CompanyIsolationMiddleware:
    """Enforce company-level isolation"""
    def __call__(self, request):
        if request.user.is_authenticated:
            request.company = request.user.company
        return self.get_response(request)

class ServiceContextMiddleware:
    """Handle service context for non-masters"""
    def __call__(self, request):
        if request.user.is_authenticated and request.user.role != 'master_admin':
            request.service = getattr(request.user, 'service', None)
        return self.get_response(request)
```

### 4. API Endpoints
**Required Endpoints**:
```python
# Master admin endpoints
POST /auth/master-login/
GET  /masters/services/list/
POST /masters/services/create/
POST /masters/company-users/create/
PUT  /masters/company-users/<id>/reset-password/

# Company user endpoints  
POST /auth/company-login/
GET  /company-users/service-sessions/list/
POST /company-users/service-sessions/create/

# Service user endpoints
POST /auth/service-login/
GET  /service-users/profile/
```

### 5. Frontend Components
**Required Components**:
```typescript
// Master admin components
MasterLoginPage.tsx
ServicesList.tsx
ServiceCreation.tsx
CompanyUserManagement.tsx

// Company user components
CompanyLoginPage.tsx
ServiceSessionsList.tsx
ServiceSessionCreation.tsx

// Service user components
ServiceLoginPage.tsx
ServiceDashboard.tsx
```

## Migration Strategy

### Phase 1: Core Infrastructure
1. **Create SAP Models**
   - Implement Company, Service, MasterAdmin, CompanyUser, ServiceUserSession
   - Set up foreign key relationships
   - Add role-based fields

2. **Implement Authentication**
   - Create role-specific login endpoints
   - Update JWT token structure
   - Implement permission classes

3. **Set up Middleware**
   - Company isolation middleware
   - Service context middleware
   - Permission enforcement

### Phase 2: Master Admin Features
1. **Service Management**
   - Clone Athens project CRUD to service CRUD
   - Update field names and validation rules
   - Implement company-scoped filtering

2. **User Management**
   - Clone Athens admin creation to company user creation
   - Update assignment logic
   - Implement role-based permissions

3. **Dashboard & Analytics**
   - Clone Athens dashboard components
   - Update data sources to use SAP models
   - Implement company-scoped statistics

### Phase 3: Frontend Migration
1. **Auth Store Updates**
   - Replace Athens field names with SAP equivalents
   - Update token handling logic
   - Modify context management

2. **Component Migration**
   - Clone Athens components to SAP equivalents
   - Update API calls to use SAP endpoints
   - Modify UI text and labels

3. **Routing Updates**
   - Update route paths to use SAP terminology
   - Modify navigation structure
   - Update breadcrumbs and page titles

### Phase 4: Testing & Validation
1. **Unit Tests**
   - Test model relationships
   - Test permission enforcement
   - Test API endpoints

2. **Integration Tests**
   - Test complete workflows
   - Test cross-role interactions
   - Test company isolation

3. **UI Tests**
   - Test login flows
   - Test CRUD operations
   - Test responsive design

## Risk Mitigation

### 1. Data Migration Risks
**Risk**: Data loss during model migration
**Mitigation**: 
- Create migration scripts with rollback capability
- Test migrations on staging environment
- Backup data before migration

### 2. Permission Bypass Risks
**Risk**: Incorrect permission implementation allowing unauthorized access
**Mitigation**:
- Implement comprehensive test suite
- Use consistent permission patterns
- Add audit logging for sensitive operations

### 3. Context Confusion Risks
**Risk**: Mixed Athens/SAP context causing data leaks
**Mitigation**:
- Use clear naming conventions
- Implement strict validation
- Add context verification in middleware

### 4. Frontend State Risks
**Risk**: Inconsistent state management between Athens and SAP patterns
**Mitigation**:
- Create SAP-specific auth store
- Implement state validation
- Add error boundaries for state errors

## Success Criteria

### 1. Functional Parity
- [ ] Master admin can create and manage services (equivalent to projects)
- [ ] Master admin can create and manage company users (equivalent to project admins)
- [ ] Company users can create and manage service user sessions (equivalent to admin users)
- [ ] All CRUD operations work with company isolation
- [ ] Permission system prevents unauthorized access

### 2. Performance Parity
- [ ] API response times similar to Athens
- [ ] Database query efficiency maintained
- [ ] Frontend rendering performance maintained

### 3. Security Parity
- [ ] Company isolation enforced at all levels
- [ ] Role-based permissions working correctly
- [ ] No cross-company data leaks
- [ ] Audit logging for sensitive operations

### 4. User Experience Parity
- [ ] Login flows intuitive and fast
- [ ] Navigation structure clear and consistent
- [ ] CRUD operations smooth and responsive
- [ ] Error handling informative and helpful