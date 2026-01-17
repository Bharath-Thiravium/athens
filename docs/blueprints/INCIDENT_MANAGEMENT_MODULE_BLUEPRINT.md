# Incident Management Module - Technical Blueprint

## 1. Module Overview

### Module Name
**Incident Management System with 8D Problem Solving Methodology**

### Business Purpose
Comprehensive workplace incident reporting, investigation, and resolution system using the industry-standard 8D (Eight Disciplines) problem-solving methodology for systematic root cause analysis and corrective action implementation.

### User Roles Involved
- **Incident Reporters**: All project users can report incidents
- **Incident Investigators**: Assigned users who investigate incidents
- **8D Champions**: Lead the 8D problem-solving process
- **8D Team Members**: Participate in 8D disciplines
- **Safety Officers**: Oversee incident management and compliance
- **Project Admins**: Manage incident workflows and assignments

### Dependent Modules
- **Authentication Module**: User management and project isolation
- **Notification System**: Real-time alerts and workflow notifications
- **File Management**: Incident attachments and documentation
- **Permission System**: Role-based access and escalation handling

## 2. Functional Scope

### Features Included
- **Incident Reporting**: Comprehensive incident capture with attachments
- **8D Problem Solving**: Full 8-discipline methodology implementation
- **Risk Assessment**: Probability/impact matrix with auto-scoring
- **Cost Tracking**: Financial impact analysis and budget tracking
- **Regulatory Compliance**: Regulatory reporting and framework tracking
- **Lessons Learned**: Knowledge management and sharing
- **Audit Trail**: Complete activity logging and compliance tracking
- **Analytics Dashboard**: KPIs, trends, and performance metrics

### Features Excluded
- **Traditional CAPA**: Replaced by 8D methodology
- **External System Integration**: SAP/ERP integration (future phase)
- **Mobile Offline Mode**: Requires internet connectivity
- **Advanced Analytics**: AI/ML-based predictive analytics (future phase)

### Permission & Visibility Rules
- **Project Isolation**: Users only see incidents from their assigned project
- **Role-Based Access**: Different permissions for reporters vs investigators
- **Escalation Restrictions**: Creator access restricted on escalation
- **8D Team Access**: Team members can only edit assigned disciplines

### Role-Based Behavior
- **Reporters**: Create incidents, view own incidents, add attachments
- **Investigators**: Assigned incidents, manage 8D process, update status
- **Champions**: Lead 8D process, assign team members, approve actions
- **Admins**: Full access, analytics, cost approval, system configuration

## 3. End-to-End Process Flow

### Step-by-Step Runtime Flow

#### Phase 1: Incident Reporting
1. **User Action**: Reporter accesses incident creation form
2. **System Action**: Validates user permissions and project assignment
3. **User Action**: Fills incident details (type, severity, location, description)
4. **System Action**: Auto-generates incident ID (INC-YYYY-NNNN format)
5. **User Action**: Uploads attachments (photos, documents)
6. **System Action**: Stores files with security validation
7. **System Action**: Creates incident record with project isolation
8. **System Action**: Sends notifications to safety officers and supervisors

#### Phase 2: 8D Process Initiation
1. **System Action**: Auto-creates 8D process when investigator assigned
2. **System Action**: Generates 8D ID (8D-YYYY-NNNN format)
3. **System Action**: Updates incident status to "8d_initiated"
4. **User Action**: Champion assembles 8D team (D1: Establish Team)
5. **System Action**: Creates team member records with roles
6. **User Action**: Team defines problem statement (D2: Describe Problem)

#### Phase 3: Containment & Analysis
1. **User Action**: Team implements containment actions (D3)
2. **System Action**: Tracks containment effectiveness ratings
3. **User Action**: Team conducts root cause analysis (D4)
4. **System Action**: Supports multiple analysis methods (5-whys, fishbone, etc.)
5. **User Action**: Team verifies root causes with evidence
6. **System Action**: Links root causes to corrective actions

#### Phase 4: Corrective Actions
1. **User Action**: Team develops corrective actions (D5)
2. **System Action**: Tracks action types (eliminate, control, detect, prevent)
3. **User Action**: Team implements corrective actions (D6)
4. **System Action**: Monitors implementation progress and costs
5. **User Action**: Team verifies action effectiveness
6. **System Action**: Updates incident status based on progress

#### Phase 5: Prevention & Closure
1. **User Action**: Team develops prevention actions (D7)
2. **System Action**: Tracks rollout to similar processes
3. **User Action**: Team recognition and celebration (D8)
4. **System Action**: Marks 8D process as completed
5. **System Action**: Auto-closes incident when 8D complete
6. **System Action**: Generates lessons learned documentation

