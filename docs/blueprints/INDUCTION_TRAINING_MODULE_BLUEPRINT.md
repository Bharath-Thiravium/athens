# Induction Training Module - Technical Blueprint

## 1. Module Overview

### Module Name
**Induction Training Management System with Face Recognition**

### Business Purpose
Comprehensive employee and worker induction training management system with face recognition attendance verification, digital signature authorization, and ISO compliance documentation for workplace safety and regulatory requirements.

### User Roles Involved
- **EPC Safety Department**: Create and manage induction training sessions
- **Trainers**: Conduct training sessions and capture attendance
- **HR Representatives**: Authorize training programs with digital signatures
- **Safety Officers**: Approve training compliance and safety aspects
- **Quality Officers**: Ensure training meets quality standards
- **Workers/Employees**: Attend training sessions with face verification

### Dependent Modules
- **Authentication Module**: User management and project isolation
- **Worker Management**: Worker profiles and employment status
- **Face Recognition System**: Biometric attendance verification
- **Digital Signature System**: Authorization workflow
- **File Management**: Photo storage and evidence documentation

## 2. Functional Scope

### Features Included
- **Training Session Management**: Create, schedule, and manage induction sessions
- **Face Recognition Attendance**: Biometric verification with 65% confidence threshold
- **Digital Signature Workflow**: Multi-level authorization (Trainer, HR, Safety, Quality)
- **ISO Compliance Documentation**: Document ID generation and revision control
- **Employment Status Integration**: Auto-update worker status upon completion
- **Evidence Documentation**: Photo capture and storage for compliance
- **Project Isolation**: Strict data segregation by project/tenant
- **Trained Personnel Tracking**: Comprehensive tracking of all trained individuals

### Features Excluded
- **External Training Providers**: Only internal training management
- **Advanced Analytics**: Training effectiveness metrics (future phase)
- **Mobile Offline Mode**: Requires internet connectivity for face recognition
- **Bulk Import**: Manual entry only for security compliance

### Permission & Visibility Rules
- **EPC Safety Department Only**: Only EPC Safety users can create/manage training
- **Project Isolation**: Users only see training from their assigned project
- **Attendance Verification**: Face recognition required for attendance marking
- **Authorization Hierarchy**: Sequential digital signature approval process

### Role-Based Behavior
- **EPC Safety Users**: Full training management, create sessions, view all data
- **Trainers**: Conduct sessions, capture attendance, upload evidence
- **Approvers**: Add digital signatures based on role (HR, Safety, Quality)
- **Participants**: Attend sessions with biometric verification
- **Project Admins**: View project-specific training data and reports

## 3. End-to-End Process Flow

### Step-by-Step Runtime Flow

#### Phase 1: Training Session Creation
1. **User Action**: EPC Safety user accesses training creation form
2. **System Action**: Validates user permissions (EPC Safety Department only)
3. **User Action**: Fills training details (title, date, location, duration, trainer)
4. **System Action**: Auto-generates ISO document ID (TRN-IND-YYYYMMDDHHMMSS)
5. **System Action**: Creates training record with project isolation
6. **System Action**: Sets initial status to 'planned'

#### Phase 2: Digital Signature Authorization
1. **User Action**: Trainer adds digital signature to authorize training
2. **User Action**: HR Representative reviews and signs training authorization
3. **User Action**: Safety Officer approves safety compliance aspects
4. **User Action**: Quality Officer ensures training meets quality standards
5. **System Action**: Tracks signature completion status
6. **System Action**: Enables attendance capture when all signatures complete

#### Phase 3: Attendance Capture with Face Recognition
1. **User Action**: Trainer initiates attendance capture for training session
2. **System Action**: Retrieves uninducted workers and users from same project
3. **User Action**: Selects participants and captures attendance photos
4. **System Action**: Performs face recognition validation (65% threshold)
5. **System Action**: Compares attendance photo with profile photo
6. **System Action**: Marks attendance as 'present' only if face matches
7. **User Action**: Captures evidence photo of training session
8. **System Action**: Creates attendance records with match scores

