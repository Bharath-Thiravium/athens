# Project Management Module – Technical Blueprint (Current Working State)

## 1. Module Overview

**Module Name:** Project Management System  
**Purpose & Business Objective:** Manages business projects within the Athens EHS system, providing project lifecycle management, user-project association, and project-based data isolation. Serves as the foundation for multi-company collaboration on construction and industrial projects.  
**Key Users / Roles:**
- Master Admin: Full project management across all tenants
- Project Admins: Project-specific management and user assignment
- Admin Users: Project data access and operations
- Workers: Project site attendance and activities

**Dependency on other modules:**
- Authentication module (user-project association)
- Tenant Isolation (project-tenant relationships)
- Attendance Management (project site check-in/out)
- All operational modules (project-based data filtering)

## 2. Functional Scope

**Features included:**
- Project CRUD operations (Create, Read, Update, Delete)
- Project categorization by industry type
- Emergency contact management (police, hospital)
- Project location and GPS coordinates
- Project timeline management (commencement, deadline)
- Multi-company project participation
- Project-based user assignment
- Project site attendance tracking
- Project dependency validation before deletion

**Features explicitly excluded:**
- Project billing or cost management
- Project document management (handled by other modules)
- Project scheduling/Gantt charts
- Project resource allocation beyond user assignment
- Project reporting (handled by analytics module)

**Role-based access control behavior:**
- Master Admin: Can create, view, edit, delete all projects
- Project Admin: Can view and edit assigned project details
- Admin User: Can view assigned project information
- Workers: Can view basic project info and mark attendance

**Visibility rules:**
- Users can only see their assigned project
- Master admins can see all projects across tenants
- Project deletion requires dependency validation
- Project attendance restricted to project site location

## 3. End-to-End Process Flow

### Project Creation Flow (Master Admin):
1. **Trigger:** Master admin creates new project
2. **Validation:** Verify project data completeness and uniqueness
3. **Processing:**
   - Create Project record with tenant association
   - Set project category and location details
   - Configure emergency contacts
   - Set project timeline
4. **Response:** Return created project data
5. **System Action:** Project becomes available for user assignment

### Project Assignment Flow:
1. **Trigger:** User creation or project assignment
2. **Validation:** Verify user and project existence
3. **Processing:**
   - Associate user with project via ForeignKey
   - Apply project-based data isolation
   - Update user permissions and access
4. **Response:** Confirm assignment success
5. **System Action:** User gains access to project-specific data

### Project Site Attendance Flow:
1. **Trigger:** User initiates check-in/check-out at project site
2. **Validation:** 
   - Verify user project assignment
   - Check GPS location within project boundaries
   - Validate face recognition against profile
3. **Processing:**
   - Capture attendance photo with GPS coordinates
   - Validate location proximity to project site
   - Record attendance with timestamp
4. **Response:** Confirm attendance recorded
5. **System Action:** Update attendance status and notify if required

### Project Deletion Flow (Master Admin):
1. **Trigger:** Master admin attempts project deletion
2. **Validation:** Check for project dependencies
3. **Processing:**
   - Scan all modules for project-related data
   - Count users, permits, incidents, training records
   - Generate dependency report
4. **Decision Point:** Allow deletion only if no dependencies
5. **System Action:** Delete project or return dependency error

### Project Data Isolation Flow:
1. **Trigger:** Any data access request
2. **Validation:** Check user's project association
3. **Processing:** Filter all queries by user's project_id
4. **Response:** Return only project-specific data
5. **Constraint:** Cross-project access blocked except for master admin

## 4. Technical Architecture

### Backend Components:

**Views / Controllers:**
- `ProjectCreateView` - Project creation endpoint
- `ProjectListView` - Project listing with filtering
- `ProjectDetailView` - Individual project details
- `ProjectUpdateView` - Project modification
- `ProjectDeleteView` - Project deletion with dependency checking
- `ProjectCleanupView` - Dependency management before deletion

**Services:**
- Project dependency validation service
- GPS location validation for attendance
- Face recognition integration for attendance
- Project-based data filtering service

**Models:**
- `Project` - Main project model with business details
- Project-related attendance models
- Emergency contact information
- Project timeline and location data

### Frontend Components:

**Pages:**
- `ProjectsList` - Project management interface
- `ProjectAttendance` - Site attendance marking
- Project creation and editing forms
- Project detail view with emergency contacts

**Components:**
- `ProjectCreation` - New project form
- `ProjectEdit` - Project modification form  
- `ProjectView` - Read-only project details
- GPS location capture for attendance
- Camera integration for attendance photos
- Face recognition validation

**State management:**
- Current project context
- Attendance status tracking
- Project list caching
- GPS and camera permissions

