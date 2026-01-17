# Enterprise Multi-Tenant EHS Architecture

## 🏢 **Business Reality Implementation**

### **Company Definition (Tenant Level)**
```
AthensTenant = Company
├── athens_tenant_id: UUID (Primary isolation key)
├── Company Type: EPC | Client | Contractor
└── Master Admin: Company owner
```

### **Project Definition (Business Level)**
```
Project = Business Project
├── athens_tenant_id: UUID (Owning company)
├── client_company_id: UUID (Client company)
├── epc_company_id: UUID (EPC company)
└── contractor_company_ids: [UUID] (Contractor companies)
```

## 🔒 **Absolute Isolation Rules**

### **Rule 1: Company Data Separation**
```sql
-- Company A can NEVER see Company B data
WHERE athens_tenant_id = 'company_a_uuid'

-- Company B can NEVER see Company A data  
WHERE athens_tenant_id = 'company_b_uuid'
```

### **Rule 2: Cross-Company Project Participation**
```
Company A (EPC) Project:
├── athens_tenant_id: company_a_uuid (Owner)
├── client_company_id: company_b_uuid (Participant)
└── contractor_company_ids: [company_c_uuid] (Participants)

Data Access:
- Company A: Full access (owner)
- Company B: NO access to Company A's data
- Company C: NO access to Company A's data
```

## 📊 **Real-World Examples**

### **Example 1: EPC Company (Larsen & Toubro)**
```
Company: L&T (athens_tenant_id: lt_uuid)

Projects Owned by L&T:
├── Mumbai Refinery Project
│   ├── Client: Reliance (reliance_uuid)
│   ├── EPC: L&T (lt_uuid) 
│   └── Contractors: [contractor1_uuid, contractor2_uuid]
│
└── Delhi Metro Project
    ├── Client: DMRC (dmrc_uuid)
    ├── EPC: L&T (lt_uuid)
    └── Contractors: [contractor3_uuid]

L&T Data Access:
✅ All L&T workers, incidents, permits
❌ Reliance workers, incidents, permits
❌ DMRC workers, incidents, permits
```

### **Example 2: Client Company (Reliance)**
```
Company: Reliance (athens_tenant_id: reliance_uuid)

Projects Owned by Reliance:
├── Jamnagar Expansion
│   ├── Client: Reliance (reliance_uuid)
│   ├── EPC: Technip (technip_uuid)
│   └── Contractors: [contractor4_uuid]
│
└── Retail Network Expansion  
    ├── Client: Reliance (reliance_uuid)
    ├── EPC: L&T (lt_uuid)
    └── Contractors: [contractor5_uuid]

Reliance Data Access:
✅ All Reliance workers, incidents, permits
❌ L&T workers, incidents, permits  
❌ Technip workers, incidents, permits
```

## 🛡️ **Database Schema Implementation**

### **All Business Tables Must Have:**
```python
class Worker(models.Model):
    # MANDATORY: Company isolation
    athens_tenant_id = models.UUIDField()
    
    # OPTIONAL: Business project assignment
    project = models.ForeignKey(Project, null=True, blank=True)

class Incident(models.Model):
    # MANDATORY: Company isolation
    athens_tenant_id = models.UUIDField()
    
    # OPTIONAL: Business project assignment
    project = models.ForeignKey(Project, null=True, blank=True)
```

### **Query Enforcement:**
```python
# CORRECT: Tenant-based isolation
queryset.filter(athens_tenant_id=user.athens_tenant_id)

# WRONG: Project-based isolation (old method)
# queryset.filter(project_id=user.project.id)
```

## 🎯 **Access Control Matrix**

| User Type | Company Access | Project Access | Cross-Company |
|-----------|---------------|----------------|---------------|
| **SAP Master** | All companies | All projects | ✅ Full access |
| **Company Master** | Single company | All company projects | ❌ No access |
| **Project Admin** | Single company | Single project | ❌ No access |
| **Worker** | Single company | Single project | ❌ No access |

## 🔧 **Middleware Implementation**

### **CompanyTenantIsolationMiddleware**
```python
def process_request(self, request):
    user_tenant_id = getattr(user, 'athens_tenant_id', None)
    
    # Master users: No restrictions
    if user.user_type == 'master':
        request.athens_tenant_id = None
        return None
    
    # Company users: Tenant restrictions
    if not user_tenant_id:
        return JsonResponse({'error': 'NO_TENANT_ACCESS'}, status=403)
    
    request.athens_tenant_id = user_tenant_id
    self._apply_tenant_isolation(user_tenant_id)
```

## ✅ **Benefits Achieved**

1. **Enterprise-Grade Isolation**: Complete company data separation
2. **Business-Aligned**: Matches real EPC/Client/Contractor workflows  
3. **Scalable**: Companies can have unlimited projects
4. **Secure**: No cross-tenant data leakage
5. **Flexible**: Multi-company project participation via role mapping

## 🚨 **Critical Implementation Notes**

### **DO:**
- Use `athens_tenant_id` for ALL company isolation
- Allow projects to reference multiple companies
- Enforce tenant filtering in middleware
- Maintain absolute data separation

### **DON'T:**
- Use `project_id` for company isolation
- Allow cross-tenant queries
- Mix company data under any circumstances
- Treat Project as Company

## 📋 **Migration Checklist**

- [ ] Replace project-based isolation middleware
- [ ] Update all ViewSets to use TenantIsolationMixin
- [ ] Ensure all models have athens_tenant_id
- [ ] Update Project model for multi-company relationships
- [ ] Test cross-company project scenarios
- [ ] Verify absolute tenant isolation