# Project Isolation Core Module - Technical Blueprint

## 1. Module Overview

### Module Name
**Project Isolation Core Engine**

### Business Purpose
Multi-tenant data isolation system ensuring complete data segregation between projects and companies. Provides both project-level and company-level (tenant) isolation with automatic query filtering.

### User Roles Involved
- **Master Users**: Can access all tenant data across projects
- **Project Users**: Limited to their assigned project data
- **Company Users**: Limited to their company tenant data

### Dependent Modules
- **Authentication Module**: User project/tenant assignments
- **All Data Modules**: Automatic isolation enforcement

## 2. Functional Scope

### Features Included
- **Project-Level Isolation**: Data filtered by user's assigned project
- **Company-Level Isolation**: Data filtered by athens_tenant_id
- **Automatic Query Filtering**: Transparent isolation in all ViewSets
- **Middleware Enforcement**: Database-level isolation context
- **Master User Bypass**: Full access for system administrators

### Isolation Rules
- **Project Isolation**: Users only see data from their assigned project
- **Tenant Isolation**: Users only see data from their company tenant
- **Creator Validation**: Object access validated against user's context
- **Empty Queryset Fallback**: Returns empty results for unauthorized access

## 3. Technical Architecture

### Core Files
- **project_isolation.py**: Project-level isolation utilities and mixins
- **tenant_isolation.py**: Company-level tenant isolation system
- **middleware.py**: Request-level isolation enforcement

### Key Functions
```python
# Project isolation
apply_project_isolation(queryset, user)
validate_project_access(user, obj)
ProjectIsolationMixin  # ViewSet mixin

# Tenant isolation  
get_tenant_isolated_queryset(queryset, user)
CompanyTenantIsolationMiddleware
TenantIsolationMixin  # ViewSet mixin
```

### Isolation Patterns
```python
# Automatic project filtering
def get_queryset(self):
    queryset = super().get_queryset()
    return apply_project_isolation(queryset, self.request.user)

# Automatic tenant assignment
def perform_create(self, serializer):
    user_tenant_id = getattr(self.request.user, 'athens_tenant_id', None)
    serializer.save(athens_tenant_id=user_tenant_id)
```

## 4. Integration Points

### Incoming Dependencies
- **Authentication**: User project/tenant assignments
- **Database Models**: project and athens_tenant_id fields

### Outgoing Dependencies
- **All Module ViewSets**: Automatic isolation through mixins
- **Database Layer**: Query filtering and context setting
- **API Responses**: Filtered data based on user context

## 5. Current Working State
- ✅ Project-level data isolation
- ✅ Company tenant isolation (athens_tenant_id)
- ✅ Automatic ViewSet integration via mixins
- ✅ Middleware-level enforcement
- ✅ Master user bypass functionality
- ✅ Empty queryset security fallback

---

**Blueprint Version**: 1.0  
**Status**: Production Ready  
**Dependencies**: Authentication, Database Models