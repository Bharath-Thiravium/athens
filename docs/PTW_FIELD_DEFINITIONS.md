# PTW Form Field Definitions

## A) Backend PTW Data Model Summary

### Source: app/backend/ptw/models.py :: Permit

### Core Fields

| Field | Type | DB Type | Required | Default | Validation | Notes |
|-------|------|---------|----------|---------|------------|-------|
| permit_number | string | CharField(50) | Auto | Generated | Unique | Auto-generated on create |
| permit_type | FK | ForeignKey | Yes | - | Must be active PermitType | Required for all permits |
| title | string | CharField(200) | No | "" | Max 200 chars | Optional descriptive title |
| description | text | TextField | Yes | - | Required | Work description |
| work_order_id | string | CharField(50) | No | "" | Max 50 chars | External WO reference |

### Location Fields

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| location | string | CharField(255) | Yes | - | Max 255 chars |
| gps_coordinates | string | CharField(100) | No | "" | Max 100 chars |
| site_layout | file | FileField | No | null | Upload to permit_layouts/ |

### Time Fields

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| planned_start_time | datetime | DateTimeField | Yes | - | Must be < planned_end_time |
| planned_end_time | datetime | DateTimeField | Yes | - | Must be > planned_start_time |
| actual_start_time | datetime | DateTimeField | No | null | Set when status → active |
| actual_end_time | datetime | DateTimeField | No | null | Set when status → completed |
| work_nature | enum | CharField(10) | No | "day" | Choices: day/night/both |

### People Fields

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| created_by | FK | ForeignKey(User) | Auto | request.user | Set by serializer |
| issuer | FK | ForeignKey(User) | No | null | Permit issuer |
| receiver | FK | ForeignKey(User) | No | null | Permit receiver |
| issuer_designation | string | CharField(100) | No | "" | Max 100 chars |
| issuer_department | string | CharField(100) | No | "" | Max 100 chars |
| issuer_contact | string | CharField(20) | No | "" | Max 20 chars |
| receiver_designation | string | CharField(100) | No | "" | Max 100 chars |
| receiver_department | string | CharField(100) | No | "" | Max 100 chars |
| receiver_contact | string | CharField(20) | No | "" | Max 20 chars |

### Status & Priority

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| status | enum | CharField(20) | No | "draft" | See status_enum |
| priority | enum | CharField(10) | No | "medium" | See priority_enum |
| current_approval_level | int | PositiveSmallIntegerField | No | 1 | Min 1 |

### Risk Assessment

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| risk_assessment_id | string | CharField(50) | No | "" | Max 50 chars |
| risk_assessment_completed | boolean | BooleanField | No | false | - |
| probability | int | PositiveSmallIntegerField | No | 1 | Min 1, Max 5 |
| severity | int | PositiveSmallIntegerField | No | 1 | Min 1, Max 5 |
| risk_score | int | PositiveSmallIntegerField | Auto | 1 | probability × severity |
| risk_level | enum | CharField(10) | Auto | "low" | Calculated from risk_score |

### Safety Information

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| control_measures | text | TextField | No | "" | Control measures description |
| ppe_requirements | array | JSONField | No | [] | List of PPE items |
| special_instructions | text | TextField | No | "" | Additional instructions |
| safety_checklist | object | JSONField | No | {} | Key-value checklist items |

### Isolation Requirements

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| requires_isolation | boolean | BooleanField | No | false | - |
| isolation_details | text | TextField | Conditional | "" | Required if requires_isolation=true |
| isolation_verified_by | FK | ForeignKey(User) | No | null | User who verified |
| isolation_certificate | file | FileField | No | null | Upload to isolation_certificates/ |

### Documentation

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| work_procedure | file | FileField | No | null | Upload to work_procedures/ |
| method_statement | file | FileField | No | null | Upload to method_statements/ |
| risk_assessment_doc | file | FileField | No | null | Upload to risk_assessments/ |

### System Fields

| Field | Type | DB Type | Required | Default | Validation |
|-------|------|---------|----------|---------|------------|
| project | FK | ForeignKey(Project) | Auto | user.project | Set from request.user |
| qr_code | string | CharField(500) | No | "" | Generated QR code |
| mobile_created | boolean | BooleanField | No | false | Created via mobile |
| offline_id | string | CharField(100) | No | "" | Offline sync ID |
| version | int | IntegerField | No | 1 | Optimistic locking |
| compliance_standards | array | JSONField | No | [] | Compliance refs |
| permit_parameters | object | JSONField | No | {} | Dynamic fields |
| created_at | datetime | DateTimeField | Auto | now() | Auto timestamp |
| updated_at | datetime | DateTimeField | Auto | now() | Auto timestamp |
| submitted_at | datetime | DateTimeField | No | null | Set on submit |
| approved_at | datetime | DateTimeField | No | null | Set on approve |
| approved_by | FK | ForeignKey(User) | No | null | Approver user |
| approval_comments | text | TextField | No | "" | Approval notes |
| verifier | FK | ForeignKey(User) | No | null | Verifier user |
| verified_at | datetime | DateTimeField | No | null | Verification time |
| verification_comments | text | TextField | No | "" | Verification notes |

## Related Entities

### PermitWorker
- permit (FK to Permit)
- worker (FK to User)
- role (string)
- assigned_at (datetime)

### PermitHazard
- permit (FK to Permit)
- hazard (FK to HazardLibrary)
- severity (enum)
- control_measures (text)

### PermitPhoto
- permit (FK to Permit)
- photo (file)
- caption (string)
- uploaded_at (datetime)

### PermitToolboxTalk
- permit (FK to Permit)
- conducted_by (FK to User)
- conducted_at (datetime)
- topics_covered (array)
- attendees (M2M to User)

### IsolationPointLibrary
- project (FK to Project)
- point_code (string)
- point_type (enum)
- energy_type (enum)
- location (string)

### PermitIsolationPoint
- permit (FK to Permit)
- point (FK to IsolationPointLibrary)
- status (enum: assigned/isolated/verified/deisolated)
- lock_applied (boolean)
- lock_count (int)
- verified_at (datetime)

### CloseoutChecklistTemplate
- permit_type (FK to PermitType)
- items (JSON array)
- is_active (boolean)

### PermitCloseout
- permit (OneToOne to Permit)
- template (FK to CloseoutChecklistTemplate)
- checklist (JSON object)
- completed (boolean)
- completed_at (datetime)
