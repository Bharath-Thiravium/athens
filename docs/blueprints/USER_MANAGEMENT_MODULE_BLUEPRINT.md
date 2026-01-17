# User Management Module – Technical Blueprint (Current Working State)

## 1. Module Overview

**Module Name:** User Management System  
**Purpose & Business Objective:** Provides comprehensive user lifecycle management including profile creation, approval workflows, document management, and user administration. Handles both admin users and regular users with role-based access control and approval processes.  
**Key Users / Roles:**
- Project Admins: Create and manage users within their project
- Admin Users: Manage their own profile and submit for approval
- Master Admin: Approve admin profiles and oversee user management
- Approvers: Review and approve user profile submissions

**Dependency on other modules:**
- Authentication module (user creation and permissions)
- Project Management (user-project association)
- Notification System (approval workflow notifications)
- Digital Signature System (signature template generation)
- File Management (document uploads and storage)

## 2. Functional Scope

**Features included:**
- User profile creation and management (UserDetail)
- Admin profile creation and management (AdminDetail)
- Document upload and validation (PAN, Aadhaar, photos)
- Digital signature template integration
- Camera integration for photo capture
- Approval workflow with notifications
- User CRUD operations by project admins
- Profile validation and form submission
- File attachment management
- Real-time photo capture via webcam

**Features explicitly excluded:**
- Bulk user import/export
- Advanced user analytics
- User role modification (handled by authentication)
- Cross-project user management
- User deactivation (uses deletion instead)

**Role-based access control behavior:**
- Project Admin: Can create, view, edit, delete users in their project
- Admin User: Can only manage their own profile
- Master Admin: Can approve admin profiles and view all users
- Users cannot access user management if not authorized

**Visibility rules:**
- Project admins see only users they created
- Admin users see only their own profile
- Approval workflows restrict editing until approved
- File uploads require proper validation and security checks

## 3. End-to-End Process Flow

### User Profile Creation Flow (Admin User):
1. **Trigger:** Admin user accesses user detail form
2. **Validation:** Check if user has existing profile
3. **Processing:**
   - Load existing profile data if available
   - Display form with required fields and validations
   - Handle file uploads and camera integration
4. **User Action:** Fill form and submit for approval
5. **System Action:** Save profile, send notification to approver
6. **Response:** Show submission confirmation

### User Approval Flow (Project Admin):
1. **Trigger:** Project admin receives approval notification
2. **Validation:** Verify admin permissions and user association
3. **Processing:**
   - Load pending user profile for review
   - Display approval interface with user data
   - Validate all required fields and documents
4. **Approver Action:** Review and approve/reject profile
5. **System Action:** Update approval status, notify user
6. **Response:** Confirm approval and update user access

### User Creation Flow (Project Admin):
1. **Trigger:** Project admin creates new user
2. **Validation:** Check project admin permissions
3. **Processing:**
   - Display user creation form
   - Validate user data and uniqueness
   - Generate temporary password
4. **System Action:** Create user account, send credentials
5. **Response:** Return user data with temporary password

### Document Upload Flow:
1. **Trigger:** User uploads document (PAN, Aadhaar, photo)
2. **Validation:** Check file type, size, and format
3. **Processing:**
   - Validate document format and content
   - Store file securely with proper naming
   - Generate thumbnails for images
4. **System Action:** Save file reference to user profile
5. **Response:** Confirm successful upload

### Camera Integration Flow:
1. **Trigger:** User clicks "Take Photo" button
2. **Validation:** Check camera permissions and availability
3. **Processing:**
   - Initialize webcam with proper constraints
   - Display camera preview in modal
   - Capture photo and convert to file
4. **User Action:** Position and capture photo
5. **System Action:** Save captured photo to form
6. **Response:** Display captured photo preview

## 4. Technical Architecture

### Backend Components:

**Views / Controllers:**
- `UserDetailRetrieveUpdateView` - User profile management
- `UserDetailApproveView` - Profile approval workflow
- `ProjectAdminUserCreateView` - User creation by admins
- `ProjectAdminUserListView` - User listing for admins
- `ProjectAdminUserUpdateView` - User editing by admins
- `ProjectAdminUserDeleteView` - User deletion by admins

**Services:**
- File upload validation and processing
- Digital signature template generation
- Notification service integration
- Profile completion validation
- Document format validation

**Models:**
- `UserDetail` - Extended user profile information
- `AdminDetail` - Admin-specific profile information
- `CustomUser` - Base user model with relationships
- File storage models for attachments

### Frontend Components:

**Pages:**
- `UserList.tsx` - User management interface for admins
- `userdetail.tsx` - User profile form and management
- User creation, editing, and viewing modals

**Components:**
- User profile form with validation
- Document upload components
- Camera integration modal
- Digital signature template component
- Approval workflow interface
- File preview and management

