# Safety Observation Module - Technical Blueprint

## Module Overview
The Safety Observation module is a comprehensive system for reporting, tracking, and managing workplace safety observations, including unsafe acts, unsafe conditions, near misses, and improvement opportunities.

## Core Architecture

### Backend Components

#### Models (`safetyobservation/models.py`)
```python
# Primary Model
class SafetyObservation(models.Model):
    # Basic Information
    observationID = CharField(max_length=50, unique=True)
    date = DateField()
    time = TimeField()
    reportedBy = CharField(max_length=100)
    department = CharField(max_length=100)
    workLocation = CharField(max_length=150)
    activityPerforming = CharField(max_length=150)
    contractorName = CharField(max_length=100, blank=True, null=True)
    
    # Observation Details
    typeOfObservation = CharField(choices=OBSERVATION_TYPE_CHOICES)
    classification = JSONField(default=list)  # Multiple selections
    safetyObservationFound = TextField(max_length=1000)
    
    # Risk Assessment
    severity = IntegerField(choices=SEVERITY_CHOICES, validators=[1-4])
    likelihood = IntegerField(choices=LIKELIHOOD_CHOICES, validators=[1-4])
    riskScore = IntegerField(editable=False)  # Auto-calculated
    
    # CAPA Information
    correctivePreventiveAction = TextField()
    correctiveActionAssignedTo = CharField(max_length=100)
    commitmentDate = DateField(null=True, blank=True)
    
    # Status Management
    observationStatus = CharField(choices=STATUS_CHOICES, default='open')
    escalation_level = IntegerField(default=1, validators=[1-5])
    
    # Environmental Fields
    is_environmental = BooleanField(default=False)
    env_incident_type = CharField(choices=ENV_INCIDENT_CHOICES)
    
    # Project Isolation
    project = ForeignKey('authentication.Project')
    
    # System Fields
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    created_by = ForeignKey(AUTH_USER_MODEL)

# File Management
class SafetyObservationFile(models.Model):
    safety_observation = ForeignKey(SafetyObservation)
    file = FileField(upload_to='safety_observation_files/')
    file_name = CharField(max_length=255)
    file_type = CharField(choices=FILE_TYPE_CHOICES)  # before/after/fixed
    uploaded_at = DateTimeField(auto_now_add=True)
    uploaded_by = ForeignKey(AUTH_USER_MODEL)
```

#### Choice Constants
```python
OBSERVATION_TYPE_CHOICES = [
    ('unsafe_act', 'Unsafe Act'),
    ('unsafe_condition', 'Unsafe Condition'),
    ('safe_act', 'Safe Act'),
    ('near_miss', 'Near Miss'),
    ('at_risk_behavior', 'At-Risk Behavior'),
    ('improvement_opportunity', 'Improvement Opportunity'),
    ('repeat_observation', 'Repeat Observation'),
    ('ppe_non_compliance', 'PPE Non-Compliance'),
    ('violation_procedure', 'Violation of Procedure/Permit'),
    ('training_need', 'Training Need to be Identified'),
    ('emergency_preparedness', 'Emergency Preparedness'),
]

CLASSIFICATION_CHOICES = [
    ('ppe_compliance', 'PPE - Personal Protective Equipment'),
    ('procedure_deviation', 'Procedure Deviation'),
    ('emergency_preparedness', 'Emergency Preparedness'),
    ('electrical', 'Electrical'),
    ('access_egress', 'Access Egress'),
    ('barricade', 'Barricade'),
    ('housekeeping', 'Housekeeping'),
    ('material_handling', 'Material Handling'),
    ('work_at_height', 'Work at Height'),
    ('environment_hygiene', 'Environment & Hygiene'),
    ('permit', 'Permit'),
    ('civil', 'Civil'),
    ('chemical_exposure', 'Chemical Exposure'),
    ('fire_safety', 'Fire Safety'),
    ('machinery_equipment', 'Machinery & Equipment'),
]

STATUS_CHOICES = [
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('pending_verification', 'Pending Verification'),
    ('closed', 'Closed'),
    ('rejected', 'Rejected'),
]
```

