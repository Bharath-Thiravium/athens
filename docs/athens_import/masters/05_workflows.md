# Masters Workflows

## A) Master Login Workflow

### Frontend Steps
1. **Login Page Load**
   - Component: `LoginPage.tsx`
   - Clear any expired tokens: `clearToken()`
   - Display login form

2. **Form Submission**
   - Validate username/password fields
   - API Call: `POST /authentication/login/`
   - Payload: `{ username: string, password: string }`

3. **Token Processing**
   - Extract response data: `{ access, refresh, username, user_type, admin_type, userId, project_id }`
   - Normalize user types: `master` → `masteradmin`
   - Store in auth store: `setToken(access, refresh, null, username, 'masteradmin', 'masteradmin', ...)`

4. **Navigation Decision**
   ```typescript
   if (isPasswordResetRequired) {
     navigate('/reset-password');
   } else if (isSuperAdmin) {
     navigate('/superadmin/dashboard');
   } else {
     navigate('/dashboard'); // Masters land here
   }
   ```

### Backend Steps
1. **Authentication Endpoint**
   - View: `SecureCompatibleLoginAPIView` or `TenantLoginAPIView`
   - Validate credentials against `CustomUser` model
   - Check user is active: `user.is_active = True`

2. **Token Generation**
   - Generate JWT access token with claims:
     ```python
     {
       'user_id': user.id,
       'username': user.username,
       'user_type': user.user_type,
       'admin_type': user.admin_type,
       'athens_tenant_id': str(user.athens_tenant_id),
       'project_id': None,  # Always null for masters
     }
     ```

3. **Response Formation**
   ```python
   return Response({
     'access': access_token,
     'refresh': refresh_token,
     'username': user.username,
     'user_type': user.user_type,
     'admin_type': user.admin_type,
     'userId': user.id,
     'project_id': None,  # Masters don't have project context
     'isPasswordResetRequired': user.is_password_reset_required,
   })
   ```

## B) First-Time Master Onboarding

### Initial Master Creation
1. **Management Command** (Most Common)
   ```bash
   python manage.py create_master_admin
   ```
   - Creates master with `user_type='master'`, `admin_type='master'`
   - Sets `can_reset_password=False`, `password_set_by_superadmin=False`

2. **Superadmin Creation** (Alternative)
   - API Call: `POST /authentication/master-admin/create/`
   - Payload: `MasterAdminSerializer` data
   - Restriction: Only one master allowed per system

### Company Details Setup
1. **Master Login** (First time)
   - Redirected to `/dashboard`
   - Company details form appears (if not completed)

2. **Company Details Submission**
   - API Call: `POST /authentication/companydetail/` (or PUT for updates)
   - Payload:
     ```json
     {
       "company_name": "string",
       "registered_office_address": "string",
       "pan": "string",
       "gst": "string",
       "company_logo": "file",
       "contact_phone": "string",
       "contact_email": "string"
     }
     ```

3. **Backend Processing**
   - View: `CompanyDetailRetrieveUpdateView`
   - Creates/updates `CompanyDetail` record
   - Links to master via `user` foreign key
   - Sets `athens_tenant_id` for tenant isolation

## C) Selecting/Switching Project Context

### Masters Don't Switch Projects
Masters operate at the **tenant level**, not project level:
- No project selector in UI
- No "current project" in auth store (`projectId: null`)
- Access all projects in their tenant simultaneously

### Project Access Pattern
1. **View All Projects**
   - Route: `/projects`
   - API Call: `GET /authentication/project/list/`
   - Returns all projects where `athens_tenant_id = user.athens_tenant_id`

2. **Project-Specific Actions**
   - Route: `/projects/view/:projectId`
   - Route: `/projects/edit/:projectId`
   - Project context comes from URL parameter, not global state

3. **Project Management**
   - Create: Modal in ProjectsList
   - Edit: Modal with project ID
   - Delete: Confirmation with dependency check

## D) Creating a Project

