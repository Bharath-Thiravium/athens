# Frontend Routes & Pages

## Masters UI Routes

### Route Registration
**File**: `/app/frontend/src/app/App.tsx` (main router)
**File**: `/app/frontend/src/features/superadmin/` (superadmin routes)

### Core Masters Routes
```typescript
// Masters management (accessed by superadmin)
/superadmin/masters -> MastersPage.tsx

// Project management (accessed by masters)
/dashboard -> Dashboard (master view)
/projects -> ProjectsList.tsx
/projects/create -> ProjectCreation.tsx
/projects/edit/:id -> ProjectEdit.tsx
/projects/view/:id -> ProjectView.tsx
```

## Masters Login Flow

### Login Route
**Path**: `/login`
**Component**: `/app/frontend/src/features/signin/components/LoginPage.tsx`

### Post-Login Redirect Logic
```typescript
// In LoginPage.tsx onFinish()
if (isPasswordResetRequired) {
  navigate('/reset-password');
} else if (isSuperAdmin) {
  navigate('/superadmin/dashboard', { replace: true });
} else {
  navigate('/dashboard'); // Masters land here
}
```

### Master Identification
```typescript
// Token extraction and normalization
const rawUserType = usertype || user_type || null;
const rawAdminType = django_user_type || admin_type || null;
const normalizedUserType = rawUserType === 'master' || rawUserType === 'MASTER_ADMIN' ? 'masteradmin' : rawUserType;
const normalizedAdminType = rawAdminType === 'master' || rawAdminType === 'MASTER_ADMIN' ? 'masteradmin' : rawAdminType;
```

## Project Management Pages

### 1. Projects List
**Component**: `/app/frontend/src/features/project/components/ProjectsList.tsx`
**Route**: `/projects`
**Features**:
- Table view of all projects (tenant-scoped)
- Actions: View, Edit, Delete
- Pagination with auto-navigation
- Add new project button

### 2. Project Creation
**Component**: `/app/frontend/src/features/project/components/ProjectCreation.tsx`
**Route**: `/projects/create` (modal)
**Features**:
- Form with project details
- Map-based location selection
- GPS location detection
- Emergency contacts
- Project timeline (commencement/deadline dates)

### 3. Project Edit
**Component**: `/app/frontend/src/features/project/components/ProjectEdit.tsx`
**Route**: `/projects/edit/:id` (modal)
**Features**:
- Pre-populated form with existing data
- Same fields as creation
- Update confirmation

### 4. Project View
**Component**: `/app/frontend/src/features/project/components/ProjectView.tsx`
**Route**: `/projects/view/:id` (modal)
**Features**:
- Read-only project details
- Map display of location
- Emergency contact information

## Masters Management (Superadmin)

### Masters Page
**Component**: `/app/frontend/src/features/superadmin/pages/MastersPage.tsx`
**Route**: `/superadmin/masters`
**Features**:
- Table of all master users
- Create/Edit/Delete masters
- Tenant assignment
- Status management (Active/Disabled)

### Masters CRUD Operations
```typescript
// API calls from MastersPage.tsx
import { createMaster, deleteMaster, fetchMasters, fetchTenants, updateMaster } from '../services/saasApi';

// Create master
await createMaster({
  email: values.email,
  password: values.password,
  tenant_id: values.tenant_id,
  username: values.username || values.email,
  is_active: values.is_active,
});

// Update master
await updateMaster(editingMaster.id, {
  email: values.email,
  username: values.username || values.email,
  tenant_id: values.tenant_id,
  is_active: values.is_active,
  password: values.password, // optional
});
```

## Route Guards & Redirects

### Authentication Guard
**File**: `/app/frontend/src/common/components/ProtectedRoute.tsx` (likely)
**Logic**:
```typescript
// Check if user is authenticated
if (!token || !isTokenValid(token)) {
  return <Navigate to="/login" replace />;
}

// Check user type for route access
if (route.requiresMaster && !isMaster) {
  return <Navigate to="/dashboard" replace />;
}
```

### Master-Specific Guards
```typescript
// Masters can access:
const isMaster = usertype === 'masteradmin' || django_user_type === 'masteradmin';

// Routes requiring master access:
- /projects/*
- /admin/dashboard/consolidated
- /master-admin/*
```

## Dashboard Landing

### Master Dashboard
**Route**: `/dashboard`
**Component**: Main dashboard with master-specific widgets
**Features**:
- Consolidated project statistics
- Pending approvals count
- Recent activities
- Quick actions (Create Project, Manage Admins)

### Dashboard Data Sources
```typescript
// API endpoints for master dashboard
/authentication/admin/dashboard/consolidated/  // KPIs and stats
/authentication/admin/pending-details/         // Pending approvals
/authentication/project/list/                  // Projects overview
/authentication/menu/dashboard/stats/          // Menu management stats
```

## Project Selection UI

### No Project Selector for Masters
Masters operate at the **tenant level**, not project level:
- No project dropdown in header
- No "current project" context
- Access to all projects in their tenant
- Project-specific actions done via project management pages

### Project Context in URLs
```typescript
// Masters access projects via:
/projects                    // List all projects
/projects/view/:projectId    // View specific project
/projects/edit/:projectId    // Edit specific project

// Not via global project context like:
/dashboard?project=123       // Not used for masters
```

## Navigation Structure

### Master Navigation Menu
```typescript
// Typical master menu structure
const masterMenuItems = [
  { key: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { key: 'projects', label: 'Projects', path: '/projects' },
  { key: 'admins', label: 'Admin Management', path: '/admin-management' },
  { key: 'approvals', label: 'Pending Approvals', path: '/approvals' },
  { key: 'settings', label: 'Company Settings', path: '/company-settings' },
];
```

### Conditional Menu Items
```typescript
// Show different menu based on user type
const getMenuItems = (userType: string) => {
  if (userType === 'masteradmin') {
    return masterMenuItems;
  } else if (userType === 'projectadmin') {
    return projectAdminMenuItems;
  } else {
    return regularUserMenuItems;
  }
};
```

## Modal vs Page Routing

### Modal Routes (within ProjectsList)
- Project Creation: Modal overlay
- Project Edit: Modal overlay  
- Project View: Modal overlay

### Full Page Routes
- Projects List: Full page
- Dashboard: Full page
- Admin Management: Full page

### Modal State Management
```typescript
// In ProjectsList.tsx
const [viewingProject, setViewingProject] = useState<Project | null>(null);
const [editingProject, setEditingProject] = useState<Project | null>(null);
const [addingProject, setAddingProject] = useState(false);

// Modal visibility controlled by state, not routes
<Modal open={addingProject} onCancel={handleCancel}>
  <ProjectCreation onSuccess={handleCreateSuccess} />
</Modal>
```