#### ViewSet (`safetyobservation/views.py`)
```python
class SafetyObservationViewSet(ProjectIsolationMixin, viewsets.ModelViewSet):
    serializer_class = SafetyObservationSerializer
    permission_classes = [IsAuthenticated, SafetyObservationPermission]
    lookup_field = 'observationID'
    
    # Project Isolation
    def get_queryset(self):
        # Master admin sees all data
        if user.is_superuser or user.admin_type == 'master':
            return SafetyObservation.objects.all()
        
        # Strict project isolation
        if not user.project:
            return SafetyObservation.objects.none()
        
        return SafetyObservation.objects.filter(
            project_id=user.project.id
        ).order_by('-created_at')
    
    # Custom Actions
    @action(detail=True, methods=['post'])
    def update_commitment(self, request, observationID=None)
    
    @action(detail=True, methods=['post'])
    def request_approval(self, request, observationID=None)
    
    @action(detail=True, methods=['post'])
    def upload_fixed_photos(self, request, observationID=None)
    
    @action(detail=True, methods=['post'])
    def approve_observation(self, request, observationID=None)
    
    @action(detail=False, methods=['get'])
    def project_users(self, request)
```

### Frontend Components

#### Main Components Structure
```
frontend/src/features/safetyobservation/
├── components/
│   ├── SafetyObservationForm.tsx          # Main creation form
│   ├── SafetyObservationFormEnhanced.tsx  # Enhanced form with validation
│   ├── SafetyObservationFormPage.tsx      # Form page wrapper
│   ├── SafetyObservationList.tsx          # List/table view
│   ├── SafetyObservationEdit.tsx          # Edit functionality
│   ├── SafetyObservationReview.tsx        # Review/approval interface
│   ├── ApprovalModal.tsx                  # Approval workflow modal
│   ├── CommitmentModal.tsx                # Commitment date modal
│   ├── ResponseModal.tsx                  # Response handling modal
│   ├── ReviewApprovalModal.tsx            # Review approval modal
│   └── FixedPhotoUploadModal.tsx          # Fixed photo upload
└── README.md
```

## Key Features

### 1. Observation Creation & Management
- **Unique ID Generation**: Auto-generated observationID with timestamp
- **Risk Assessment**: Automatic risk score calculation (severity × likelihood)
- **Multiple Classifications**: JSON array for multiple safety categories
- **File Attachments**: Before/after/fixed photo management
- **Project Isolation**: Strict project-based data segregation

### 2. Workflow Management
```
Open → In Progress → Pending Verification → Closed
  ↓         ↓              ↓
Rejected ←──┴──────────────┘
```

#### Status Transitions:
- **Open**: Initial state after creation
- **In Progress**: After commitment date is provided
- **Pending Verification**: After fixed photos uploaded
- **Closed**: After approval by creator
- **Rejected**: If creator rejects the completion

### 3. Assignment & Notification System
- **Assignment**: Observations assigned to specific users
- **Commitment Notifications**: When assigned user provides commitment date
- **Completion Notifications**: When fixed photos uploaded
- **Approval Notifications**: When observation approved/rejected

### 4. Auto-Escalation System
```python
def save(self, *args, **kwargs):
    # Auto-calculate risk score
    if self.severity and self.likelihood:
        self.riskScore = self.severity * self.likelihood
    
    # Auto-escalation for high-risk observations
    if self.riskScore >= 12 and not hasattr(self, '_skip_escalation'):
        old_escalation = getattr(self, 'escalation_level', 1)
        if old_escalation <= 1:
            self.escalation_level = 2
            # Restrict creator access on escalation
            restrict_creator_access_on_escalation(self)
```

### 5. Environmental Integration
- **Environmental Flag**: `is_environmental` boolean field
- **Environmental Types**: Spill, emission exceedance, bird strike, etc.
- **Dual Classification**: Safety + Environmental categorization

