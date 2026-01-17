# Authentication & Authorization Module – Technical Blueprint (Current Working State)

## 1. Module Overview

**Module Name:** Authentication & Authorization System  
**Purpose & Business Objective:** Provides secure user authentication, role-based access control, and multi-tenant isolation for the Athens EHS system. Manages user lifecycle from creation to approval and access control.  
**Key Users / Roles:**
- Master Admin: System-wide user management and tenant control
- Project Admins: Project-level user management (client, epc, contractor)
- Admin Users: Regular users with role-based access (clientuser, epcuser, contractoruser)

**Dependency on other modules:**
- All modules depend on this for authentication and authorization
- Project Management (user-project association)
- Digital Signature System (user signature management)
- Notification System (approval workflows)

## 2. Functional Scope

**Features included:**
- JWT-based authentication with refresh tokens
- Multi-level user hierarchy (Master → Project Admin → Admin User)
- Role-based access control with admin_type classification
- User profile management (UserDetail, AdminDetail, CompanyDetail)
- Approval workflows for user details
- Multi-tenant isolation with athens_tenant_id
- Password management and reset functionality
- Digital signature integration
- Face recognition authentication support
- Project-based user isolation

**Features explicitly excluded:**
- Social media authentication
- Single Sign-On (SSO) integration
- LDAP/Active Directory integration
- Two-factor authentication (2FA)

**Role-based access control behavior:**
- Master Admin: Full system access, can manage all projects and users
- Project Admin (client/epc/contractor): Can create and manage users within their project
- Admin User (clientuser/epcuser/contractoruser): Limited access based on role and project

**Visibility rules:**
- Users can only see data from their assigned project
- Master admins can see all data across tenants
- Approval workflows restrict access until details are approved

## 3. End-to-End Process Flow

### User Authentication Flow:
1. **Trigger:** User submits login credentials
2. **Validation:** System validates username/password against CustomUser model
3. **Processing:** 
   - Generate JWT access and refresh tokens
   - Include user metadata in token (user_type, admin_type, project_id)
   - Check password reset requirements
4. **Response:** Return tokens and user profile data
5. **Success:** User gains access to authorized features
6. **Failure:** Return authentication error

### User Creation Flow (Project Admin):
1. **Trigger:** Project admin creates new user
2. **Validation:** Verify admin permissions and project association
3. **Processing:**
   - Create CustomUser with auto-generated password
   - Set created_by relationship and project association
   - Determine admin_type based on creator's type
   - Send credentials to user
4. **Response:** Return user data with temporary password
5. **User Action:** User logs in and must reset password

### User Approval Flow:
1. **Trigger:** User submits UserDetail or AdminDetail information
2. **Validation:** Check required fields completion
3. **Processing:**
   - Save user details to respective model
   - Send notification to approver (admin or master admin)
   - Set approval status to pending
4. **Approver Action:** Review and approve/reject details
5. **System Action:** Update approval status and notify user
6. **Success:** User gains full system access

### Project Isolation Flow:
1. **Trigger:** Any data access request
2. **Validation:** Check user's project association
3. **Processing:** Filter queries by user's project_id
4. **Response:** Return only project-specific data
5. **Constraint:** Cross-project access blocked except for master admin

## 4. Technical Architecture

### Backend Components:

**Views / Controllers:**
- `CustomTokenObtainPairView` - JWT token generation
- `LogoutView` - Token blacklisting and logout
- `ProjectAdminUserCreateView` - User creation by project admins
- `UserDetailRetrieveUpdateView` - User profile management
- `AdminDetailUpdateView` - Admin profile management
- `ProjectCreateView` - Project management
- `MasterAdminCreateProjectAdminsView` - Master admin user creation

**Services:**
- `CustomUserManager` - User creation and management logic
- Authentication backends for JWT validation
- Password utilities for secure password generation
- Security utilities for input sanitization

**Models:**
- `CustomUser` - Main user model with role hierarchy
- `Project` - Business project model
- `UserDetail` - Extended user profile information
- `AdminDetail` - Admin-specific profile information
- `CompanyDetail` - Company information for master admins
- `UserSignature` - Digital signature storage
- `FormSignature` - Signature usage tracking

### Frontend Components:

**Pages:**
- Login/Signin pages
- User profile management pages
- Admin creation and management interfaces
- Password reset functionality

**Components:**
- Authentication forms
- User detail forms
- Admin approval interfaces
- Profile picture and signature upload

**State management:**
- JWT token storage and refresh
- User profile data caching
- Authentication state management

### APIs used:

