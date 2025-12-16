# 🔐 EHS Authentication System - Comprehensive Documentation

## 📋 System Overview

The EHS (Environment, Health, Safety) Authentication System is a comprehensive, enterprise-grade platform providing multi-tier user management, project-based access control, real-time notifications, digital signatures, and GPS-based attendance tracking.

## 🏗️ Architecture Components

### Core Modules
- **Custom User Management** - Multi-tier user hierarchy
- **Project-Based Access Control** - Location-based permissions  
- **Real-time Notifications** - WebSocket-based messaging
- **Digital Signatures** - Professional signature templates
- **Attendance Tracking** - GPS-based check-in/out
- **Role-Based Permissions** - Granular access control
- **Company Management** - Multi-company support

## 👥 User Hierarchy & Roles

### 1. Master Admin (`admin_type: 'master'`)
**Highest Authority** - System-wide control
- ✅ Create and manage projects
- ✅ Create/delete all admin types
- ✅ System configuration and settings
- ✅ Password reset for any user
- ✅ Access to all projects and users
- ✅ Master admin creation via management command

### 2. Project Admins (`user_type: 'projectadmin'`)

#### Client Admin (`admin_type: 'client'`)
- **Role**: Client company representative
- **Scope**: Single project access
- **Capabilities**: Manage client users, view project data, approve submissions

#### EPC Admin (`admin_type: 'epc'`)  
- **Role**: Engineering, Procurement, Construction company admin
- **Scope**: Single project access
- **Capabilities**: Full project management, create/manage EPC users, safety compliance

#### Contractor Admin (`admin_type: 'contractor'`)
- **Role**: Contractor company representative  
- **Scope**: Single project access
- **Capabilities**: Manage contractor workers, submit reports, attendance tracking

### 3. Admin Users (`user_type: 'adminuser'`)
- **Role**: Field workers, supervisors, specialists
- **Created By**: Project admins
- **Grades**: 
  - **Grade A**: Site Incharge
  - **Grade B**: Team Leader/Manager  
  - **Grade C**: Worker
- **Capabilities**: Submit forms, reports, attendance tracking, safety observations

## 🔐 Authentication Features

### JWT Token-Based Authentication
```python
# Token Configuration
ACCESS_TOKEN_LIFETIME = timedelta(minutes=60)  # Configurable
REFRESH_TOKEN_LIFETIME = timedelta(days=7)     # Configurable
BLACKLIST_AFTER_ROTATION = True               # Security feature
```

### Security Features
- **Auto-generated Passwords**: 12-character secure passwords
- **Forced Password Reset**: New users must reset password
- **Account Activation**: Admin approval required
- **Token Blacklisting**: Secure logout with token invalidation
- **Session Management**: Comprehensive token handling

### Custom Authentication Backend
```python
class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Username-based authentication
        # Active user validation
        # Comprehensive security logging
```

## 📍 Project & Location Management

### Project Model Features
```python
class Project(models.Model):
    projectName = models.CharField(max_length=255)
    projectCategory = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    commencementDate = models.DateField()
    deadlineDate = models.DateField()
    # Emergency contacts, capacity, location details
```

### Project Categories
- Governments, Manufacturing, Construction, Chemical
- Port & Maritime, Power & Energy, Logistics, Schools
- Mining, Oil & Gas, Shopping Mall, Aviation

### Location-Based Features
- **Attendance Geofencing**: 300-meter radius validation
- **GPS Validation**: Haversine formula for distance calculation
- **Project Assignment**: Users tied to specific projects
- **Emergency Contacts**: Police station and hospital details

## 🔔 Real-Time Notification System

### WebSocket Architecture
```python
# WebSocket Consumer
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
```

### Notification Types
1. **Meeting Notifications**: `meeting`, `meeting_response`, `meeting_invitation`
2. **Approval Notifications**: `approval` for user details, form submissions  
3. **Chat Messages**: `chat_message`, `chat_file_shared`
4. **General Notifications**: `general` system announcements
5. **Action Items**: `action_item` task assignments