### APIs used:

**Endpoints:**
- `GET /authentication/project/list/` - List accessible projects
- `POST /authentication/project/create/` - Create new project
- `PUT /authentication/project/update/{id}/` - Update project
- `DELETE /authentication/project/delete/{id}/` - Delete project
- `POST /authentication/api/attendance/check-in/` - Mark attendance
- `GET /authentication/api/attendance/status/{project_id}/` - Get attendance status

**Request/Response structure:**
```json
// Project Creation Request
{
  "projectName": "Solar Power Plant",
  "projectCategory": "power_and_energy",
  "capacity": "100 MW",
  "location": "Gujarat, India",
  "latitude": 23.0225,
  "longitude": 72.5714,
  "nearestPoliceStation": "City Police Station",
  "nearestPoliceStationContact": "+91-1234567890",
  "nearestHospital": "City Hospital",
  "nearestHospitalContact": "+91-0987654321",
  "commencementDate": "2024-01-01",
  "deadlineDate": "2025-12-31"
}

// Attendance Check-in Request (FormData)
{
  "project_id": "1",
  "latitude": "23.0225",
  "longitude": "72.5714",
  "photo": File
}
```

### Database entities:

**Tables:**
- `authentication_project`
- `authentication_customuser` (project association)
- Attendance tracking tables

**Key fields:**
- Project: projectName, projectCategory, capacity, location, latitude, longitude
- Project: nearestPoliceStation, nearestHospital, commencementDate, deadlineDate
- Project: athens_tenant_id (tenant association)
- User: project_id (project association)

**Relationships:**
- CustomUser.project → Project (ForeignKey)
- Project.athens_tenant_id → Tenant isolation
- Attendance records → Project (via project_id)

## 5. File-Level Blueprint (CRITICAL)

### Backend Files:

**`/backend/authentication/models.py` (Project model)**
- **Responsibility:** Define Project model with business attributes
- **Key classes:** Project with category choices and location fields
- **Inputs:** Project business data and geographic information
- **Outputs:** Database schema for project management
- **Important conditions:** Category validation, coordinate validation
- **Risk notes:** Model changes affect user associations

**`/backend/authentication/views.py` (Project views)**
- **Responsibility:** Handle project CRUD operations and dependency checking
- **Key functions:** ProjectCreateView, ProjectDeleteView, dependency validation
- **Inputs:** HTTP requests with project data
- **Outputs:** JSON responses with project information
- **Important conditions:** Master admin permissions, dependency validation
- **Risk notes:** Deletion logic affects data integrity

**`/backend/authentication/views_attendance.py`**
- **Responsibility:** Handle project site attendance operations
- **Key functions:** check_in, check_out, attendance status validation
- **Inputs:** GPS coordinates, photos, project association
- **Outputs:** Attendance confirmation and status
- **Important conditions:** Location validation, face recognition
- **Risk notes:** GPS spoofing, photo validation bypass

**`/backend/authentication/serializers.py` (Project serializer)**
- **Responsibility:** API serialization for project data
- **Key functions:** ProjectSerializer with field validation
- **Inputs:** Project model instances
- **Outputs:** JSON-serialized project data
- **Important conditions:** Field compatibility, emergency contact validation
- **Risk notes:** Serialization changes affect frontend integration

### Frontend Files:

**`/frontend/src/features/project/components/ProjectsList.tsx`**
- **Responsibility:** Main project management interface
- **Key functions:** Project listing, CRUD operations, pagination
- **Inputs:** User interactions and API responses
- **Outputs:** Project management interface
- **Important conditions:** Master admin permissions, project filtering
- **Risk notes:** Permission bypass, data exposure

**`/frontend/src/features/project/components/ProjectAttendance.tsx`**
- **Responsibility:** Project site attendance marking interface
- **Key functions:** GPS capture, camera integration, face validation
- **Inputs:** GPS coordinates, camera photos, user interactions
- **Outputs:** Attendance records and status updates
- **Important conditions:** Location accuracy, camera permissions, face matching
- **Risk notes:** Location spoofing, photo manipulation, permission bypass

**`/frontend/src/features/project/components/ProjectCreation.tsx`**
- **Responsibility:** New project creation form
- **Key functions:** Form validation, emergency contact input, location setting
- **Inputs:** Project details and business information
- **Outputs:** New project creation request
- **Important conditions:** Required field validation, coordinate validation
- **Risk notes:** Invalid data submission, incomplete project setup

**`/frontend/src/features/project/components/ProjectEdit.tsx`**
- **Responsibility:** Project modification interface
- **Key functions:** Project data editing, validation, update submission
- **Inputs:** Existing project data and modifications
- **Outputs:** Project update requests
- **Important conditions:** Permission validation, data consistency
- **Risk notes:** Unauthorized modifications, data corruption