#### Phase 4: Training Completion and Status Updates
1. **System Action**: Updates training status to 'completed'
2. **System Action**: Stores evidence photo for compliance documentation
3. **System Action**: Updates worker employment status to 'deployed' for present workers
4. **System Action**: Maintains audit trail of all attendance activities
5. **System Action**: Generates trained personnel tracking records

### Validation & Decision Points
- **EPC Safety Permission**: Only EPC Safety users can manage training
- **Project Assignment**: User must have project assignment
- **Face Recognition Threshold**: Minimum 65% confidence for attendance
- **Signature Completion**: All four signatures required for authorization
- **Photo Validation**: Profile photos must exist for face recognition

### Success & Failure Flows
- **Success**: Training Creation → Authorization → Attendance → Completion → Status Update
- **Face Recognition Failure**: Attendance marked as 'absent' if face doesn't match
- **Permission Failure**: Access denied with specific error messages
- **Missing Photos**: Face recognition skipped, attendance allowed with warning

## 4. Technical Architecture

### Backend Architecture

#### Views / Controllers
- **InductionTrainingViewSet**: Main training CRUD operations with EPC Safety restrictions
- **create_induction_training**: Dedicated endpoint for training creation
- **signatures**: Digital signature management endpoint
- **attendance**: Face recognition attendance capture endpoint
- **initiated_workers**: Get uninducted personnel from same project
- **trained_personnel**: Comprehensive trained personnel tracking
- **users/users_search**: User lookup for trainer assignment

#### Services
- **Face Recognition Service**: Biometric validation with confidence scoring
- **Project Isolation Service**: Ensures data segregation by project
- **Digital Signature Service**: Multi-level authorization workflow
- **Employment Status Service**: Auto-updates worker deployment status
- **ISO Document Service**: Generates compliant document IDs

#### Models
- **InductionTraining**: Core training session model with ISO compliance
- **InductionAttendance**: Attendance records with face recognition data

#### Key Model Fields
```python
# InductionTraining Model
- title, description, date, start_time, end_time
- duration, duration_unit, location, conducted_by
- status (planned/completed/cancelled)
- evidence_photo (Base64 encoded)
- document_id (ISO compliant: TRN-IND-YYYYMMDDHHMMSS)
- revision_number, project (FK)
- Digital signatures: trainer_signature, hr_signature, safety_signature, dept_head_signature
- Signature metadata: signer names, dates, user references

# InductionAttendance Model
- induction (FK), worker_id, worker_name, worker_photo
- attendance_photo (Base64), participant_type (worker/user)
- match_score (face recognition confidence)
- status (present/absent)
```

#### Serializers
- **InductionTrainingSerializer**: Full training data with signatures
- **InductionTrainingListSerializer**: Optimized list view
- **InductionAttendanceSerializer**: Attendance data with face recognition results

#### URLs
```python
# Training management
/api/induction-training/                    # Training CRUD
/api/induction-training/create/             # Training creation
/api/induction-training/{id}/signatures/    # Digital signatures
/api/induction-training/{id}/attendance/    # Attendance capture
/api/induction-training/initiated-workers/  # Uninducted personnel
/api/induction-training/trained-personnel/  # Trained personnel tracking
/api/induction-training/users/              # User lookup
/api/induction-training/users-search/       # User search
```

### Frontend Architecture

#### Pages
- **InductionTrainingList**: Training session dashboard with filtering
- **InductionTrainingCreate**: Training creation form with validation
- **InductionTrainingDetail**: Comprehensive training view with signatures
- **AttendanceCapture**: Face recognition attendance interface
- **TrainedPersonnelList**: Comprehensive trained personnel tracking

#### Components
- **TrainingForm**: Reusable training creation/editing form
- **DigitalSignaturePad**: Signature capture component
- **FaceRecognitionCamera**: Biometric attendance capture
- **AttendanceGrid**: Participant selection and photo capture
- **SignatureStatus**: Visual signature completion tracker
- **EvidencePhotoCapture**: Training evidence documentation

#### State Management
- **Training Store**: Training session data and operations
- **Attendance Store**: Attendance capture and face recognition
- **Signature Store**: Digital signature workflow state
- **Personnel Store**: Trained personnel tracking data

