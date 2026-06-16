# Frontend Components & State Management

## Layout Components

### Master Layout Structure
**Primary Layout**: Standard dashboard layout with master-specific navigation
**File**: `/app/frontend/src/common/components/PageLayout.tsx`

### Layout Usage in Masters Pages
```typescript
// In ProjectsList.tsx
<PageLayout
  title="Projects Management"
  subtitle="Manage and track all project information"
  icon={<ProjectOutlined />}
  breadcrumbs={[{ title: 'Projects' }]}
  actions={
    <Button type="primary" icon={<PlusOutlined />} onClick={handleAddProject}>
      Add New Project
    </Button>
  }
>
  <Card variant="borderless">
    <Table columns={columns} dataSource={projects} />
  </Card>
</PageLayout>
```

### Navigation Components
- **Header**: Contains user profile, notifications, logout
- **Sidebar**: Master-specific menu items
- **Breadcrumbs**: Contextual navigation path
- **No Project Selector**: Masters don't have project dropdown

## State Management Pattern

### Zustand Auth Store
**File**: `/app/frontend/src/common/store/authStore.ts`
**Pattern**: Zustand with persistence

### Auth State Interface
```typescript
interface AuthState {
  // Authentication
  token: string | null;
  refreshToken: string | null;
  
  // User Identity
  username: string | null;
  userId: number | null;
  usertype: string | null;           // 'masteradmin' for masters
  django_user_type: string | null;   // 'masteradmin' for masters
  isSuperAdmin: boolean;
  
  // Context (null for masters - they operate at tenant level)
  projectId: number | null;
  
  // Profile Status
  isPasswordResetRequired: boolean;
  grade: string | null;
  department: string | null;
  is_approved: boolean;
  has_submitted_details: boolean;
  
  // Actions
  setToken: (token: string, refresh: string, projectId: number | null, ...) => void;
  clearToken: () => void;
  updateProfile: (updates: Partial<AuthState>) => void;
}
```

### Master-Specific State Logic
```typescript
// Masters have no projectId
const setToken = (
  token: string,
  refresh: string,
  projectId: number | null,  // Always null for masters
  username: string,
  usertype: string,
  django_user_type: string,
  isSuperAdmin: boolean,
  // ... other params
) => {
  // For masters, projectId is always null
  const isMaster = usertype === 'masteradmin' || django_user_type === 'masteradmin';
  const finalProjectId = isMaster ? null : projectId;
  
  set({
    token,
    refreshToken: refresh,
    projectId: finalProjectId,
    username,
    usertype,
    django_user_type,
    isSuperAdmin,
    // ... other fields
  });
};
```

## Token & Session Persistence

### Storage Configuration
```typescript
// Zustand persist configuration
const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // ... state and actions
    }),
    {
      name: 'auth-storage',        // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({   // What to persist
        token: state.token,
        refreshToken: state.refreshToken,
        username: state.username,
        usertype: state.usertype,
        django_user_type: state.django_user_type,
        projectId: state.projectId,
        userId: state.userId,
        // ... other persistent fields
      }),
    }
  )
);
```

### Token Storage Keys
- **Primary Key**: `auth-storage` (Zustand persist)
- **Storage Type**: `localStorage` (persistent across sessions)
- **Fallback**: `sessionStorage` (if localStorage fails)

### Selected Project Storage
```typescript
// Masters don't have "selected project" - they operate at tenant level
// projectId is always null for masters
const projectId = get().projectId; // null for masters

// Project context comes from URL params or API calls, not global state
const currentProjectId = useParams().projectId; // From route params
```

## API Client & Interceptors

### Axios Setup
**File**: `/app/frontend/src/common/utils/axiosetup.ts`

### Request Interceptors
```typescript
// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Response Interceptors
```typescript
// Handle token refresh and auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired - attempt refresh
      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const response = await api.post('/authentication/token/refresh/', {
            refresh: refreshToken
          });
          const newToken = response.data.access;
          useAuthStore.getState().setToken(newToken, refreshToken, /* ... other params */);
          // Retry original request
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed - redirect to login
          useAuthStore.getState().clearToken();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

## Error Handling

### API Error Handler
**File**: `/app/frontend/src/utils/apiErrorHandler.ts`

