# Enhanced PTW System - Grade-Based Workflow Implementation

## Overview
This document outlines the updated Permit to Work (PTW) system with grade-based workflow logic and specialized verification/approval processes.

## Workflow Logic

### **User Roles & Grade-Based Permissions**

#### **EPC Users**
- **Grade C**: 
  - ✅ Verify contractor permits (specialized)
  - ✅ Create own permits
  - ❌ Cannot approve (no approval authority)

- **Grade B**: 
  - ✅ Verify permits, especially EPC-created permits (specialized)
  - ✅ Create permits
  - ❌ Cannot approve (no approval authority)

- **Grade A**: 
  - ✅ **Full approval authority** (can approve all permits)
  - ✅ Create permits
  - ✅ Can also verify if needed

#### **Client Users**
- **Grade C**: 
  - ✅ Create permits
  - ✅ Limited verification (basic verification only)
  - ❌ Cannot approve

- **Grade B**: 
  - ✅ Verify permits, especially Client-created permits (specialized)
  - ✅ Create permits
  - ❌ Cannot approve

- **Grade A**: 
  - ✅ **Full approval authority** (can approve all permits)
  - ✅ Create permits
  - ✅ Can also verify if needed

#### **Contractor Users**
- **All Grades**: 
  - ✅ Create permits only
  - ❌ Cannot verify or approve

### **Workflow Process Flow**

```
1. PERMIT CREATION (Anyone)
   ↓
2. VERIFIER SELECTION (Requestor selects based on rules)
   ↓
3. VERIFICATION (EPC/Client B/C grade - specialized)
   ↓
4. APPROVER SELECTION (Verifier selects from A grade users)
   ↓
5. APPROVAL (EPC/Client A grade - full authority)
   ↓
6. PERMIT ACTIVE
```

### **Selection Rules**

#### **Verifier Selection Rules**
- **Contractor permits** → Preferably EPC Grade C (specialized for contractor permits)
- **EPC permits** → Preferably EPC Grade B (specialized for EPC permits)
- **Client permits** → Preferably Client Grade B (specialized for Client permits)
- **Client requestors** → Can only select Client verifiers
- **EPC/Contractor requestors** → Can select both EPC and Client verifiers

#### **Approver Selection Rules**
- **Only Grade A users** have full approval authority
- **Client verifiers** → Can only select Client Grade A approvers
- **EPC verifiers** → Can select both EPC and Client Grade A approvers

### **Company-Based Filtering**
- Users can filter verifiers/approvers by company name
- Enables better organization in multi-company projects
- Maintains proper oversight within company hierarchies

## Backend Structure

### Core Files
```
backend/ptw/
├── models.py                 # Enhanced PTW models with grade-based workflow
├── serializers.py           # Comprehensive serializers with relationships
├── views.py                 # Advanced viewsets with grade-aware APIs
├── workflow_manager.py      # Grade-based workflow management system
├── urls.py                  # Complete URL configuration
├── admin.py                 # Rich Django admin interface
├── permissions.py           # Grade-based permission system
├── notification_utils.py    # Notification handling
└── management/commands/
    └── create_ptw_data.py   # Data population command
```

### Key Models Enhanced
- **Permit**: 25+ fields with grade-aware workflow integration
- **PermitType**: Enhanced with grade-specific requirements
- **WorkflowTemplate/Instance/Step**: Grade-based workflow management
- **HazardLibrary**: Pre-defined hazards with grade-specific controls
- **GasReading**: Real-time monitoring with grade-based oversight
- **PermitPhoto**: Documentation with grade-based verification
- **DigitalSignature**: Multi-role signature with grade validation
- **PermitAudit**: Complete audit trail with grade-based actions

### Grade-Based Workflow Manager
```python
class PTWWorkflowManager:
    def get_available_verifiers(project, requestor_type, requestor_grade, company_filter)
    def get_available_approvers(project, verifier_type, verifier_grade, company_filter)
    def _can_select_verifier(requestor, verifier)  # Grade validation
    def _can_select_approver(verifier, approver)   # Grade validation
```

## Frontend Structure