#### API Bindings
- **Training API**: Full training lifecycle operations
- **Attendance API**: Face recognition attendance capture
- **Signature API**: Digital signature management
- **Personnel API**: Trained personnel tracking

### APIs

#### Core Training Endpoints
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/induction-training/` | GET | Query params | Training list (EPC only) |
| `/api/induction-training/` | POST | Training data | Created training |
| `/api/induction-training/{id}/` | GET | - | Full training details |
| `/api/induction-training/{id}/signatures/` | POST | Signature data | Updated signatures |
| `/api/induction-training/{id}/attendance/` | POST | Attendance + photos | Face recognition results |
| `/api/induction-training/initiated-workers/` | GET | - | Uninducted personnel |
| `/api/induction-training/trained-personnel/` | GET | - | Trained personnel list |

#### Face Recognition Integration
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/induction-training/{id}/attendance/` | POST | Photos + participant data | Match scores + attendance |

### Database Schema

#### Core Tables
- **inductiontraining_inductiontraining**: Main training sessions
- **inductiontraining_inductionattendance**: Attendance records with face data

#### Key Relationships
- **InductionTraining → Project**: Foreign key for isolation
- **InductionTraining → User**: Multiple foreign keys for signers
- **InductionAttendance → InductionTraining**: One-to-many
- **InductionAttendance → Worker/User**: Reference by ID

## 5. File-Level Blueprint

### Critical Backend Files

#### `/backend/inductiontraining/models.py`
- **Purpose**: Core data models for induction training and attendance
- **Key Logic**: ISO document ID generation, signature validation, duration calculation
- **Inputs**: Training data, digital signatures, attendance records
- **Outputs**: Structured training and attendance data
- **Validations**: Signature completeness, duration units, status transitions
- **Risk Notes**: Digital signature integrity, Base64 photo storage

#### `/backend/inductiontraining/views.py`
- **Purpose**: API endpoints for training management and face recognition
- **Key Logic**: EPC Safety permission checking, face recognition integration, project isolation
- **Inputs**: HTTP requests with training/attendance data and photos
- **Outputs**: JSON responses with face recognition results
- **Validations**: EPC Safety permissions, project assignment, face recognition thresholds
- **Risk Notes**: Face recognition security, photo data handling, permission bypass

#### `/backend/shared/training_face_recognition.py`
- **Purpose**: Face recognition utilities for attendance verification
- **Key Logic**: Face comparison algorithms, confidence scoring, photo validation
- **Inputs**: Profile photos and attendance photos (Base64)
- **Outputs**: Match confidence scores and validation results
- **Validations**: Photo format validation, confidence thresholds
- **Risk Notes**: Biometric data security, false positive/negative rates

### Critical Frontend Files

#### `/frontend/src/pages/InductionTraining/`
- **Purpose**: Main induction training management interface
- **Key Logic**: Training CRUD, signature workflow, attendance capture
- **Inputs**: User interactions, form data, signature data
- **Outputs**: API calls, UI updates, signature status
- **Validations**: Form validation, signature requirements
- **Risk Notes**: Signature data handling, photo capture security

#### `/frontend/src/components/FaceRecognition/`
- **Purpose**: Face recognition attendance capture components
- **Key Logic**: Camera access, photo capture, attendance submission
- **Inputs**: Camera stream, participant selection
- **Outputs**: Attendance photos, face recognition requests
- **Validations**: Camera permissions, photo quality
- **Risk Notes**: Camera access security, biometric data handling

## 6. Configuration & Setup

### Environment Variables
```bash
# Face recognition settings
FACE_RECOGNITION_THRESHOLD=0.65
FACE_RECOGNITION_ENABLED=true
ATTENDANCE_PHOTO_MAX_SIZE=5MB

# Training settings
AUTO_UPDATE_EMPLOYMENT_STATUS=true
REQUIRE_ALL_SIGNATURES=true
ISO_DOCUMENT_PREFIX=TRN-IND

# EPC Safety Department settings
EPC_SAFETY_ONLY_ACCESS=true
STRICT_PROJECT_ISOLATION=true
```

