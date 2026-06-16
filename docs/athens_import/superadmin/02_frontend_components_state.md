# Athens Super Admin Module - Frontend Components & State

## Reusable Components Used

### Ant Design Components
The Super Admin module heavily uses Ant Design components:

**From SuperadminLayout.tsx**:
- `Layout`, `Menu`, `Typography`, `Button`, `Avatar`, `Space`, `Dropdown`, `Badge`, `Card`
- Icons: `DashboardOutlined`, `ApartmentOutlined`, `TeamOutlined`, `CreditCardOutlined`, `AuditOutlined`, `SettingOutlined`

**From TenantsPage.tsx**:
- `Table`, `Modal`, `Form`, `Input`, `Select`, `Checkbox`, `Tag`, `message`
- Table with pagination and action buttons
- Modal forms for CRUD operations

**From SuperadminDashboard.tsx**:
- `Card`, `Col`, `Row`, `Typography`, `List`, `Tag`, `Alert`
- Metric cards layout
- Activity lists

### Custom Components

#### SuperadminLayout
**File**: `app/frontend/src/features/superadmin/components/SuperadminLayout.tsx`

**Features**:
- Responsive sidebar with collapsible menu
- Theme toggle integration
- Notification system integration
- Profile dropdown with logout
- Mobile-friendly navigation

**Key Props**: None (uses Outlet for child routes)

**State Management**:
- Uses `useAuthStore` for user authentication state
- Uses `useTheme` for theme management
- Uses `useResponsiveSidebar` for responsive behavior
- Uses `useNotificationsContext` for notifications

#### PageLayout
**File**: `@common/components/PageLayout`

Used within SuperadminLayout to provide consistent page structure:
```typescript
<PageLayout title={currentTitle} showDivider={false} className="saas-page-layout">
  <Outlet />
</PageLayout>
```

## State Management Pattern

### Authentication Store (Zustand)
**File**: `@common/store/authStore`

**Used State**:
```typescript
const { token, isAuthenticated, isSuperAdmin, logout, username } = useAuthStore();
```

**Key Methods**:
- `isAuthenticated()` - Check if user has valid token
- `isSuperAdmin` - Boolean flag for superadmin access
- `logout()` - Clear authentication and redirect

### Theme Context
**File**: `@common/contexts/ThemeContext`

**Usage**:
```typescript
const { setTheme, effectiveTheme } = useTheme();
```

**Features**:
- Light/dark theme toggle
- Persistent theme preference
- Theme-aware styling

### Notifications Context
**File**: `@common/contexts/NotificationsContext`

**Usage**:
```typescript
const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotificationsContext();
```

**Features**:
- Real-time notification display
- Unread count badge
- Mark as read functionality

### Local Component State
Each page component manages its own local state using React hooks:

**TenantsPage.tsx Example**:
```typescript
const [tenants, setTenants] = useState<Tenant[]>([]);
const [loading, setLoading] = useState(false);
const [modalVisible, setModalVisible] = useState(false);
const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
const [form] = Form.useForm<Tenant>();
```

## API Client Integration

### SaaS API Service
**File**: `app/frontend/src/features/superadmin/services/saasApi.ts`

**HTTP Client**: Uses `@common/utils/axiosetup` (configured Axios instance)

**Key Functions**:
```typescript
// Tenant Management
export const fetchTenants = async () => {
  const { data } = await api.get('/api/saas/tenants/');
  return data;
};

export const createTenant = async (payload: TenantPayload) => {
  const { data } = await api.post('/api/saas/tenants/', payload);
  return data;
};

// Master User Management
export const fetchMasters = async () => {
  const { data } = await api.get('/api/saas/masters/');
  return data;
};

// Module Management
export const fetchTenantModules = async (tenantId: string) => {
  const { data } = await api.get(`/api/saas/tenants/${tenantId}/modules`);
  return data;
};
```

### API Interceptors & Token Storage
**File**: `@common/utils/axiosetup`

**Features**:
- Automatic token attachment to requests
- Response interceptors for error handling
- CSRF token management (if needed)

## Form Validation

### Ant Design Form Integration
**Example from TenantsPage.tsx**:
```typescript
const [form] = Form.useForm<Tenant>();

// Form validation rules
<Form.Item name="name" label="Name" rules={[{ required: true }]}>
  <Input />
</Form.Item>

// Form submission
const handleSubmit = async () => {
  try {
    const values = await form.validateFields();
    if (editingTenant) {
      await updateTenant(editingTenant.id, values);
    } else {
      await createTenant(values);
    }
  } catch (err: any) {
    message.error(err?.response?.data?.detail || 'Operation failed');
  }
};
```

### Validation Patterns
- Required field validation
- Email format validation
- UUID format validation for IDs
- Custom validation for business rules

## Error Handling

### API Error Handling
```typescript
try {
  const data = await fetchTenants();
  setTenants(normalizeList(data));
} catch (err: any) {
  message.error('Failed to load tenants');
} finally {
  setLoading(false);
}
```

### Data Normalization
```typescript
const normalizeList = (data: any) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
};
```

## Responsive Design

### Responsive Sidebar Hook
**File**: `@common/hooks/useResponsive`

**Usage**:
```typescript
const { collapsed, mobileVisible, toggleSidebar, closeMobileSidebar, isMobile, isTablet } = useResponsiveSidebar();
```

**Features**:
- Automatic sidebar collapse on mobile
- Touch-friendly navigation
- Responsive breakpoints

### Mobile-First Design
- Collapsible sidebar for mobile devices
- Touch-friendly buttons and interactions
- Responsive table layouts
- Mobile-optimized modals

## Component Architecture

### Layout Hierarchy
```
SuperadminLayout
├── Sidebar (Menu + Branding)
├── Header (Title + Actions + Profile)
└── Content
    └── PageLayout
        └── Outlet (Page Components)
```

### Page Component Pattern
```typescript
const PageComponent: React.FC = () => {
  // State management
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // API calls
  const loadData = async () => {
    setLoading(true);
    try {
      const result = await apiCall();
      setData(result);
    } catch (error) {
      message.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };
  
  // Effects
  useEffect(() => {
    loadData();
  }, []);
  
  // Render
  return (
    <Card title="Page Title">
      <Table dataSource={data} loading={loading} />
    </Card>
  );
};
```

## Styling Approach

### CSS Classes
- Uses global CSS classes from `@common/styles/global.css`
- Theme-aware class names (e.g., `!bg-color-bg-base`)
- Responsive utility classes

### Inline Styles
- Dynamic styles based on theme and responsive state
- Conditional styling for mobile/desktop views
- Animation and transition styles