### Frontend Flow
1. **Initiate Creation**
   - Click "Add New Project" in ProjectsList
   - Opens modal with ProjectCreation component
   - State: `setAddingProject(true)`

2. **Form Completion**
   - Project details: name, category, capacity
   - Location selection: map + GPS coordinates
   - Emergency contacts: police station, hospital
   - Timeline: commencement date, deadline date

3. **Form Submission**
   - API Call: `POST /authentication/master-admin/projects/create/`
   - Payload:
     ```json
     {
       "name": "string",
       "category": "string",
       "capacity": "string",
       "location": "string",
       "latitude": number,
       "longitude": number,
       "policeStation": "string",
       "policeContact": "string",
       "hospital": "string",
       "hospitalContact": "string",
       "commencementDate": "YYYY-MM-DD",
       "deadlineDate": "YYYY-MM-DD"
     }
     ```

4. **Success Handling**
   - Close modal: `setAddingProject(false)`
   - Refresh project list: `fetchProjects()`
   - Navigate to new project page: `setCurrentPage(newProjectPage)`

### Backend Flow
1. **Permission Check**
   - View: `MasterAdminProjectCreateView`
   - Decorator: `@permission_classes([IsMasterAdmin])`
   - Validates user is master admin

2. **Data Validation**
   - Serializer: `ProjectSerializer`
   - Validates required fields, date ranges, coordinates

3. **Tenant Assignment**
   - Extract tenant: `getattr(request.user, "athens_tenant_id", None)`
   - Set project tenant: `project.athens_tenant_id = tenant_id`

4. **Project Creation**
   ```python
   project = serializer.save(athens_tenant_id=tenant_id)
   return Response(ProjectSerializer(project).data, status=201)
   ```

## E) Assigning Projects to Masters

### Masters Don't Get "Assigned" Projects
Masters **own** all projects in their tenant:
- Masters create projects
- Masters manage all projects in their tenant
- No assignment needed - automatic access via `athens_tenant_id`

### Creating Project Admins (Master Assigns Admins to Projects)

#### Frontend Flow
1. **Admin Creation Form**
   - Accessed from project management interface
   - Form includes client, EPC, contractor admin details

2. **Form Submission**
   - API Call: `POST /authentication/master-admin/projects/create-admins/`
   - Payload:
     ```json
     {
       "project_id": number,
       "client_username": "string",
       "client_company": "string",
       "client_residentAddress": "string",
       "epc_username": "string",
       "epc_company": "string",
       "epc_residentAddress": "string",
       "contractor_admins": [
         {
           "username": "string",
           "company_name": "string",
           "registered_address": "string"
         }
       ]
     }
     ```

#### Backend Flow
1. **Permission & Validation**
   - View: `MasterAdminCreateProjectAdminsView`
   - Permission: `@permission_classes([IsMasterAdmin])`
   - Validate project exists and belongs to master's tenant

2. **Admin Creation Loop**
   ```python
   created_admins = []
   
   # Create client admin
   if client_username:
     password = generate_secure_password()
     client_data = {
       'username': client_username,
       'password': password,
       'user_type': 'projectadmin',
       'project': project,
       'admin_type': 'client',
       'company_name': client_company,
       'athens_tenant_id': project.athens_tenant_id,
     }
     user = CustomUserSerializer(data=client_data).save()
     created_admins.append({
       'username': user.username,
       'password': password,
       'admin_type': 'client'
     })
   
   # Similar for EPC and contractor admins
   ```

3. **Response**
   ```python
   return Response({
     "created_admins": created_admins,
     "existing_admins": existing_admins
   }, status=201)
   ```

## F) Project-Scoped Operations Examples

### 1. Viewing Project Statistics
#### Frontend
- Route: `/projects/view/:projectId`
- Component: `ProjectView.tsx`
- API Calls:
  - `GET /authentication/project/list/` (filter by ID)
  - `GET /authentication/users-overview/?project_id=123`
  - `GET /authentication/admin/list/123/`

