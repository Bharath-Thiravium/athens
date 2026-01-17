# SAP-Athens Integration Architecture

## 🔑 **Entry Point Rule (NON-NEGOTIABLE)**

### **Single Entry Point**
```
SAP Issues: usertype: masteradmin → Athens Accepts
```

### **Athens Responsibility (Service Plane Only)**
- ✅ Accept SAP-issued `usertype: masteradmin` credentials
- ✅ Validate Athens service is active for company
- ✅ Treat `usertype: masteradmin` as full administrative authority inside Athens
- ✅ Manage internal users, projects, modules, permissions independently
- ✅ Enforce data isolation using `athens_tenant_id`

### **Athens Must NOT**
- ❌ Create master users
- ❌ Authenticate SAP passwords (trusts SAP-issued credentials)
- ❌ Modify SAP credentials
- ❌ Interpret SAP usertypes beyond `masteradmin`
- ❌ Control SAP-side service activation

## 🏛️ **Responsibility Separation**

### **SAP Responsibilities**
```
SAP Controls:
├── Master credential issuance
├── Service enable/disable state
├── Company onboarding/offboarding
└── Athens service activation per company
```

### **Athens Responsibilities**
```
Athens Controls:
├── Internal user management
├── Project management
├── Module permissions
├── Data isolation (athens_tenant_id)
└── Business workflows
```

## 🔒 **Access Enforcement Flow**

### **Master User Authentication**
```python
def authenticate_sap_master(user, password):
    # 1. Validate SAP-issued credentials
    if not user.check_password(password):
        return None
    
    # 2. Check Athens service activation
    tenant = AthensTenant.objects.get(id=user.athens_tenant_id)
    if not tenant.is_active:
        return None  # SAP disabled Athens service
    
    # 3. Grant full Athens access
    return user
```

### **Service Deactivation**
```
If SAP disables Athens service:
├── AthensTenant.is_active = False
├── All company access immediately denied
└── Master user cannot authenticate
```

## 🎯 **User Type Hierarchy**

### **SAP-Issued (External)**
```
usertype: masteradmin
├── Issued by: SAP
├── Athens Access: Full administrative
├── Tenant Scope: Single company
└── Data Access: All company data
```

### **Athens-Managed (Internal)**
```
Athens Internal Users:
├── projectadmin: Project-level admin
├── adminuser: Department-level user
├── worker: Operational user
└── All managed inside Athens only
```

## 📊 **Authentication Matrix**

| User Type | Credential Source | Athens Access | Tenant Restriction |
|-----------|------------------|---------------|-------------------|
| **masteradmin** | SAP-issued | Full admin | Single company |
| **projectadmin** | Athens-managed | Project admin | Single company |
| **adminuser** | Athens-managed | Department user | Single company |
| **worker** | Athens-managed | Operational | Single company |

## 🛡️ **Security Implementation**

### **Entry Point Validation**
```python
class SAPIntegratedAuthBackend:
    def authenticate(self, username, password):
        user = CustomUser.objects.get(username=username)
        
        if user.user_type == 'masteradmin':
            return self._authenticate_sap_master(user, password)
        else:
            return self._authenticate_athens_user(user, password)
```

### **Service Activation Check**
```python
def _authenticate_sap_master(self, user, password):
    # Validate Athens service is active
    tenant = AthensTenant.objects.get(id=user.athens_tenant_id)
    if not tenant.is_active:
        return None  # Service disabled by SAP
    
    return user
```

## ✅ **Integration Benefits**

1. **Clear Separation**: SAP vs Athens responsibilities
2. **Single Entry Point**: Only `usertype: masteradmin` from SAP
3. **Service Control**: SAP can enable/disable Athens per company
4. **Internal Autonomy**: Athens manages internal users independently
5. **Security**: No cross-tenant data access
6. **Scalability**: Decoupled authentication systems

## 🚨 **Critical Rules**

### **DO:**
- Accept only `usertype: masteradmin` from SAP
- Validate Athens service activation on every master login
- Manage all other users internally in Athens
- Enforce `athens_tenant_id` isolation

### **DON'T:**
- Create or modify master users in Athens
- Interpret SAP usertypes beyond `masteradmin`
- Allow cross-tenant access
- Bypass service activation checks

## 📋 **Implementation Checklist**

- [x] `SAPIntegratedAuthBackend` implemented
- [x] Master user entry point validation
- [x] Athens service activation checks
- [x] Tenant isolation enforcement
- [x] Internal user management separation
- [x] Documentation complete

This architecture ensures **clean SAP-Athens integration** with **absolute tenant isolation** and **clear responsibility boundaries**.