### Error Handling Patterns
```typescript
// In ProjectCreation.tsx
const handleApiCall = async (apiCall: () => Promise<any>, operation: string) => {
  try {
    const response = await apiCall();
    return response.data;
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || 
                        error.response?.data?.error || 
                        `Failed to ${operation.toLowerCase()}`;
    message.error(errorMessage);
    return null;
  }
};

// Usage
const response = await handleApiCall(
  () => api.post('/authentication/master-admin/projects/create/', apiData),
  'Project Creation'
);
```

### 401/403 Handling
```typescript
// Unauthorized (401) - Token expired
if (error.response?.status === 401) {
  // Handled by axios interceptor - attempts token refresh
  // If refresh fails, redirects to login
}

// Forbidden (403) - Insufficient permissions
if (error.response?.status === 403) {
  message.error('You do not have permission to perform this action');
  // Stay on current page, show error
}
```

## Component State Patterns

### Local State Management
```typescript
// In ProjectsList.tsx
const [projects, setProjects] = useState<Project[]>([]);
const [loading, setLoading] = useState(false);
const [currentPage, setCurrentPage] = useState(1);
const [pageSize, setPageSize] = useState(10);

// Modal states
const [viewingProject, setViewingProject] = useState<Project | null>(null);
const [editingProject, setEditingProject] = useState<Project | null>(null);
const [addingProject, setAddingProject] = useState(false);
```

### Data Fetching Patterns
```typescript
// useCallback for stable references
const fetchProjects = useCallback(async () => {
  setLoading(true);
  try {
    const response = await api.get('/authentication/project/list/');
    const projects = Array.isArray(response.data) ? response.data : [];
    setProjects(projects);
  } catch (error) {
    message.error('Failed to fetch projects');
  } finally {
    setLoading(false);
  }
}, [message]);

// useEffect for initial load
useEffect(() => {
  fetchProjects();
}, [fetchProjects]);
```

### Form State Management
```typescript
// Ant Design Form integration
const [form] = Form.useForm();

// Form submission
const onFinish = async (values: any) => {
  setLoading(true);
  try {
    await api.post('/authentication/master-admin/projects/create/', values);
    message.success('Project created successfully!');
    form.resetFields();
    onSuccess?.(); // Callback to parent
  } catch (error) {
    // Error handling
  } finally {
    setLoading(false);
  }
};
```

## Component Communication

### Parent-Child Communication
```typescript
// Parent (ProjectsList) to Child (ProjectCreation)
<ProjectCreation onSuccess={handleCreateSuccess} />

// Child callback to parent
const ProjectCreation: React.FC<{ onSuccess?: () => void }> = ({ onSuccess }) => {
  const handleSubmit = async () => {
    // ... API call
    onSuccess?.(); // Notify parent of success
  };
};
```

### Modal State Coordination
```typescript
// Centralized modal state in parent
const handleCancel = () => {
  setViewingProject(null);
  setEditingProject(null);
  setAddingProject(false);
};

// Success handlers for different operations
const handleCreateSuccess = () => {
  const newProjectPage = Math.ceil((projects.length + 1) / pageSize);
  setCurrentPage(newProjectPage);
  handleCancel(); // Close modal
  fetchProjects(); // Refresh data
};

const handleUpdateSuccess = () => {
  handleCancel(); // Close modal
  fetchProjects(); // Refresh data
  // Stay on current page
};
```

## Performance Optimizations

### Memoization
```typescript
// Memoize expensive calculations
const columns = useMemo(() => [
  { title: 'Project Name', dataIndex: 'projectName', key: 'projectName' },
  // ... other columns
], []);

// Memoize callback functions
const handlePaginationChange = useCallback((page: number, size: number) => {
  setCurrentPage(page);
  setPageSize(size);
}, []);
```

### Lazy Loading
```typescript
// Lazy load heavy components
const ProjectMapSelector = lazy(() => import('./ProjectMapSelector'));

// Usage with Suspense
<Suspense fallback={<Spin tip="Loading Map..." />}>
  <ProjectMapSelector position={position} onLocationChange={handleLocationChange} />
</Suspense>
```

### Error Boundaries
```typescript
// Wrap tables in error boundaries
<TableErrorBoundary>
  <Table columns={columns} dataSource={projects} />
</TableErrorBoundary>
```