**Endpoints:**
- `POST /authentication/login/` - User authentication
- `POST /authentication/logout/` - User logout
- `GET /authentication/project/list/` - Project listing
- `POST /authentication/projectadminuser/create/` - User creation
- `GET /authentication/userdetail/` - User profile retrieval
- `PUT /authentication/admin/detail/update/` - Admin profile update
- `POST /authentication/userdetail/approve/` - User approval

**Request/Response structure:**
```json
// Login Response
{
  "access": "jwt_token",
  "refresh": "refresh_token",
  "username": "user123",
  "user_type": "adminuser",
  "admin_type": "epcuser",
  "project_id": 1,
  "isPasswordResetRequired": false
}

// User Creation Request
{
  "username": "newuser",
  "name": "John",
  "surname": "Doe",
  "designation": "Engineer",
  "department": "Safety"
}
```

### Database entities:

**Tables:**
- `authentication_customuser`
- `authentication_project`
- `authentication_userdetail`
- `authentication_admindetail`
- `authentication_companydetail`
- `authentication_usersignature`
- `authentication_formsignature`

**Key fields:**
- CustomUser: username, user_type, admin_type, project_id, athens_tenant_id
- Project: projectName, projectCategory, athens_tenant_id
- UserDetail: employee_id, mobile, pan, is_approved
- AdminDetail: phone_number, pan_number, gst_number, is_approved

**Relationships:**
- CustomUser.project → Project (ForeignKey)
- CustomUser.created_by → CustomUser (Self-referencing ForeignKey)
- UserDetail.user → CustomUser (OneToOne)
- AdminDetail.user → CustomUser (OneToOne)

## 5. File-Level Blueprint (CRITICAL)

### Backend Files:

**`/backend/authentication/models.py`**
- **Responsibility:** Define all authentication-related database models
- **Key classes:** CustomUser, Project, UserDetail, AdminDetail, CompanyDetail
- **Inputs:** Model field definitions and relationships
- **Outputs:** Database schema and model instances
- **Important conditions:** Multi-tenant isolation fields, user hierarchy validation
- **Risk notes:** Changes to user model affect entire system

**`/backend/authentication/views.py`**
- **Responsibility:** Handle all authentication and user management API endpoints
- **Key functions:** Login, logout, user creation, profile management, approval workflows
- **Inputs:** HTTP requests with authentication data
- **Outputs:** JSON responses with user data and tokens
- **Important conditions:** Project isolation enforcement, permission checking
- **Risk notes:** Security-critical file, changes affect access control

**`/backend/authentication/serializers.py`**
- **Responsibility:** API serialization and validation for authentication data
- **Key classes:** CustomUserSerializer, CustomTokenObtainPairSerializer, UserDetailSerializer
- **Inputs:** Model instances and request data
- **Outputs:** Validated JSON data
- **Important conditions:** Password handling, token generation, field validation
- **Risk notes:** Validation logic affects data integrity

**`/backend/authentication/urls.py`**
- **Responsibility:** URL routing for authentication endpoints
- **Key functions:** Route mapping for all authentication APIs
- **Inputs:** URL patterns and view mappings
- **Outputs:** Routed HTTP endpoints
- **Important conditions:** Proper authentication and permission decorators
- **Risk notes:** URL changes break frontend integration

**`/backend/authentication/permissions.py`**
- **Responsibility:** Custom permission classes for role-based access control
- **Key functions:** IsMasterAdmin, project-based permissions
- **Inputs:** User authentication data
- **Outputs:** Permission granted/denied decisions
- **Important conditions:** Role hierarchy validation, project association checks
- **Risk notes:** Permission logic affects system security

**`/backend/authentication/middleware.py`**
- **Responsibility:** Request/response processing for authentication
- **Key functions:** JWT validation, tenant isolation, security headers
- **Inputs:** HTTP requests and responses
- **Outputs:** Modified requests with user context
- **Important conditions:** Token validation, tenant ID extraction
- **Risk notes:** Middleware errors affect entire application

### Frontend Files:

**`/frontend/src/features/signin/`**
- **Responsibility:** User authentication interface
- **Key functions:** Login form, password reset, token management
- **Inputs:** User credentials and form data
- **Outputs:** Authentication state and navigation
- **Important conditions:** Token storage, error handling
- **Risk notes:** Security vulnerabilities in token handling

**`/frontend/src/features/user/components/userdetail.tsx`**
- **Responsibility:** User profile management interface
- **Key functions:** Profile form, file upload, approval status
- **Inputs:** User profile data and file uploads
- **Outputs:** Updated user profile
- **Important conditions:** File validation, approval workflow
- **Risk notes:** File upload security, data validation