**State management:**
- User profile data state
- File upload state and validation
- Camera modal state
- Approval workflow state
- Form submission and loading states

### APIs used:

**Endpoints:**
- `GET /authentication/userdetail/` - Get user profile
- `PUT /authentication/userdetail/` - Update user profile
- `POST /authentication/userdetail/approve/{id}/` - Approve profile
- `GET /authentication/projectadminuser/list/` - List users
- `POST /authentication/projectadminuser/create/` - Create user
- `PUT /authentication/projectadminuser/update/{id}/` - Update user
- `DELETE /authentication/projectadminuser/delete/{id}/` - Delete user

**Request/Response structure:**
```json
// User Profile Response
{
  "id": 1,
  "user": 123,
  "employee_id": "EMP001",
  "gender": "Male",
  "father_or_spouse_name": "John Doe Sr",
  "date_of_birth": "1990-01-01",
  "nationality": "Indian",
  "education_level": "Bachelor's Degree",
  "date_of_joining": "2024-01-01",
  "mobile": "9876543210",
  "uan": "123456789012",
  "pan": "ABCDE1234F",
  "aadhaar": "123456789012",
  "mark_of_identification": "Scar on left hand",
  "photo": "/media/photos/user_123.jpg",
  "pan_attachment": "/media/pan_attachments/pan_123.pdf",
  "aadhaar_attachment": "/media/aadhaar_attachments/aadhaar_123.pdf",
  "specimen_signature": "/media/signatures/sig_123.jpg",
  "is_approved": false,
  "approved_by": null,
  "approved_at": null,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}

// User Creation Request
{
  "username": "john.doe",
  "name": "John",
  "surname": "Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "designation": "Software Engineer",
  "phone_number": "9876543210"
}
```

### Database entities:

**Tables:**
- `authentication_userdetail`
- `authentication_admindetail`
- `authentication_customuser`
- File storage tables for attachments

**Key fields:**
- UserDetail: employee_id, mobile, pan, aadhaar, photo, is_approved
- AdminDetail: phone_number, pan_number, gst_number, logo, is_approved
- File fields: pan_attachment, aadhaar_attachment, specimen_signature

**Relationships:**
- UserDetail.user → CustomUser (OneToOne)
- AdminDetail.user → CustomUser (OneToOne)
- UserDetail.approved_by → CustomUser (ForeignKey)
- CustomUser.created_by → CustomUser (Self-referencing ForeignKey)

## 5. File-Level Blueprint (CRITICAL)

### Backend Files:

**`/backend/authentication/views.py` (User management views)**
- **Responsibility:** Handle user CRUD operations and approval workflows
- **Key functions:** UserDetailRetrieveUpdateView, ProjectAdminUserCreateView, approval views
- **Inputs:** HTTP requests with user data and file uploads
- **Outputs:** JSON responses with user information and status
- **Important conditions:** Project isolation, approval workflow, file validation
- **Risk notes:** File upload security, approval logic, permission enforcement

**`/backend/authentication/models.py` (UserDetail, AdminDetail)**
- **Responsibility:** Define user profile models with extended information
- **Key classes:** UserDetail, AdminDetail with file fields and approval status
- **Inputs:** User profile data and file attachments
- **Outputs:** Database schema for user profiles
- **Important conditions:** File upload paths, approval status tracking
- **Risk notes:** File storage security, model relationships

**`/backend/authentication/serializers.py` (User serializers)**
- **Responsibility:** API serialization for user profile data
- **Key functions:** UserDetailSerializer, AdminDetailSerializer validation
- **Inputs:** User model instances and form data
- **Outputs:** Validated JSON data for API responses
- **Important conditions:** File validation, required field checking
- **Risk notes:** Data validation bypass, file upload validation

### Frontend Files:

**`/frontend/src/features/user/components/userdetail.tsx`**
- **Responsibility:** Main user profile form and management interface
- **Key functions:** Profile form, file uploads, camera integration, approval workflow
- **Inputs:** User profile data, file uploads, camera capture
- **Outputs:** Profile submission and approval interface
- **Important conditions:** Form validation, file handling, camera permissions
- **Risk notes:** File upload security, camera access, form validation bypass

**`/frontend/src/features/user/components/UserList.tsx`**
- **Responsibility:** User management interface for project admins
- **Key functions:** User listing, CRUD operations, pagination
- **Inputs:** User interactions and API responses
- **Outputs:** User management interface with actions
- **Important conditions:** Permission checking, project isolation
- **Risk notes:** Unauthorized access, data exposure

**`/frontend/src/features/user/components/UserCreation.tsx`**
- **Responsibility:** New user creation form for project admins
- **Key functions:** User creation form, validation, submission
- **Inputs:** New user data and form interactions
- **Outputs:** User creation requests to API
- **Important conditions:** Required field validation, username uniqueness
- **Risk notes:** Duplicate user creation, validation bypass

