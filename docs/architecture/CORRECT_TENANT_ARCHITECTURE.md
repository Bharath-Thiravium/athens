# Correct Multi-Tenant Database Architecture

## 🏢 Company vs Project Separation

### **CORRECT Architecture:**
```
AthensTenant (Company Level)
├── athens_tenant_id: UUID (Company Identifier)
├── master_admin_id: UUID
└── enabled_modules: JSON

Project (Business Project Level)  
├── athens_tenant_id: UUID (FK to Company)
├── projectName: "Construction Site A"
├── projectCategory: "construction"
└── location: "Mumbai"

User (User Level)
├── athens_tenant_id: UUID (FK to Company)
├── project: FK to Project (Business Project)
└── user_type: "projectadmin"
```

## 🔑 **Isolation Hierarchy**

### **Level 1: Company Isolation (athens_tenant_id)**
```sql
-- Company A users can only see Company A data
SELECT * FROM worker WHERE athens_tenant_id = 'company_a_uuid';

-- Company B users can only see Company B data  
SELECT * FROM incident WHERE athens_tenant_id = 'company_b_uuid';
```

### **Level 2: Project Isolation (within company)**
```sql
-- Company A, Project Alpha users see only Project Alpha data
SELECT * FROM worker 
WHERE athens_tenant_id = 'company_a_uuid' 
AND project_id = 'project_alpha_id';
```

## 📋 **Data Examples**

### **Company A (Reliance Industries)**
```
athens_tenant_id: "550e8400-e29b-41d4-a716-446655440001"

Projects:
├── Project Alpha (Refinery Mumbai)
├── Project Beta (Petrochemical Jamnagar)  
└── Project Gamma (Retail Network)

Users:
├── Master Admin (Cross-project access)
├── Project Admin Alpha (Refinery only)
├── Project Admin Beta (Petrochemical only)
└── Workers (Project-specific)
```

### **Company B (Tata Steel)**
```
athens_tenant_id: "550e8400-e29b-41d4-a716-446655440002"

Projects:
├── Project Delta (Steel Plant Jamshedpur)
├── Project Echo (Mining Operations)
└── Project Foxtrot (Port Operations)

Users:
├── Master Admin (Cross-project access)
├── Project Admin Delta (Steel Plant only)
├── Project Admin Echo (Mining only)
└── Workers (Project-specific)
```

## 🛡️ **Access Control Matrix**

| User Type | Company Access | Project Access | Data Scope |
|-----------|---------------|----------------|------------|
| **SAP Master** | All companies | All projects | Global |
| **Company Master** | Single company | All company projects | Company-wide |
| **Project Admin** | Single company | Single project | Project-specific |
| **Worker** | Single company | Single project | Project-specific |

## 🔒 **Isolation Rules**

### **Company Level (Primary)**
- `athens_tenant_id` enforces company boundaries
- No cross-company data access (except SAP Master)
- Complete data separation between companies

### **Project Level (Secondary)**  
- `project_id` enforces project boundaries within company
- Users can access multiple projects within their company (if authorized)
- Project admins limited to their assigned projects

## 📊 **Database Schema Updates Required**

### **1. User Model Fix**
```python
class CustomUser(AbstractBaseUser):
    # Company isolation (PRIMARY)
    athens_tenant_id = models.UUIDField()  # Company identifier
    
    # Project assignment (SECONDARY)  
    project = models.ForeignKey(Project)  # Business project within company
    
    # User hierarchy
    user_type = models.CharField(choices=[
        ('master', 'SAP Master'),           # Cross-company
        ('company_master', 'Company Master'), # Company-wide  
        ('projectadmin', 'Project Admin'),   # Project-specific
        ('worker', 'Worker'),               # Project-specific
    ])
```

### **2. All Data Models**
```python
class Worker(models.Model):
    # Company isolation (MANDATORY)
    athens_tenant_id = models.UUIDField()
    
    # Project assignment (OPTIONAL - for project-level filtering)
    project = models.ForeignKey(Project, null=True, blank=True)

class Incident(models.Model):
    # Company isolation (MANDATORY)
    athens_tenant_id = models.UUIDField()
    
    # Project assignment (OPTIONAL)
    project = models.ForeignKey(Project, null=True, blank=True)
```

## ✅ **Benefits of Correct Architecture**

1. **Clear Separation**: Companies vs Business Projects
2. **Scalable**: Companies can have unlimited projects
3. **Flexible**: Project-level permissions within companies
4. **Secure**: Complete company data isolation
5. **Business-Aligned**: Matches real-world organizational structure

## 🚨 **Migration Required**

The current system needs migration from:
- `project_id` based company isolation → `athens_tenant_id` based company isolation
- Repurpose `Project` model for actual business projects
- Update all middleware and isolation logic