## API Endpoints

### Standard CRUD Operations
```
GET    /api/safetyobservation/                    # List observations
POST   /api/safetyobservation/                    # Create observation
GET    /api/safetyobservation/{observationID}/    # Retrieve observation
PUT    /api/safetyobservation/{observationID}/    # Update observation
DELETE /api/safetyobservation/{observationID}/    # Delete observation
```

### Custom Actions
```
POST /api/safetyobservation/{observationID}/update_commitment/
POST /api/safetyobservation/{observationID}/request_approval/
POST /api/safetyobservation/{observationID}/upload_fixed_photos/
POST /api/safetyobservation/{observationID}/approve_observation/
GET  /api/safetyobservation/project-users/
```

## Security & Permissions

### Project Isolation
- **Strict Filtering**: Users only see observations from their project
- **Creation Control**: Auto-assign user's project on creation
- **Master Admin Override**: Superusers see all data

### Permission System
```python
class SafetyObservationPermission(BasePermission):
    def has_permission(self, request, view):
        # Check user has project access
        # Validate induction training for assignments
        
    def has_object_permission(self, request, view, obj):
        # Check project membership
        # Validate escalation level access
```

### Role-Based Access
- **Creator**: Can create, edit (if not escalated), approve completion
- **Assigned User**: Can commit, upload fixed photos, request approval
- **Project Admin**: Full access within project
- **Master Admin**: System-wide access

## Data Validation & Business Rules

### Automatic Calculations
- **Risk Score**: `severity × likelihood`
- **Observation ID**: `SO-{timestamp}`
- **Auto-Escalation**: Risk score ≥ 12 triggers escalation

### Validation Rules
- **Project Assignment**: Required for all operations
- **Induction Training**: Required for assignment eligibility
- **File Upload Permissions**: Only assigned user can upload fixed photos
- **Approval Permissions**: Only creator can approve/reject completion

## Integration Points

### Notification System
- **Assignment Notifications**: When observation assigned
- **Commitment Notifications**: When commitment date provided
- **Completion Notifications**: When fixed photos uploaded
- **Approval Notifications**: When observation approved/rejected

### File Management
- **Upload Directory**: `safety_observation_files/`
- **File Types**: Before, After, Fixed photos
- **File Tracking**: Full audit trail with uploader and timestamp

### Environmental Module Integration
- **Shared Classifications**: Environmental incidents can be safety observations
- **Dual Reporting**: Single incident, multiple module tracking
- **Cross-Reference**: Environmental incidents link to safety observations

## Performance Considerations

### Database Optimization
- **Indexes**: observationID, project_id, created_at, observationStatus
- **Query Optimization**: Project-based filtering at database level
- **File Storage**: Separate file model for efficient querying

### Caching Strategy
- **User Project Cache**: Cache user project assignments
- **Classification Cache**: Cache choice options for forms
- **File URL Cache**: Cache file URLs for display

## Monitoring & Analytics

### Key Metrics
- **Observation Volume**: Count by type, severity, project
- **Response Times**: Time to commitment, completion, approval
- **Risk Distribution**: Risk score analysis and trends
- **Escalation Rates**: Percentage of observations escalated

### Reporting Capabilities
- **Status Reports**: Open/closed observation counts
- **Risk Analysis**: High-risk observation identification
- **Performance Metrics**: Assignment response times
- **Trend Analysis**: Observation patterns over time

## Future Enhancements

### Planned Features
- **Mobile App Integration**: Field observation capture
- **AI Risk Assessment**: Automated risk scoring
- **Predictive Analytics**: Risk pattern identification
- **Integration APIs**: Third-party safety system integration

### Scalability Considerations
- **Multi-Tenant Architecture**: Enhanced project isolation
- **Microservices Split**: Separate observation and workflow services
- **Event-Driven Architecture**: Async notification processing
- **Advanced Caching**: Redis-based caching layer