### Core Components
```
frontend/src/features/ptw/
├── components/
│   ├── PermitForm.tsx           # Original form (kept for compatibility)
│   ├── EnhancedPermitForm.tsx   # World-class multi-step form
│   ├── PermitList.tsx           # Enhanced permit listing
│   ├── PermitDetail.tsx         # Detailed permit view
│   ├── PTWLayout.tsx            # Layout component
│   ├── ComplianceDashboard.tsx  # Analytics and KPI dashboard
│   ├── MobilePermitApp.tsx      # Progressive Web App
│   ├── WorkflowEngine.tsx       # Workflow management UI
│   ├── IntegrationHub.tsx       # System integrations UI
│   └── index.ts                 # Component exports
├── hooks/
│   └── useOfflineSync.ts        # Offline synchronization hook
├── types/
│   └── index.ts                 # TypeScript type definitions
├── utils/
│   └── ptwConstants.ts          # System constants and configurations
├── api.ts                       # API client functions
└── routes.tsx                   # Route definitions
```

## Permission System

### Updated Permission Classes

#### CanManagePermits
- **CREATE**: contractoruser (any grade), clientuser/epcuser (C grade only)
- **UPDATE**: clientuser/epcuser (B grade), permit creators
- **DELETE**: projectadmins, permit creators
- **VIEW**: All authenticated users

#### CanApprovePermits
- **Client users (A/B/C grade)**: Can approve contractor and client permits
- **EPC B grade**: Can approve EPC permits
- **VIEW**: All authenticated users

#### CanVerifyPermits
- **EPC C/B grade**: Can verify contractor and EPC permits
- **Client B grade**: Can verify client permits
- **VIEW**: All authenticated users

## Key Features Implemented

### 🎯 **Grade-Based Workflow Features**
1. **Specialized Verification**: Grade-specific verification based on permit origin
2. **Approval Authority**: Only Grade A users have full approval authority
3. **Company Filtering**: Filter verifiers/approvers by company name
4. **Role Specialization**: 
   - EPC C: Contractor permit specialists
   - EPC B: EPC permit specialists  
   - Client B: Client permit specialists
   - Grade A: Full approval authority
5. **Selection Rules**: Enforced selection rules based on user type and grade
6. **Workflow Validation**: Grade-based validation at each workflow step

### 🎯 **World-Class Features**
1. **Multi-step Wizard Form**: 6-step process with validation
2. **Risk Assessment**: Probability × Severity matrix with auto-calculation
3. **Workflow Engine**: Grade-aware configurable approval chains
4. **Digital Signatures**: Multi-role signature capture with grade tracking
5. **QR Code Integration**: Mobile scanning for permit verification
6. **Photo Documentation**: Before/during/after work photos with GPS
7. **Gas Testing**: Real-time monitoring with grade-based safety oversight
8. **Offline Support**: Complete offline functionality with sync
9. **Analytics Dashboard**: Grade-based KPIs and compliance tracking
10. **Integration Hub**: ERP, CMMS, IoT, and notification systems

### 📊 **Analytics & Reporting**
- Dashboard statistics with real-time KPIs
- Compliance scoring and trend analysis
- Risk distribution and status tracking
- PDF/Excel export capabilities
- Automated compliance reports
- Audit trail with complete change history

### 📱 **Mobile Features**
- Progressive Web App (PWA)
- Offline data storage and sync
- Camera integration for photos
- QR code scanning
- GPS location tracking
- Touch-optimized interface

### 🔗 **Integration Capabilities**
- SAP ERP integration
- IBM Maximo CMMS integration
- Gas monitoring systems (IoT)
- Active Directory (HR)
- Email/SMS notifications
- Slack/Teams integration

## Removed Files

### Backend Cleanup
- ❌ `models_enhanced.py` → renamed to `models.py`
- ❌ `serializers_enhanced.py` → renamed to `serializers.py`
- ❌ `views_enhanced.py` → renamed to `views.py`
- ❌ `urls_enhanced.py` → renamed to `urls.py`
- ❌ `admin_enhanced.py` → renamed to `admin.py`
- ❌ `reports.py` (functionality moved to views)
- ❌ `signals.py` (functionality moved to models)
- ❌ `test_notification_fix.py` (test file)
- ❌ `DOCUMENTATION.md` (replaced by this summary)

### Frontend Cleanup
- ❌ `NotificationHandler.tsx` (functionality integrated)
- ❌ `PendingApprovals.tsx` (functionality in main components)
- ❌ `PendingVerifications.tsx` (functionality in main components)
- ❌ `PermitStatusBadge.tsx` (functionality integrated)
- ❌ `PermitTimeline.tsx` (functionality integrated)
- ❌ `Reports.tsx` (functionality in ComplianceDashboard)
- ❌ `types.ts` (consolidated into types/index.ts)
- ❌ `DOCUMENTATION.md` (replaced by this summary)

## Database Schema