### Validation & Decision Points
- **Project Assignment**: User must have project assignment
- **Induction Training**: Only trained users can be investigators
- **Escalation Triggers**: Auto-escalation based on severity and time
- **Status Transitions**: Validates allowed status changes
- **8D Completion**: All disciplines must be completed before closure

### Success & Failure Flows
- **Success**: Incident → 8D Process → Corrective Actions → Prevention → Closure
- **Failure**: Validation errors return specific error messages
- **Escalation**: High/critical incidents auto-escalate after time limits
- **Rollback**: Audit trail allows tracking of all changes

## 4. Technical Architecture

### Backend Architecture

#### Views / Controllers
- **IncidentViewSet**: Main incident CRUD operations with project isolation
- **EightDProcessViewSet**: 8D process management and discipline tracking
- **EightDTeamViewSet**: Team member management and recognition
- **EightDContainmentActionViewSet**: Containment action tracking (D3)
- **EightDRootCauseViewSet**: Root cause analysis management (D4)
- **EightDCorrectiveActionViewSet**: Corrective action implementation (D5/D6)
- **EightDPreventionActionViewSet**: Prevention action management (D7)
- **IncidentCostCenterViewSet**: Financial impact tracking
- **IncidentLearningViewSet**: Lessons learned management

#### Services
- **Project Isolation Service**: Ensures data segregation by project
- **8D Workflow Manager**: Orchestrates 8D discipline progression
- **Notification Service**: Sends alerts for status changes and assignments
- **Risk Assessment Calculator**: Auto-calculates risk matrix scores
- **Cost Impact Analyzer**: Tracks financial implications
- **Audit Logger**: Records all system activities

#### Models
- **Incident**: Core incident model with comprehensive fields
- **EightDProcess**: 8D methodology process tracking
- **EightDDiscipline**: Individual discipline (D1-D8) management
- **EightDTeam**: Team member roles and responsibilities
- **EightDContainmentAction**: Interim containment measures (D3)
- **EightDRootCause**: Root cause identification and verification (D4)
- **EightDCorrectiveAction**: Permanent corrective actions (D5/D6)
- **EightDPreventionAction**: Prevention measures (D7)
- **IncidentAttachment**: File storage with security
- **IncidentAuditLog**: Complete audit trail
- **IncidentCostCenter**: Financial tracking
- **IncidentLearning**: Knowledge management

#### Serializers
- **IncidentSerializer**: Full incident data serialization
- **IncidentListSerializer**: Optimized list view serialization
- **EightDProcessSerializer**: Complete 8D process data
- **EightDProcessListSerializer**: Optimized 8D list view
- **Individual 8D Component Serializers**: Specialized serializers for each 8D element

#### URLs
```python
# Main incident management
/api/incidents/                    # Incident CRUD
/api/incidents/{id}/close/         # Close incident
/api/incidents/{id}/update-status/ # Update status
/api/incidents/dashboard-stats/    # Analytics
/api/incidents/project-users/      # User dropdown

# 8D Process management
/api/8d-processes/                 # 8D process CRUD
/api/8d-processes/{id}/start-discipline/    # Start discipline
/api/8d-processes/{id}/complete-discipline/ # Complete discipline
/api/8d-processes/overdue/         # Overdue processes
/api/8d-processes/analytics/       # 8D analytics

# 8D Components
/api/8d-teams/                     # Team management
/api/8d-containment-actions/       # Containment actions
/api/8d-root-causes/               # Root cause analysis
/api/8d-corrective-actions/        # Corrective actions
/api/8d-prevention-actions/        # Prevention actions
```

### Frontend Architecture

#### Pages
- **IncidentList**: Incident dashboard with filtering and search
- **IncidentDetail**: Comprehensive incident view with 8D integration
- **IncidentCreate**: Incident reporting form with file upload
- **EightDProcess**: 8D methodology workflow interface
- **EightDDisciplines**: Individual discipline management
- **IncidentAnalytics**: Dashboard with KPIs and trends

#### Components
- **IncidentForm**: Reusable incident creation/editing form
- **FileUpload**: Secure file attachment component
- **EightDWorkflow**: Visual 8D process progress tracker
- **RiskMatrix**: Interactive risk assessment matrix
- **CostTracker**: Financial impact visualization
- **AuditTrail**: Activity history display
- **NotificationPanel**: Real-time alert system

#### State Management
- **Incident Store**: Incident data and operations
- **EightD Store**: 8D process state management
- **User Store**: Current user and project context
- **Notification Store**: Real-time notification handling

