# User Authentication and Role Detection System

## Overview

The authentication system implements a two-tier role-based access control mechanism that identifies and manages different user types throughout the application. This document explains how the system detects and handles various user roles including master, client, EPC, contractor, clientuser, epcuser, and contractoruser.

## System Architecture

### User Type Classification

The system uses a two-level classification approach:

1. **Primary Classification** (`user_type`):
   - `projectadmin`: Users with administrative privileges for a specific project
   - `adminuser`: Regular users with role-specific permissions

2. **Secondary Classification** (`admin_type`):
   - `master`: Super admin with full system access
   - `client`: Client organization administrator
   - `epc`: EPC (Engineering, Procurement, Construction) organization administrator
   - `contractor`: Contractor organization administrator
   - `clientuser`: Regular user from client organization
   - `epcuser`: Regular user from EPC organization
   - `contractoruser`: Regular user from contractor organization

### Special Cases

- **Multiple Contractors**: When multiple contractor admins exist in a project, they are distinguished by appending an index (e.g., `contractor1`, `contractor2`) to their usertype.

## Backend Implementation

### User Model

The `CustomUser` model extends Django's `AbstractUser` with additional fields:

```python
class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=20, choices=[
        ('projectadmin', 'Project Admin'),
        ('adminuser', 'Admin User'),
    ], default='adminuser')
    
    admin_type = models.CharField(max_length=20, choices=[
        ('master', 'Master'),
        ('client', 'Client'),
        ('epc', 'EPC'),
        ('contractor', 'Contractor'),
        ('clientuser', 'Client User'),
        ('epcuser', 'EPC User'),
        ('contractoruser', 'Contractor User'),
    ], null=True, blank=True)
    
    # Other fields...
```

### JWT Token Generation

The system extends the standard JWT token with user role information:

```python
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user.__class__.objects.get(pk=self.user.pk)
        
        if user.user_type == 'projectadmin':
            # Special handling for contractor admins
            if user.admin_type == 'contractor':
                contractor_admins = CustomUser.objects.filter(
                    project=user.project, 
                    user_type='projectadmin', 
                    admin_type='contractor'
                ).order_by('id')
                
                index = None
                for i, admin in enumerate(contractor_admins, start=1):
                    if admin.pk == user.pk:
                        index = i
                        break
                        
                if index:
                    data['usertype'] = f'contractor{index}'
                else:
                    data['usertype'] = user.admin_type
            else:
                data['usertype'] = user.admin_type
                
            data['username'] = user.username
            
        elif user.user_type == 'adminuser':
            data['usertype'] = user.admin_type
            data['username'] = user.email
            
        data['django_user_type'] = user.user_type
        
        return data
```

## Frontend Implementation

### Auth Store (Zustand)

The frontend uses Zustand for state management, storing authentication and user role information:

```typescript
interface AuthState {
  token: string | null;
  refreshToken: string | null;
  username: string | null;
  projectId: number | null;
  usertype: string | null;        // Specific role (contractor, client, etc.)
  django_user_type: string | null; // Base user type ('projectadmin' or 'adminuser')
  userId: string | number | null;
  isPasswordResetRequired: boolean;
  lastRefreshTime: number | null;
  tokenExpiry: string | null;
  
  // Methods
  setToken: (token: string | null, refreshToken: string | null, /* other params */) => void;
  isAuthenticated: () => boolean;
  logout: () => Promise<void>;
  // Other methods...
}

const useAuthStore = create<AuthState>((set, get) => ({
  // Initialize from localStorage
  token: getStoredItem('token'),
  refreshToken: getStoredItem('refreshToken'),
  username: getStoredItem('username'),
  projectId: getStoredItem('projectId') ? parseInt(getStoredItem('projectId')!, 10) : null,
  usertype: getStoredItem('usertype'),
  django_user_type: getStoredItem('django_user_type'),
  userId: getStoredItem('userId'),
  // Other state...
  
  // Methods implementation...
}));
```