### Role Mappings
- **epcuser**: Can create and manage induction training
- **trainer**: Can conduct sessions and capture attendance
- **hr_representative**: Can add HR authorization signatures
- **safety_officer**: Can add safety approval signatures
- **quality_officer**: Can add quality approval signatures

### Project Isolation
- All training data filtered by user's project assignment
- Attendance limited to workers/users from same project
- Face recognition uses project-specific photo storage
- Trained personnel tracking scoped to project

### Defaults & Assumptions
- Face recognition confidence threshold: 65%
- All four digital signatures required for authorization
- Auto-update worker employment status to 'deployed' upon completion
- ISO document ID format: TRN-IND-YYYYMMDDHHMMSS

## 7. Integration Points

### Incoming Dependencies
- **Authentication Module**: User context and EPC Safety validation
- **Worker Management**: Worker profiles and employment status
- **Face Recognition System**: Biometric comparison algorithms
- **Digital Signature System**: Signature capture and validation

### Outgoing Dependencies
- **Worker Management**: Updates employment status to 'deployed'
- **Audit System**: Logs all training and attendance activities
- **Notification System**: Training completion notifications
- **Compliance System**: ISO documentation and audit trails

### Auth / Tokens / Sessions
- JWT authentication required for all endpoints
- EPC Safety Department validation on every request
- Project assignment validated for data access
- Face recognition data encrypted in transit

## 8. Current Working State Validation

### UI Behavior
- ✅ Training creation form with EPC Safety restrictions
- ✅ Digital signature workflow interface
- ✅ Face recognition attendance capture
- ✅ Project-isolated personnel lists
- ✅ Trained personnel comprehensive tracking

### API Behavior
- ✅ EPC Safety permission enforcement
- ✅ Face recognition integration with confidence scoring
- ✅ Project isolation for all data access
- ✅ Digital signature workflow management
- ✅ Employment status auto-updates

### DB State
- ✅ ISO compliant training records
- ✅ Face recognition attendance data
- ✅ Digital signature authorization records
- ✅ Project isolation foreign keys
- ✅ Comprehensive audit trails

### Logs / Success Indicators
- Training creation logs with ISO document IDs
- Face recognition match score logging
- Employment status update confirmations
- Digital signature completion tracking
- Project isolation validation logs

## 9. Constraints & Design Decisions

### Why This Design Exists
- **EPC Safety Restriction**: Ensures only qualified safety personnel manage training
- **Face Recognition**: Prevents attendance fraud and ensures compliance
- **Digital Signatures**: Provides authorization audit trail for compliance
- **Project Isolation**: Multi-tenant security and data segregation
- **ISO Compliance**: Meets regulatory documentation requirements

### What Must Not Be Altered
- EPC Safety Department access restrictions (compliance critical)
- Face recognition confidence threshold (security critical)
- Project isolation enforcement (security critical)
- Digital signature workflow sequence (audit critical)

### Performance Implications
- Face recognition processing adds latency to attendance capture
- Base64 photo storage increases database size
- Project isolation queries require proper indexing
- Real-time attendance updates impact system load

## 10. Future Reference & Debugging Guide

### High-Risk Files
- `views.py`: EPC Safety permission logic and face recognition integration
- `models.py`: Digital signature validation and ISO compliance
- Face recognition utilities: Biometric security validation
- Attendance capture: Photo handling and match scoring

### Safe Extension Points
- Additional signature roles in authorization workflow
- Enhanced face recognition algorithms
- Training effectiveness analytics
- Bulk training session management

### Debug Entry Points
- EPC Safety permission validation
- Face recognition confidence scoring
- Project isolation query filtering
- Digital signature completion workflow

### Common Failure Areas
- EPC Safety permission validation failures
- Face recognition photo quality issues
- Project assignment validation errors
- Digital signature workflow interruptions
- Base64 photo encoding/decoding errors

---

**Blueprint Version**: 1.0  
**Last Updated**: January 2025  
**Status**: Production Ready  
**Dependencies**: Authentication, Worker Management, Face Recognition, Digital Signatures