#### API Bindings
- **Incident API**: Full incident lifecycle operations
- **8D Process API**: 8D methodology management
- **File Upload API**: Secure attachment handling
- **Analytics API**: Dashboard data and metrics

### APIs

#### Core Incident Endpoints
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/incidents/` | GET | Query params | Paginated incident list |
| `/api/incidents/` | POST | Incident data + files | Created incident |
| `/api/incidents/{id}/` | GET | - | Full incident details |
| `/api/incidents/{id}/` | PUT/PATCH | Updated data | Updated incident |
| `/api/incidents/{id}/close/` | POST | Closure notes | Closed incident |
| `/api/incidents/{id}/update-status/` | POST | Status + notes | Status update |
| `/api/incidents/dashboard-stats/` | GET | - | Analytics data |

#### 8D Process Endpoints
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/8d-processes/` | GET | Query params | 8D process list |
| `/api/8d-processes/{id}/` | GET | - | Full 8D details |
| `/api/8d-processes/{id}/start-discipline/` | POST | Discipline number | Started discipline |
| `/api/8d-processes/{id}/complete-discipline/` | POST | Discipline data | Completed discipline |
| `/api/8d-teams/` | POST | Team member data | Added team member |
| `/api/8d-containment-actions/` | POST | Action data | Created action |

### Database Schema

#### Core Tables
- **incidentmanagement_incident**: Main incident records
- **incidentmanagement_eightdprocess**: 8D process tracking
- **incidentmanagement_eightddiscipline**: Individual disciplines (D1-D8)
- **incidentmanagement_eightdteam**: Team member assignments
- **incidentmanagement_eightdcontainmentaction**: Containment measures
- **incidentmanagement_eightdrootcause**: Root cause analysis
- **incidentmanagement_eightdcorrectiveaction**: Corrective actions
- **incidentmanagement_eightdpreventionaction**: Prevention measures
- **incidentmanagement_incidentattachment**: File attachments
- **incidentmanagement_incidentauditlog**: Audit trail
- **incidentmanagement_incidentcostcenter**: Cost tracking
- **incidentmanagement_incidentlearning**: Lessons learned

#### Key Relationships
- **Incident → EightDProcess**: One-to-one relationship
- **EightDProcess → Disciplines**: One-to-many (8 disciplines)
- **EightDProcess → Team**: Many-to-many through EightDTeam
- **EightDRootCause → CorrectiveActions**: One-to-many
- **Incident → Attachments**: One-to-many
- **All models → Project**: Foreign key for isolation

## 5. File-Level Blueprint

### Critical Backend Files

#### `/backend/incidentmanagement/models.py`
- **Purpose**: Core data models for incident management and 8D methodology
- **Key Logic**: Auto-ID generation, risk calculation, 8D workflow automation
- **Inputs**: User data, file uploads, workflow transitions
- **Outputs**: Structured incident and 8D data
- **Validations**: Status transitions, risk matrix validation, file type checking
- **Risk Notes**: Complex model relationships, auto-escalation logic

#### `/backend/incidentmanagement/views.py`
- **Purpose**: API endpoints for incident and 8D process management
- **Key Logic**: Project isolation, permission checking, workflow orchestration
- **Inputs**: HTTP requests with incident/8D data
- **Outputs**: JSON responses with processed data
- **Validations**: User permissions, project assignment, data integrity
- **Risk Notes**: File upload security, project isolation enforcement

#### `/backend/incidentmanagement/serializers.py`
- **Purpose**: Data serialization and validation for API responses
- **Key Logic**: Nested serialization for complex 8D relationships
- **Inputs**: Model instances and request data
- **Outputs**: Validated JSON data structures
- **Validations**: Field validation, business rule enforcement
- **Risk Notes**: Sensitive data exposure, validation bypass

#### `/backend/incidentmanagement/permissions.py`
- **Purpose**: Custom permission classes for incident management
- **Key Logic**: Role-based access control, escalation restrictions
- **Inputs**: User context and requested operations
- **Outputs**: Permission granted/denied decisions
- **Validations**: User roles, project assignment, escalation levels
- **Risk Notes**: Permission bypass, unauthorized access

### Critical Frontend Files

#### `/frontend/src/pages/IncidentManagement/`
- **Purpose**: Main incident management interface
- **Key Logic**: Incident CRUD operations, 8D workflow integration
- **Inputs**: User interactions, form data, file uploads
- **Outputs**: API calls, UI updates, notifications
- **Validations**: Form validation, file type checking
- **Risk Notes**: File upload security, data validation