### Advanced Features
- **Read Receipts**: Message delivery and read status tracking
- **Notification Preferences**: User-configurable settings
- **Broadcast Messaging**: System-wide announcements
- **Real-time Delivery**: Instant WebSocket message delivery
- **Persistent Storage**: Database-backed notification history

## 📝 Digital Signature System

### Professional Template Generation
```python
class SignatureTemplateGenerator:
    def create_signature_template(self, user_detail):
        # Creates 400x200px signature template
        # Company logo watermark (20% opacity)
        # User name, designation, company details
        # Professional fonts and styling
```

### Template Features
- **Company Branding**: Logo integration with watermarks
- **User Information**: Name, designation, company details
- **Dynamic Elements**: Date/time stamps, project context
- **Auto-generation**: Batch template creation via management command
- **Regeneration**: Update templates when details change
- **Preview System**: Template preview before document use

### Signature Integration
- **Document Embedding**: Signature placement in PDFs/documents
- **Template Data**: JSON configuration for positioning
- **Multiple Formats**: PNG templates with transparency
- **Professional Styling**: DejaVu fonts, proper spacing

## ⏰ GPS-Based Attendance Tracking

### Attendance Model
```python
class ProjectAttendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField()
    check_in_latitude = models.FloatField()
    check_in_longitude = models.FloatField()
    check_in_photo = models.ImageField()
    working_time = models.DurationField()
```

### Features
- **Location Validation**: Must be within 300m of project coordinates
- **Photo Capture**: Check-in/out photos required for verification
- **Working Time**: Automatic duration calculation
- **Status Tracking**: Real-time attendance status
- **Project-Specific**: Attendance tied to specific projects

## 🛡️ Permission System

### Permission Classes
```python
class IsMasterAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.admin_type == 'master'

class IsProjectAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'projectadmin'
```

### Access Control Matrix
| Role | Create Projects | Manage Users | View All Data | System Config |
|------|----------------|--------------|---------------|---------------|
| Master Admin | ✅ | ✅ | ✅ | ✅ |
| Project Admin | ❌ | ✅ (Own Project) | ✅ (Own Project) | ❌ |
| Admin User | ❌ | ❌ | ✅ (Limited) | ❌ |

## 🏢 Company Management

### Multi-Company Support
```python
class CompanyDetail(models.Model):
    company_name = models.CharField(max_length=255)
    registered_office_address = models.TextField()
    company_logo = models.ImageField()
    pan = models.CharField(max_length=100)
    gst = models.CharField(max_length=100)
```

### Features
- **Company Isolation**: Data separation between companies
- **Branding Integration**: Company logos in signatures and documents
- **Contact Management**: Phone, email, address details
- **Project Capacity**: Completed and ongoing project tracking

## 📊 Management Commands

### Administrative Tools
```bash
# Create master admin (only one allowed)
python manage.py create_master_admin <username> <password> [--email <email>]

# Generate signature templates for existing users
python manage.py create_signature_templates [--dry-run] [--force] [--user-type adminuser|projectadmin|all]

# Set GPS coordinates for projects
python manage.py set_project_location --project-id 1 --latitude 28.6139 --longitude 77.2090

# Test notification system comprehensively
python manage.py test_notification_system [--run-all] [--test-user-id 1]
```

## 🔧 Database Models Summary

### Core Models
- **CustomUser**: Extended Django user with custom fields
- **Project**: Project management with GPS coordinates
- **UserDetail**: Extended user profile with signature templates
- **AdminDetail**: Admin-specific profile data
- **CompanyDetail**: Company information and branding
- **Notification**: Real-time notification system
- **ProjectAttendance**: GPS-based attendance tracking
- **NotificationPreference**: User notification settings

### Model Relationships
```
Master Admin (1) → Projects (Many)
Project (1) → Project Admins (Many)
Project Admin (1) → Admin Users (Many)
User (1) → UserDetail (1)
User (1) → CompanyDetail (1)
User (1) → Notifications (Many)
User (1) → Attendance Records (Many)
```

## 🌐 API Endpoints Summary