### Enhanced Permit Model Fields
```python
# Basic Information
permit_number, permit_type, title, description, work_order_id

# Location Information  
location, gps_coordinates, site_layout

# Time Information
planned_start_time, planned_end_time, actual_start_time, actual_end_time

# People Information
created_by, issuer, receiver, approver, area_incharge, department_head

# Contact Information
issuer_designation, issuer_department, issuer_contact
receiver_designation, receiver_department, receiver_contact

# Risk Assessment
risk_assessment_id, probability, severity, risk_score, risk_level

# Safety Information
control_measures, ppe_requirements, safety_checklist

# Isolation Requirements
requires_isolation, isolation_details, isolation_verified_by

# QR Code and Mobile
qr_code, mobile_created, offline_id

# Compliance and Audit
compliance_standards, audit_trail
```

## API Endpoints

### Core Endpoints
- `GET/POST /api/ptw/permits/` - List/Create permits (anyone can create)
- `GET/PUT/DELETE /api/ptw/permits/{id}/` - Retrieve/Update/Delete permit
- `GET /api/ptw/permits/dashboard_stats/` - Dashboard statistics
- `GET /api/ptw/permits/analytics/` - Analytics data
- `POST /api/ptw/permits/{id}/update_status/` - Status updates
- `POST /api/ptw/permits/{id}/add_photo/` - Photo upload
- `POST /api/ptw/permits/{id}/add_signature/` - Digital signature
- `GET /api/ptw/permits/export_excel/` - Excel export
- `GET /api/ptw/permits/{id}/export_pdf/` - PDF export

### Grade-Based Workflow Endpoints
- `GET /api/ptw/permits/available_verifiers/?company_filter=<name>` - Get available verifiers with grade filtering
- `GET /api/ptw/permits/available_approvers_for_verifier/?company_filter=<name>` - Get available approvers (A grade only)
- `POST /api/ptw/permits/{id}/assign_verifier/` - Assign verifier (requestor action)
- `POST /api/ptw/permits/{id}/assign_approver/` - Assign approver (verifier action)
- `POST /api/ptw/permits/{id}/verify/` - Verify permit (B/C grade action)
- `POST /api/ptw/permits/{id}/approve/` - Approve permit (A grade action)
- `POST /api/ptw/permits/{id}/reject/` - Reject permit (any verification/approval stage)

### Mobile Endpoints
- `POST /api/ptw/sync-offline-data/` - Offline data sync
- `GET /api/ptw/qr-scan/{qr_code}/` - QR code scanning

### Integration Endpoints
- `GET/POST /api/ptw/system-integrations/` - Integration management
- `POST /api/ptw/system-integrations/{id}/test_connection/` - Test connections
- `POST /api/ptw/system-integrations/{id}/sync_data/` - Data synchronization

## Installation & Setup

### Backend Setup
```bash
# Run migrations
python manage.py migrate

# Create PTW data
python manage.py create_ptw_data

# Create superuser
python manage.py createsuperuser
```

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm start
```

## Production Deployment

### Requirements
- Django 4.x+
- PostgreSQL (recommended)
- Redis (for caching)
- Celery (for background tasks)
- React 18+
- TypeScript 4.x+

### Security Features
- Role-based access control
- Digital signature verification
- Complete audit trail
- IP address tracking
- Device information logging
- Data encryption at rest

### Performance Optimizations
- Database indexing
- Query optimization
- Caching strategies
- File compression
- CDN integration ready

## Compliance Standards

### Supported Standards
- OSHA (Occupational Safety and Health Administration)
- ISO 45001 (Occupational Health and Safety)
- NFPA (National Fire Protection Association)
- API (American Petroleum Institute)
- ASME (American Society of Mechanical Engineers)
- IEC (International Electrotechnical Commission)

### Grade-Based Audit Features
- Complete change history with grade-based actions
- Digital signatures with grade validation and timestamps
- IP address and device tracking
- Grade-specific compliance reporting
- Automated workflow compliance checks
- Data retention policies with grade-based access
- Export capabilities for regulatory audits
- Grade-based authorization trails

### Workflow Compliance
- **Grade Validation**: Ensures only authorized grades can perform specific actions
- **Specialization Tracking**: Records which grade specialist handled each permit type
- **Authority Verification**: Validates approval authority at Grade A level
- **Company Segregation**: Maintains proper company-based oversight
- **Audit Trail**: Complete grade-aware audit logging for compliance

This enhanced PTW system provides a complete, production-ready solution with grade-based workflow management that meets international safety standards and regulatory compliance requirements.