#### `/frontend/src/components/EightD/`
- **Purpose**: 8D methodology workflow components
- **Key Logic**: Discipline progression, team management, action tracking
- **Inputs**: 8D process data, user actions
- **Outputs**: Workflow updates, progress tracking
- **Validations**: Discipline completion requirements
- **Risk Notes**: Workflow bypass, incomplete processes

## 6. Configuration & Setup

### Environment Variables
```bash
# File upload settings
MAX_INCIDENT_ATTACHMENT_SIZE=10MB
ALLOWED_INCIDENT_FILE_TYPES=jpg,jpeg,png,pdf,doc,docx

# 8D Process settings
AUTO_CREATE_8D_PROCESS=true
8D_AUTO_ESCALATION_DAYS=3
8D_COMPLETION_REQUIRED_FOR_CLOSURE=true

# Risk assessment settings
RISK_MATRIX_SCORING=enabled
AUTO_ESCALATION_HIGH_RISK=true
ESCALATION_NOTIFICATION_HOURS=24
```

### Role Mappings
- **incident_reporter**: Can create and view own incidents
- **incident_investigator**: Can investigate assigned incidents
- **8d_champion**: Can lead 8D processes
- **8d_team_member**: Can participate in 8D disciplines
- **safety_officer**: Can view all incidents and analytics
- **cost_approver**: Can approve incident costs

### Project Isolation
- All incident data filtered by user's project assignment
- 8D team members must be from same project
- File attachments inherit project isolation
- Analytics scoped to user's project

### Defaults & Assumptions
- Auto-assign reporter as initial investigator
- Auto-create 8D process when investigator assigned
- Default risk matrix scoring (probability × impact)
- Auto-escalation for high/critical incidents after 24 hours

## 7. Integration Points

### Incoming Dependencies
- **Authentication Module**: User context and project assignment
- **Permission System**: Role-based access control and escalation
- **Notification System**: Real-time alerts and workflow notifications
- **File Management**: Secure file storage and retrieval

### Outgoing Dependencies
- **Notification System**: Sends incident and 8D process notifications
- **Audit System**: Logs all incident management activities
- **Analytics System**: Provides incident metrics and KPIs
- **Reporting System**: Generates incident and 8D reports

### Auth / Tokens / Sessions
- JWT authentication required for all endpoints
- Project assignment validated on every request
- Session-based file upload security
- Role-based permission checking

## 8. Current Working State Validation

### UI Behavior
- ✅ Incident creation form with file upload
- ✅ 8D process workflow interface
- ✅ Real-time status updates
- ✅ Project-isolated incident lists
- ✅ Analytics dashboard with KPIs

### API Behavior
- ✅ RESTful incident CRUD operations
- ✅ 8D process management endpoints
- ✅ File upload with security validation
- ✅ Project isolation enforcement
- ✅ Audit trail logging

### DB State
- ✅ Comprehensive incident data model
- ✅ Full 8D methodology implementation
- ✅ Project isolation foreign keys
- ✅ Audit trail tables
- ✅ Cost tracking and learning models

### Logs / Success Indicators
- Incident creation logs with auto-ID generation
- 8D process initiation and completion logs
- File upload success/failure tracking
- Project isolation validation logs
- Performance metrics for 8D completion times

## 9. Constraints & Design Decisions

### Why This Design Exists
- **8D Methodology**: Industry-standard problem-solving approach
- **Project Isolation**: Multi-tenant security requirement
- **Auto-Escalation**: Ensures timely incident resolution
- **Comprehensive Tracking**: Regulatory compliance and audit requirements

### What Must Not Be Altered
- Project isolation enforcement (security critical)
- 8D discipline sequence and requirements
- Audit trail integrity and completeness
- File upload security validations

### Performance Implications
- Complex 8D relationships require optimized queries
- File uploads need size and type restrictions
- Analytics queries should use database indexes
- Real-time notifications impact system load

## 10. Future Reference & Debugging Guide

### High-Risk Files
- `models.py`: Complex relationships and auto-calculations
- `views.py`: Project isolation and permission logic
- `permissions.py`: Security-critical access control
- File upload handlers: Security validation points

### Safe Extension Points
- Additional 8D analysis methods
- Custom incident categories
- Enhanced cost tracking
- Extended analytics and reporting

### Debug Entry Points
- Incident creation workflow validation
- 8D process auto-creation logic
- Project isolation query filtering
- File upload security checks

### Common Failure Areas
- Project assignment validation failures
- 8D process auto-creation errors
- File upload size/type violations
- Permission escalation edge cases
- Complex 8D relationship queries

---

**Blueprint Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production Ready  
**Dependencies**: Authentication, Notifications, Permissions, File Management