**`/frontend/src/features/user/components/UserEdit.tsx`**
- **Responsibility:** User editing interface for project admins
- **Key functions:** User data modification, validation, update submission
- **Inputs:** Existing user data and modifications
- **Outputs:** User update requests to API
- **Important conditions:** Permission validation, data consistency
- **Risk notes:** Unauthorized modifications, data corruption

**`/frontend/src/features/user/components/UserView.tsx`**
- **Responsibility:** Read-only user profile display
- **Key functions:** User information display, document viewing
- **Inputs:** User profile data from API
- **Outputs:** Formatted user information display
- **Important conditions:** Data privacy, document access control
- **Risk notes:** Information disclosure, unauthorized access

**`/frontend/src/features/user/components/DigitalSignatureTemplate.tsx`**
- **Responsibility:** Digital signature template integration
- **Key functions:** Signature template display and management
- **Inputs:** User signature data and template configuration
- **Outputs:** Signature template interface
- **Important conditions:** Template generation, signature validation
- **Risk notes:** Signature forgery, template manipulation

## 6. Configuration & Setup

### Environment variables used:
- File upload size limits and allowed types
- Camera resolution and quality settings
- Digital signature template configuration
- Document validation parameters

### Feature flags:
- Camera integration enabled/disabled
- Digital signature template generation
- Approval workflow requirements
- File upload validation strictness

### Permissions & roles mapping:
- Project Admin: Full user management within project
- Admin User: Own profile management only
- Master Admin: Admin profile approval rights
- File access permissions based on user ownership

### Project / tenant / company isolation logic:
- Users can only manage profiles within their project
- File uploads isolated by user and project
- Approval workflows respect project boundaries
- Document access restricted to authorized users

### Default values & assumptions:
- Profile photos required for all users
- PAN and Aadhaar documents mandatory
- Digital signature templates auto-generated
- Approval required for profile activation

## 7. Integration Points

### Modules this depends on:
- Authentication module (user creation and permissions)
- File storage system (document uploads)
- Camera API (photo capture)
- Notification system (approval workflows)
- Digital signature system (template generation)

### Modules that depend on this:
- All modules requiring user profile information
- Attendance system (profile photos for recognition)
- Digital signature system (user signature templates)
- Reporting modules (user information display)

### External services:
- Camera hardware (photo capture)
- File storage service (document management)
- Image processing (photo optimization)
- Document validation services

### Auth / token / session usage:
- JWT tokens for API authentication
- User context for profile access control
- Session persistence for form data
- File upload authentication and authorization

## 8. Current Working State Validation

### Expected UI behavior:
- User profile form loads with existing data
- File uploads work with proper validation
- Camera integration captures photos successfully
- Approval workflow shows pending status correctly
- Form validation prevents invalid submissions

### Expected API responses:
- Profile data loads within acceptable time
- File uploads complete successfully with validation
- Approval operations update status immediately
- User CRUD operations work with proper permissions
- Error handling provides meaningful feedback

### Expected DB state:
- User profiles stored with correct relationships
- File attachments linked properly to users
- Approval status tracked accurately
- Digital signature templates generated automatically
- Project isolation maintained correctly

### Logs or indicators of success:
- Profile submission logs with user details
- File upload logs with validation results
- Approval workflow logs with approver information
- Camera access logs for security monitoring
- Form validation logs for debugging

## 9. Known Constraints & Design Decisions

### Why certain approaches were used:
- FormData for file uploads to handle multipart data
- Camera integration for secure photo capture
- Approval workflow for data quality assurance
- Project-based isolation for security
- Digital signature integration for compliance

### Intentional limitations:
- No bulk user operations (security requirement)
- No cross-project user management (isolation requirement)
- No user role modification through this module
- No advanced document processing (separate service)

### Performance or scalability considerations:
- File upload size limits for performance
- Image compression for storage optimization
- Lazy loading of user lists for large datasets
- Efficient camera handling to prevent memory leaks
- Optimized queries for user profile loading

## 10. Future Reference Notes

### What must NOT be changed casually:
- User profile model structure (affects relationships)
- File upload validation logic (security critical)
- Approval workflow process (compliance requirement)
- Camera integration security (privacy critical)
- Project isolation logic (security requirement)

### Files that are high-risk:
- `userdetail.tsx` - Core profile management interface
- User management views in `views.py` - CRUD operations
- File upload handling - Security critical
- Camera integration - Privacy sensitive
- Approval workflow logic - Business critical

### Areas where bugs are likely if modified:
- File upload validation and processing
- Camera permission handling and capture
- Form validation and submission logic
- Approval workflow state management
- Project isolation and permission checking

### Recommended debugging entry points:
- Check user profile API responses and data structure
- Verify file upload validation and storage
- Test camera permissions and capture functionality
- Validate approval workflow notifications and status
- Examine project isolation in user queries
- Monitor form validation and error handling