### Authentication Endpoints
- `POST /auth/login/` - Secure login with JWT tokens
- `POST /auth/logout/` - Secure logout with token blacklisting
- `POST /auth/token/refresh/` - Refresh access tokens

### User Management
- `GET /auth/users-overview/` - User statistics by type
- `POST /auth/projectadminuser/create/` - Create admin users
- `GET /auth/userdetail/` - Get/update user details
- `POST /auth/userdetail/approve/<id>/` - Approve user details

### Project Management  
- `POST /auth/master-admin/projects/create/` - Create projects (Master Admin)
- `POST /auth/master-admin/projects/create-admins/` - Create project admins
- `GET /auth/project/list/` - List accessible projects

### Notifications
- `GET /auth/notifications/` - Get user notifications
- `POST /auth/notifications/mark-all-read/` - Mark all as read
- `GET /auth/notifications/unread-count/` - Get unread count
- `POST /auth/notifications/broadcast/` - Broadcast notifications

### Attendance
- `POST /auth/api/attendance/check-in/` - GPS-based check-in
- `POST /auth/api/attendance/check-out/` - GPS-based check-out
- `GET /auth/api/attendance/status/<project_id>/` - Get attendance status

### Digital Signatures
- `POST /auth/signature/template/create/` - Create signature template
- `GET /auth/signature/template/preview/` - Preview template
- `POST /auth/signature/generate/` - Generate document signature

## 🎯 Key System Strengths

### 1. Scalability
- **Multi-project Support**: Unlimited projects and users
- **Hierarchical Structure**: Clear organizational hierarchy
- **Role-based Access**: Granular permission control
- **Company Isolation**: Multi-tenant architecture

### 2. Security
- **JWT Authentication**: Secure token-based auth
- **Password Policies**: Auto-generated secure passwords
- **Location Validation**: GPS-based access control
- **Audit Logging**: Comprehensive security event tracking
- **Token Blacklisting**: Secure session management

### 3. User Experience
- **Real-time Notifications**: Instant WebSocket communication
- **Professional Signatures**: Branded document signing
- **Mobile-Friendly**: GPS and photo capture support
- **Intuitive Workflows**: Clear approval processes
- **Responsive Design**: Cross-platform compatibility

### 4. Enterprise Features
- **Multi-company Support**: Corporate hierarchy management
- **Compliance Ready**: Audit trails and documentation
- **Attendance Tracking**: GPS-based workforce management
- **Document Management**: Digital signature integration
- **Notification System**: Real-time communication platform

## 📈 Implementation Status

| Feature Category | Status | Key Components |
|-----------------|--------|----------------|
| User Management | ✅ Complete | Multi-tier hierarchy, role-based access |
| Authentication | ✅ Complete | JWT tokens, secure logout, custom backend |
| Project Management | ✅ Complete | GPS coordinates, timeline tracking |
| Notifications | ✅ Complete | Real-time WebSocket, persistent storage |
| Digital Signatures | ✅ Complete | Professional templates, company branding |
| Attendance Tracking | ✅ Complete | GPS validation, photo capture |
| Permissions | ✅ Complete | Hierarchical, role-based, project isolation |
| Company Management | ✅ Complete | Multi-company, branding integration |

## 🚀 Getting Started

### 1. Initial Setup
```bash
# Create master admin
python manage.py create_master_admin masteradmin SecurePass123 --email admin@company.com

# Set project location
python manage.py set_project_location --project-id 1 --latitude 28.6139 --longitude 77.2090

# Generate signature templates
python manage.py create_signature_templates
```

### 2. User Creation Flow
1. Master Admin creates projects
2. Master Admin creates project admins (client, EPC, contractor)
3. Project admins create their admin users
4. Users complete profile details
5. Admins approve user details
6. Signature templates auto-generated

### 3. Daily Operations
- Users check-in/out with GPS validation
- Submit safety observations and reports
- Receive real-time notifications
- Sign documents with digital signatures
- Admins approve submissions and manage users

This authentication system provides a **comprehensive foundation** for enterprise EHS applications with robust security, real-time communication, and professional document management capabilities.