**`/frontend/src/features/admin/components/AdminDetail.tsx`**
- **Responsibility:** Admin profile management interface
- **Key functions:** Admin profile form, company details, approval workflow
- **Inputs:** Admin profile data and company information
- **Outputs:** Updated admin profile
- **Important conditions:** Role-based field visibility, approval status
- **Risk notes:** Privilege escalation through profile manipulation

## 6. Configuration & Setup

### Environment variables used:
- `SECRET_KEY` - Django secret key for cryptographic operations
- `JWT_SECRET_KEY` - JWT token signing key
- `ATHENS_BACKEND_PORT` - Backend server port
- Database configuration variables

### Feature flags:
- `is_password_reset_required` - Forces password reset on first login
- `is_autogenerated_password` - Indicates auto-generated passwords
- `is_approved` - Controls access based on approval status

### Permissions & roles mapping:
- Master Admin: `admin_type='master'`, `user_type='master'`
- Project Admin: `user_type='projectadmin'`, `admin_type` in ['client', 'epc', 'contractor']
- Admin User: `user_type='adminuser'`, `admin_type` in ['clientuser', 'epcuser', 'contractoruser']

### Project / tenant / company isolation logic:
- All models include `athens_tenant_id` for multi-tenant isolation
- Users associated with projects via `project` ForeignKey
- Queries filtered by user's project association
- Master admins bypass project isolation

### Default values & assumptions:
- New users require password reset on first login
- Auto-generated passwords are 16 characters with special characters
- Users default to inactive until approved
- Project association is mandatory for non-master users

## 7. Integration Points

### Modules this depends on:
- Django REST Framework (API functionality)
- Django JWT (token authentication)
- Django signals (automatic profile creation)
- File storage system (profile pictures, signatures)

### Modules that depend on this:
- All application modules (authentication required)
- Menu Management (user-based menu filtering)
- Project Management (user-project association)
- Notification System (approval workflows)
- Digital Signature System (user signature management)

### External services:
- None (self-contained authentication system)

### Auth / token / session usage:
- JWT access tokens (15-minute expiry)
- JWT refresh tokens (7-day expiry)
- Token blacklisting on logout
- Automatic token refresh in frontend

## 8. Current Working State Validation

### Expected UI behavior:
- Login form accepts credentials and redirects on success
- Password reset required for auto-generated passwords
- Profile forms show appropriate fields based on user type
- Approval workflows show pending status until approved
- File uploads work for profile pictures and company logos

### Expected API responses:
- `/authentication/login/` returns JWT tokens and user data
- User creation returns user object with temporary password
- Profile updates return success confirmation
- Approval endpoints return updated approval status
- Project isolation enforced in all data queries

### Expected DB state:
- CustomUser records have proper role hierarchy
- Project associations maintained correctly
- Approval status tracked in UserDetail/AdminDetail
- Digital signatures linked to users
- Multi-tenant isolation fields populated

### Logs or indicators of success:
- Successful login logs in Django logs
- User creation logs with project association
- Password reset logs for security tracking
- Approval workflow logs for audit trail
- JWT token validation logs

## 9. Known Constraints & Design Decisions

### Why certain approaches were used:
- JWT tokens chosen for stateless authentication
- Role hierarchy designed for multi-company projects
- Approval workflows ensure data quality and security
- Project isolation prevents cross-project data access
- Auto-generated passwords ensure initial security

### Intentional limitations:
- No social media authentication (security requirement)
- No user-level menu customization (project-based only)
- No cross-project user access (isolation requirement)
- Password complexity enforced (security requirement)

### Performance or scalability considerations:
- JWT tokens reduce database queries for authentication
- Project-based filtering optimized with database indexes
- File uploads limited in size for performance
- User queries optimized with select_related for relationships

## 10. Future Reference Notes

### What must NOT be changed casually:
- User model structure (affects all modules)
- JWT token structure (breaks frontend authentication)
- Role hierarchy logic (affects access control)
- Project isolation logic (security implications)
- Database relationships (data integrity)

### Files that are high-risk:
- `models.py` - User model changes require careful migration
- `views.py` - Authentication logic affects system security
- `permissions.py` - Permission changes affect access control
- `middleware.py` - Middleware errors affect entire application
- `serializers.py` - Validation changes affect data integrity

### Areas where bugs are likely if modified:
- User creation workflow (role assignment logic)
- Project isolation queries (data leakage risk)
- Approval workflow logic (access control bypass)
- JWT token handling (authentication bypass)
- File upload validation (security vulnerabilities)

### Recommended debugging entry points:
- Start with `/authentication/login/` for authentication issues
- Check user creation logs for role assignment problems
- Verify project association in user profile data
- Examine JWT token contents for permission issues
- Use Django admin to verify database state
- Check middleware logs for request processing issues