#### Backend
- Views automatically filter by tenant: `athens_tenant_id = user.athens_tenant_id`
- Project-specific data filtered by `project_id` parameter
- Masters can access any project in their tenant

### 2. Managing Project Admins
#### Frontend Flow
1. **View Project Admins**
   - API Call: `GET /authentication/admin/list/<project_id>/`
   - Display client, EPC, contractor admins

2. **Reset Admin Password**
   - API Call: `POST /authentication/master-admin/reset-admin-password/`
   - Payload: `{ project_id, admin_type, new_password, admin_index? }`

3. **Delete Admin**
   - API Call: `DELETE /authentication/master-admin/projects/admin/delete/<user_id>/`
   - Confirmation dialog with dependency check

#### Backend Flow
1. **List Admins**
   ```python
   # ProjectAdminListByProjectView
   admins = CustomUser.objects.filter(
     project_id=project_id, 
     user_type='projectadmin',
     athens_tenant_id=request.user.athens_tenant_id  # Tenant isolation
   )
   ```

2. **Password Reset**
   ```python
   # MasterAdminResetAdminPasswordView
   admin_user = CustomUser.objects.get(
     project=project,
     admin_type=admin_type,
     athens_tenant_id=request.user.athens_tenant_id
   )
   admin_user.set_password(new_password)
   admin_user.save()
   ```

### 3. Approving Admin Details
#### Frontend Flow
1. **View Pending Approvals**
   - API Call: `GET /authentication/admin/pending-details/`
   - Display list of pending admin detail submissions

2. **Review Admin Details**
   - API Call: `GET /authentication/admin/pending/<user_id>/`
   - Display admin details for review

3. **Approve/Reject**
   - API Call: `POST /authentication/admin/detail/approve/<user_id>/`
   - Send notification to admin

#### Backend Flow
1. **Get Pending Details**
   ```python
   # PendingAdminDetailsView
   pending_details = AdminDetail.objects.filter(
     is_approved=False,
     user__athens_tenant_id=request.user.athens_tenant_id  # Tenant scoped
   )
   ```

2. **Approve Details**
   ```python
   # AdminDetailApproveView
   admin_detail.is_approved = True
   admin_detail.approved_by = request.user
   admin_detail.approved_at = timezone.now()
   admin_detail.save()
   
   # Send WebSocket notification
   send_websocket_notification(
     user_id=admin_detail.user.id,
     title="Admin Details Approved",
     message="Your admin details have been approved.",
     notification_type="admin_approval"
   )
   ```

## API Call Sequences

### Master Login Sequence
```
1. POST /authentication/login/
   Request: { username, password }
   Response: { access, refresh, user_type: 'master', admin_type: 'master', project_id: null }

2. GET /authentication/admin/me/
   Headers: { Authorization: Bearer <token> }
   Response: { username, company_name, logo_url, project: null }

3. GET /authentication/project/list/
   Headers: { Authorization: Bearer <token> }
   Response: [{ id, projectName, projectCategory, location }] // All tenant projects
```

### Project Creation Sequence
```
1. POST /authentication/master-admin/projects/create/
   Headers: { Authorization: Bearer <token> }
   Request: { name, category, capacity, location, latitude, longitude, ... }
   Response: { id, projectName, projectCategory, athens_tenant_id }

2. GET /authentication/project/list/
   Headers: { Authorization: Bearer <token> }
   Response: [{ ...existing_projects, ...new_project }]
```

### Admin Creation Sequence
```
1. POST /authentication/master-admin/projects/create-admins/
   Headers: { Authorization: Bearer <token> }
   Request: { project_id, client_username, epc_username, contractor_admins }
   Response: { 
     created_admins: [{ username, password, admin_type }],
     existing_admins: [username]
   }

2. GET /authentication/admin/list/<project_id>/
   Headers: { Authorization: Bearer <token> }
   Response: { 
     clientAdmin: { username, company_name },
     epcAdmin: { username, company_name },
     contractorAdmins: [{ username, company_name }]
   }
```