**`/frontend/src/features/project/components/ProjectView.tsx`**
- **Responsibility:** Read-only project details display
- **Key functions:** Project information display, emergency contacts
- **Inputs:** Project data from API
- **Outputs:** Formatted project information
- **Important conditions:** Data privacy, contact information security
- **Risk notes:** Information disclosure, contact data exposure

## 6. Configuration & Setup

### Environment variables used:
- `ATHENS_BACKEND_PORT` - Backend server configuration
- GPS accuracy thresholds for attendance validation
- Face recognition confidence levels
- Project site boundary radius settings

### Feature flags:
- GPS-based attendance validation
- Face recognition for attendance
- Project dependency validation
- Emergency contact requirements

### Permissions & roles mapping:
- Master Admin: Full project CRUD operations
- Project Admin: Project viewing and limited editing
- Admin User: Project information access
- Worker: Attendance marking and basic project info

### Project / tenant / company isolation logic:
- Projects belong to specific tenants (athens_tenant_id)
- Users associated with single project (project_id)
- Data filtering by user's project association
- Master admins can access all projects

### Default values & assumptions:
- Project categories predefined (construction, power, etc.)
- GPS accuracy within 300 meters for attendance
- Face recognition confidence threshold for validation
- Emergency contacts required for project creation

## 7. Integration Points

### Modules this depends on:
- Authentication module (user-project association)
- Tenant Isolation (project-tenant relationships)
- GPS services (location validation)
- Camera services (attendance photos)
- Face recognition service (attendance validation)

### Modules that depend on this:
- All operational modules (project-based filtering)
- Attendance Management (project site validation)
- User Management (project assignment)
- Reporting modules (project-based reports)
- Notification system (project-based alerts)

### External services:
- GPS/Location services (attendance validation)
- Camera hardware (attendance photos)
- Face recognition API (attendance verification)

### Auth / token / session usage:
- JWT tokens include project_id for filtering
- Project association validated on each request
- Attendance requires authenticated user with project
- Master admin tokens bypass project restrictions

## 8. Current Working State Validation

### Expected UI behavior:
- Master admin sees all projects in management interface
- Project creation form validates all required fields
- Project attendance requires GPS and camera permissions
- Face recognition validates user identity for attendance
- Project deletion shows dependency warnings

### Expected API responses:
- Project list filtered by user permissions
- Project creation returns complete project data
- Attendance endpoints validate location and identity
- Dependency check returns detailed dependency report
- Project updates reflect immediately in interface

### Expected DB state:
- Projects associated with correct tenants
- Users linked to appropriate projects
- Attendance records tied to specific projects
- Emergency contacts properly stored
- Project coordinates accurate for location validation

### Logs or indicators of success:
- Project CRUD operations logged with user details
- Attendance attempts logged with GPS and photo data
- Face recognition results logged for audit
- Dependency validation results logged
- Location validation success/failure logged

## 9. Known Constraints & Design Decisions

### Why certain approaches were used:
- Single project per user for data isolation simplicity
- GPS validation for attendance accuracy
- Face recognition for identity verification
- Dependency checking for data integrity
- Emergency contacts for safety compliance

### Intentional limitations:
- No multi-project user assignment (isolation requirement)
- No project hierarchy or sub-projects
- No project document storage (separate module)
- No project cost tracking (out of scope)
- No project scheduling features (separate system)

### Performance or scalability considerations:
- Project queries optimized with proper indexing
- Attendance photos stored with size limits
- GPS validation cached to reduce API calls
- Face recognition optimized for mobile devices
- Dependency checking optimized for large datasets

## 10. Future Reference Notes

### What must NOT be changed casually:
- Project-user association logic (affects data isolation)
- GPS validation thresholds (affects attendance accuracy)
- Face recognition confidence levels (affects security)
- Project dependency validation (affects data integrity)
- Emergency contact requirements (compliance requirement)

### Files that are high-risk:
- `models.py` - Project model changes affect associations
- `views_attendance.py` - Attendance logic affects security
- `ProjectAttendance.tsx` - GPS and camera integration
- Dependency validation logic - Data integrity critical
- Face recognition integration - Security critical

### Areas where bugs are likely if modified:
- GPS coordinate validation and accuracy checking
- Face recognition confidence thresholds
- Project dependency scanning across modules
- Camera permission handling and photo capture
- Location boundary validation for attendance

### Recommended debugging entry points:
- Check project-user associations in database
- Verify GPS coordinates and accuracy in attendance logs
- Examine face recognition confidence scores
- Test dependency validation with sample data
- Validate camera permissions and photo capture
- Check project filtering in data queries