### Local Storage Persistence

The system persists authentication information in localStorage for session continuity:

```typescript
setToken: (
  token: string | null,
  refreshToken: string | null,
  projectId: number | null,
  username: string | null,
  usertype: string | null,
  django_user_type: string | null,
  userId: string | number | null,
  isPasswordResetRequired: boolean
) => {
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('tokenExpiry', expiryDate!);
    } else {
      localStorage.removeItem('token');
      localStorage.removeItem('tokenExpiry');
    }
    // Store other user data...
  }
  
  set({
    token,
    refreshToken,
    projectId,
    username,
    usertype,
    django_user_type,
    userId,
    isPasswordResetRequired,
    tokenExpiry: expiryDate,
  });
}
```

## Authentication Flow

1. **Login Process**:
   - User submits credentials to the backend
   - Backend validates credentials and generates JWT tokens
   - Backend adds user type information to the token response
   - Frontend stores this information in the auth store and localStorage

2. **Role Detection**:
   - The system uses two levels of role classification:
     - `django_user_type`: Primary classification ('projectadmin' or 'adminuser')
     - `usertype`: Secondary, more specific role (client, epc, contractor, etc.)
   - For contractor admins, an index is appended (e.g., 'contractor1') to distinguish multiple contractors

3. **Role-Based Access Control**:
   - Components check `usertype` and `django_user_type` to determine:
     - Which UI elements to display
     - Which routes are accessible
     - Which actions are permitted

4. **Token Refresh**:
   - When tokens are refreshed, user role information is preserved
   - The system maintains the user's role context throughout their session

5. **Logout Process**:
   - Sends logout request to backend to invalidate refresh token
   - Clears all authentication data from localStorage and state store

## Usage Examples

### Checking User Type in Components

```typescript
import useAuthStore from '../common/store/authStore';

function MyComponent() {
  const { usertype, django_user_type } = useAuthStore();
  
  // Check if user is a contractor
  const isContractor = usertype?.startsWith('contractor');
  
  // Check if user is a project admin
  const isProjectAdmin = django_user_type === 'projectadmin';
  
  // Render appropriate UI based on role
  return (
    <div>
      {isProjectAdmin && <AdminControls />}
      {isContractor && <ContractorView />}
    </div>
  );
}
```

### Protected Routes

```typescript
import useAuthStore from '../common/store/authStore';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ allowedRoles, children }) {
  const { usertype, isAuthenticated } = useAuthStore();
  
  // Check if user is authenticated
  if (!isAuthenticated()) {
    return <Navigate to="/login" />;
  }
  
  // Check if user has required role
  const hasRequiredRole = allowedRoles.some(role => {
    if (role.endsWith('*')) {
      // Handle wildcard roles (e.g., 'contractor*')
      const prefix = role.slice(0, -1);
      return usertype?.startsWith(prefix);
    }
    return usertype === role;
  });
  
  if (!hasRequiredRole) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
}
```

## Security Considerations

1. **Token Storage**: 
   - User role information is stored in both the JWT token and localStorage
   - Tokens have a limited lifespan (55 minutes) to reduce security risks

2. **Role Verification**: 
   - Critical operations should verify roles on the backend
   - Frontend role checks are for UI purposes only and not security enforcement

3. **Token Expiry**: 
   - Tokens expire after 55 minutes to limit the window of potential misuse
   - The system tracks token expiry and can prompt for re-authentication

4. **Logout Handling**: 
   - The logout process clears all role information from storage
   - Backend invalidates the refresh token to prevent reuse

## Best Practices

1. **Always verify permissions on the backend** for any sensitive operations
2. **Use the `isAuthenticated()` method** to check authentication status rather than directly checking token existence
3. **Handle role-specific UI conditionally** to prevent unauthorized access to features
4. **Consider token refresh timing** to maintain session continuity without disrupting user experience
5. **Implement proper error handling** for authentication failures and permission denials