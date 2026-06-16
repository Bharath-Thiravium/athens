# Athens Super Admin Module - Frontend Routes & Pages

## Route Configuration

### Main Route Registration
**File**: `app/frontend/src/app/App.tsx`

```typescript
<Route path="/superadmin" element={<SuperadminLayout />}>
  <Route index element={<Navigate to="dashboard" replace />} />
  <Route path="dashboard" element={<SuperadminDashboard />} />
  <Route path="tenants" element={<TenantsPage />} />
  <Route path="masters" element={<MastersPage />} />
  <Route path="subscriptions" element={<SubscriptionsPage />} />
  <Route path="audit-logs" element={<AuditLogsPage />} />
  <Route path="settings" element={<SuperadminSettings />} />
</Route>
```

### Route Guards & Redirects

#### Authentication Guard
**File**: `app/frontend/src/features/superadmin/components/SuperadminLayout.tsx`
```typescript
// Guards (after hooks)
if (!token) return <Navigate to="/login" replace />;
if (!isSuperAdmin) return <Navigate to="/dashboard" replace />;
```

#### Auto-redirect Logic
**File**: `app/frontend/src/app/App.tsx`
```typescript
const ProtectedDashboard: React.FC = () => {
  const { token, isAuthenticated, isSuperAdmin } = useAuthStore();
  
  if (!token || !isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (isSuperAdmin) {
    return <Navigate to="/superadmin/dashboard" replace />;
  }

  return <Dashboard />;
};
```

## Page Components

### 1. SuperadminDashboard
**File**: `app/frontend/src/features/superadmin/pages/SuperadminDashboard.tsx`

**Purpose**: Platform overview with key metrics and recent activity

**UI Sections**:
- Tenant metrics cards (Total, Active, Trialing, Suspended)
- Master users count
- Recent SaaS activity list (audit logs)
- Tenant status breakdown

**Data Sources**:
- `fetchTenants()` - Tenant list and counts
- `fetchMasters()` - Master user count
- `fetchAuditLogs({})` - Recent platform activity

### 2. TenantsPage
**File**: `app/frontend/src/features/superadmin/pages/TenantsPage.tsx`

**Purpose**: Complete tenant/company management

**UI Sections**:
- Tenant list table with actions
- Create/Edit tenant modal
- Module management modal (enable/disable modules per tenant)
- Tenant sync modal (create AthensTenant record)

**Key Actions**:
- Create tenant
- Edit tenant details
- Suspend/Reactivate tenant
- Delete tenant
- Manage tenant modules
- Sync tenant for module management

### 3. MastersPage
**File**: `app/frontend/src/features/superadmin/pages/MastersPage.tsx`

**Purpose**: Master admin user management

**UI Sections**:
- Master users table with search/filter
- Create/Edit master user modal
- Tenant assignment

### 4. SubscriptionsPage
**File**: `app/frontend/src/features/superadmin/pages/SubscriptionsPage.tsx`

**Purpose**: Billing and subscription management

**UI Sections**:
- Subscription list with tenant details
- Plan management
- Billing status tracking

### 5. AuditLogsPage
**File**: `app/frontend/src/features/superadmin/pages/AuditLogsPage.tsx`

**Purpose**: Platform activity audit trail

**UI Sections**:
- Filterable audit log table
- Action details and timestamps
- Actor information

### 6. SuperadminSettings
**File**: `app/frontend/src/features/superadmin/pages/SuperadminSettings.tsx`

**Purpose**: Global platform configuration

**UI Sections**:
- Platform branding settings
- Email configuration
- Security settings
- Billing provider settings

## Layout Component

### SuperadminLayout
**File**: `app/frontend/src/features/superadmin/components/SuperadminLayout.tsx`

**Features**:
- Responsive sidebar with menu items
- Theme toggle (light/dark)
- Notification dropdown
- User profile dropdown
- Mobile-friendly navigation

**Menu Structure**:
```typescript
const menuItems = [
  { key: '/superadmin/dashboard', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/superadmin/tenants', icon: <ApartmentOutlined />, label: 'Tenants (Companies)' },
  { key: '/superadmin/masters', icon: <TeamOutlined />, label: 'Masters' },
  { key: '/superadmin/subscriptions', icon: <CreditCardOutlined />, label: 'Subscriptions / Billing' },
  { key: '/superadmin/audit-logs', icon: <AuditOutlined />, label: 'Audit Logs' },
  { key: '/superadmin/settings', icon: <SettingOutlined />, label: 'Settings' },
];
```

## Entry Points

### Main App Router
**File**: `app/frontend/src/app/App.tsx`

The Super Admin routes are integrated into the main application router with proper guards and redirects.

### Lazy Loading
All Super Admin components are lazy-loaded:
```typescript
const SuperadminLayout = React.lazy(() => import('@features/superadmin/components/SuperadminLayout'));
const SuperadminDashboard = React.lazy(() => import('@features/superadmin/pages/SuperadminDashboard'));
const TenantsPage = React.lazy(() => import('@features/superadmin/pages/TenantsPage'));
// ... etc
```

## Navigation Flow

1. **Login** → Authentication check → Superadmin redirect
2. **Dashboard** → Overview metrics and activity
3. **Tenants** → Company management and module control
4. **Masters** → User management for tenant admins
5. **Subscriptions** → Billing and plan management
6. **Audit Logs** → Activity tracking and compliance
7. **Settings** → Platform configuration

## Route Protection

- All routes require authentication (`token` check)
- All routes require superadmin role (`isSuperAdmin` check)
- Non-superadmin users are redirected to regular dashboard
- Unauthenticated users are redirected to login