# Athens Training Logic & Workflow Specification

## Overview
This document captures the business logic, user workflows, and screen content for Athens training modules: Induction Training, Job Training, and Toolbox Talk (TBT). This specification is framework-agnostic and focuses purely on functional requirements.

---

## 1. INDUCTION TRAINING

### Purpose
Mandatory safety training for new workers and users before they can be deployed to work sites. Includes face recognition attendance verification and digital signature authorization workflow.

### Roles & Permissions

**Creator (Training Creator)**
- Can create new induction training sessions
- Can edit training when status = 'planned'
- Can delete training when status = 'planned'
- Can view check-in codes (QR/PIN)
- Can mark attendance and complete training

**Admin (Project Admin)**
- Can edit any training when status = 'planned'
- Can delete any training when status = 'planned'
- Can view all trainings in project
- Can view check-in codes
- Can mark attendance

**EPC Safety Department Users**
- Only EPC Safety Department users can access induction training module
- Can create, view, edit, delete based on creator rules above

**Participant (Worker/User)**
- Can join training using QR code or PIN
- Cannot edit or delete trainings
- Can view their own attendance status

**Others**
- No access to induction training module

**Edit/Delete Rules:**
- Edit allowed when: status = 'planned' AND (user is creator OR user is project admin)
- Delete allowed when: status = 'planned' AND (user is creator OR user is project admin)
- Complete allowed when: user is creator OR user is project admin
- View check-in codes: creator OR project admin
- Mark attendance: creator OR project admin

### Status Model & Transitions

**Statuses:**
- `planned` - Initial status, training scheduled but not conducted
- `completed` - Training conducted, attendance marked, cannot be modified
- `cancelled` - Training cancelled, no attendance allowed

**State Transitions:**
- `planned` → `completed`: When attendance is submitted successfully
- `planned` → `cancelled`: Manual cancellation by creator/admin
- `completed`: Final state, no further transitions
- `cancelled`: Final state, no further transitions

**Locked When Completed:**
- Cannot edit training details
- Cannot delete training
- Cannot modify attendance records
- Cannot change status

### Screen Workflow

#### A) Create Training

**Required Fields:**
- `title` - Training session title
- `date` - Training date
- `location` - Training venue
- `conducted_by` - Name of trainer/conductor
- `duration` - Training duration (number)
- `duration_unit` - 'minutes' or 'hours'

**Optional Fields:**
- `description` - Training description
- `start_time` - Session start time
- `end_time` - Session end time

**Default Values:**
- `status` = 'planned'
- `duration` = 60
- `duration_unit` = 'minutes'
- `date` = current date
- `conducted_by` = current user's name

**Validations:**
- Title: required, max 255 characters
- Date: required, valid date
- Location: required, max 255 characters
- Conducted by: required, max 255 characters
- Duration: required, positive integer, max 480

#### B) List Screen Behavior

**Columns Displayed:**
- Title
- Date
- Location
- Conducted By
- Status (with color tags: blue=planned, green=completed, red=cancelled)

**Actions Per Row:**
- View Details (eye icon) - always visible
- Show Check-in Codes (QR icon) - visible when status ≠ 'completed'
- Conduct & Take Attendance (team icon) - visible when status ≠ 'completed' AND status ≠ 'cancelled'
- Edit (edit icon) - visible when status = 'planned' AND user can modify
- Delete (delete icon) - visible when status = 'planned' AND user can modify

**Action Visibility Rules:**
- View: always visible
- Check-in Codes: hidden when status = 'completed'
- Conduct Attendance: hidden when status = 'completed' OR status = 'cancelled'
- Edit: visible when status = 'planned' AND (creator OR admin)
- Delete: visible when status = 'planned' AND (creator OR admin)

#### C) Detail Screen Behavior

**Sections/Tabs:**
1. **Training Sessions Tab** - List of all training sessions
2. **Trained Personnel Tab** - List of personnel who completed induction

**Training Details Section:**
- Basic info: title, description, date, location, conducted by
- Duration: duration + unit display
- Status with color coding
- Created by information
- Document ID (auto-generated: TRN-IND-YYYYMMDDHHMMSS)
- Revision number

**Digital Signatures Section:**
- Trainer signature status
- HR signature (with name and date)
- Safety Officer signature (with name and date)
- Quality Officer signature (with name and date)
- Overall completion status

**Attendance Records Section:**
- List of attendees with photos
- Attendance status (present/absent)
- Face match confidence scores
- Attendance timestamps

#### D) Attendance Flow

**Attendance Method:** Face recognition with photo capture

**Process:**
1. Creator/admin opens "Conduct & Take Attendance"
2. System loads all workers with employment_status = 'initiated' + users who haven't completed induction
3. For each participant:
   - Take photo using camera
   - Compare with registered profile photo
   - Mark as present (face match ≥ 65%) or absent (face match < 65%)
4. Take group evidence photo
5. Submit all attendance records
6. System updates training status to 'completed'
7. Workers marked present get employment_status = 'deployed'

**Who Can Start Attendance:** Creator OR project admin
**Who Can Join:** Workers with 'initiated' status + admin users in same project
**Completion Rules:** 
- Attendance becomes locked after submission
- Cannot edit attendance after completion
- Training status becomes 'completed'

### Check-in Codes Logic

**Code Generation:**
- `join_code`: 6-digit PIN generated on training creation
- `qr_token`: UUID hex string generated on training creation
- Codes generated automatically when training is created

**Code Expiration:**
- `qr_expires_at`: 7 days from creation
- No automatic regeneration
- Manual regeneration not implemented

**User Display:**
- PIN code displayed as 6-digit number
- QR code contains JSON: {training_id, qr_token, training_type: "INDUCTION"}
- Expiration timestamp shown

**Security Rules:**
- Only creator and project admin can view codes
- Codes shown in modal popup
- QR code includes training type validation

### Button Visibility Rules

| Condition | View | Check-in | Conduct | Edit | Delete |
|-----------|------|----------|---------|------|--------|
| status=planned + creator | ✓ | ✓ | ✓ | ✓ | ✓ |
| status=planned + admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| status=planned + other | ✓ | ✗ | ✗ | ✗ | ✗ |
| status=completed | ✓ | ✗ | ✗ | ✗ | ✗ |
| status=cancelled | ✓ | ✗ | ✗ | ✗ | ✗ |

### Edge Cases & Error Handling

**Marking Attendance Without Permission:**
- Error: "Access denied. Only EPC Safety Department users can access induction training."

**Invalid/Expired Codes:**
- QR shows expiration timestamp
- No automatic handling of expired codes

**Deleting Completed Training:**
- Error: Edit/delete buttons hidden for completed status

**Duplicate Attendance:**
- System prevents duplicate attendance per participant
- Updates existing record if participant already marked

**No Participants Added:**
- Error: "Mark at least one worker" when submitting empty attendance

**Face Recognition Failure:**
- Participant marked as 'absent' if face match < 65%
- Match score stored for audit

---

## 2. JOB TRAINING

### Purpose
Specialized training for workers and users who have already completed induction training. Focuses on job-specific skills and safety procedures.

### Roles & Permissions

**Creator (Training Creator)**
- Can create new job training sessions
- Can edit training when status = 'planned'
- Can delete training when status = 'planned'
- Can view check-in codes (QR/PIN)
- Can mark attendance and complete training

**Admin (Project Admin)**
- Can edit any training when status = 'planned'
- Can delete any training when status = 'planned'
- Can view all trainings in project
- Can view check-in codes
- Can mark attendance

**Participant (Worker/User)**
- Must have completed induction training to participate
- Can join training using QR code or PIN
- Cannot edit or delete trainings

**Others**
- Can view trainings (read-only)

**Edit/Delete Rules:**
- Edit allowed when: status = 'planned' AND (user is creator OR user is project admin)
- Delete allowed when: status = 'planned' AND (user is creator OR user is project admin)
- Complete allowed when: user is creator OR user is project admin
- View check-in codes: creator OR project admin
- Mark attendance: creator OR project admin

### Status Model & Transitions

**Statuses:**
- `planned` - Initial status, training scheduled but not conducted
- `completed` - Training conducted, attendance marked, cannot be modified
- `cancelled` - Training cancelled, no attendance allowed

**State Transitions:**
- `planned` → `completed`: When attendance is submitted successfully
- `planned` → `cancelled`: Manual cancellation by creator/admin
- `completed`: Final state, no further transitions
- `cancelled`: Final state, no further transitions

**Locked When Completed:**
- Cannot edit training details
- Cannot delete training
- Cannot modify attendance records
- Cannot change status

### Screen Workflow

#### A) Create Training

**Required Fields:**
- `title` - Training session title
- `date` - Training date
- `location` - Training venue
- `conducted_by` - Name of trainer/conductor

**Optional Fields:**
- `description` - Training description

**Default Values:**
- `status` = 'planned'
- `conducted_by` = current user's name

**Validations:**
- Title: required, max 255 characters
- Date: required, valid date
- Location: required, max 255 characters
- Conducted by: required, max 255 characters

#### B) List Screen Behavior

**Columns Displayed:**
- Title
- Description
- Date
- Location
- Conducted By
- Status (with color tags)
- Created By

**Actions Per Row:**
- View Details (eye icon) - always visible
- Show Check-in Codes (QR icon) - visible when status ≠ 'completed'
- Conduct & Take Attendance (team icon) - visible when status ≠ 'completed' AND status ≠ 'cancelled'
- Edit (edit icon) - visible when status = 'planned' AND user can modify
- Delete (delete icon) - visible when status = 'planned' AND user can modify

#### C) Detail Screen Behavior

**Training Details Section:**
- Basic info: title, description, date, location, conducted by
- Status with color coding
- Created by information
- Creation and update timestamps

**Attendance Records Section:**
- List of attendees with photos
- Attendance status (present/absent)
- Face match confidence scores
- Attendance timestamps
- Participant type (worker/user)

#### D) Attendance Flow

**Attendance Method:** Face recognition with photo capture

**Prerequisite:** Only induction-trained personnel can participate

**Process:**
1. Creator/admin opens "Conduct & Take Attendance"
2. System loads all workers and users who have completed induction training
3. For each participant:
   - Take photo using camera
   - Compare with registered profile photo
   - Mark as present (face match) or absent (no match)
4. Take group evidence photo
5. Submit all attendance records
6. System updates training status to 'completed'

**Who Can Start Attendance:** Creator OR project admin
**Who Can Join:** Workers and users who completed induction training in same project
**Completion Rules:**
- Attendance becomes locked after submission
- Cannot edit attendance after completion
- Training status becomes 'completed'

### Check-in Codes Logic

**Code Generation:**
- `join_code`: 6-digit PIN generated on training creation
- `qr_token`: UUID hex string generated on training creation
- Codes generated automatically when training is created

**Code Expiration:**
- `qr_expires_at`: 7 days from creation
- No automatic regeneration

**User Display:**
- PIN code displayed as 6-digit number
- QR code contains JSON: {training_id, qr_token, training_type: "JOB"}
- Expiration timestamp shown

**Security Rules:**
- Only creator and project admin can view codes
- Codes shown in modal popup

### Button Visibility Rules

| Condition | View | Check-in | Conduct | Edit | Delete |
|-----------|------|----------|---------|------|--------|
| status=planned + creator | ✓ | ✓ | ✓ | ✓ | ✓ |
| status=planned + admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| status=planned + other | ✓ | ✗ | ✗ | ✗ | ✗ |
| status=completed | ✓ | ✗ | ✗ | ✗ | ✗ |
| status=cancelled | ✓ | ✗ | ✗ | ✗ | ✗ |

### Edge Cases & Error Handling

**Non-inducted Participants:**
- Error: Only shows personnel who completed induction training
- Message: "Found X trained personnel eligible for job training"

**Marking Attendance Without Permission:**
- Error: "Access denied" for non-creators/non-admins

**Invalid/Expired Codes:**
- QR shows expiration timestamp
- No automatic handling of expired codes

**Deleting Completed Training:**
- Error: Edit/delete buttons hidden for completed status

**Duplicate Attendance:**
- System uses update_or_create to prevent duplicates
- Updates existing record if participant already marked

**No Participants Added:**
- Error: "No attendance records provided" when submitting empty attendance

---

## 3. TOOLBOX TALK (TBT)

### Purpose
Short, focused safety discussions conducted regularly on work sites. Covers specific safety topics, hazards, and procedures relevant to current work activities.

### Roles & Permissions

**Creator (Training Creator)**
- Can create new toolbox talks
- Can edit talk when status = 'planned'
- Can delete talk when status = 'planned'
- Can view check-in codes (QR/PIN)
- Can mark attendance and complete talk

**Admin (Project Admin)**
- Can edit any talk when status = 'planned'
- Can delete any talk when status = 'planned'
- Can view all talks in project
- Can view check-in codes
- Can mark attendance

**Participant (Worker/User)**
- Must have completed induction training to participate
- Can join talk using QR code or PIN
- Cannot edit or delete talks

**Others**
- Can view talks (read-only)

**Edit/Delete Rules:**
- Edit allowed when: status = 'planned' AND (user is creator OR user is project admin)
- Delete allowed when: status = 'planned' AND (user is creator OR user is project admin)
- Complete allowed when: user is creator OR user is project admin
- View check-in codes: creator OR project admin
- Mark attendance: creator OR project admin

### Status Model & Transitions

**Statuses:**
- `planned` - Initial status, talk scheduled but not conducted
- `completed` - Talk conducted, attendance marked, cannot be modified
- `cancelled` - Talk cancelled, no attendance allowed

**State Transitions:**
- `planned` → `completed`: When attendance is submitted successfully
- `planned` → `cancelled`: Manual cancellation by creator/admin
- `completed`: Final state, no further transitions
- `cancelled`: Final state, no further transitions

**Locked When Completed:**
- Cannot edit talk details
- Cannot delete talk
- Cannot modify attendance records
- Cannot change status

### Screen Workflow

#### A) Create Training

**Required Fields:**
- `title` - Toolbox talk title
- `date` - Talk date
- `location` - Talk venue
- `conducted_by` - Name of talk leader
- `duration` - Talk duration (number)
- `duration_unit` - 'minutes' or 'hours'

**Optional Fields:**
- `description` - Talk description/topics

**Default Values:**
- `status` = 'planned'
- `duration` = 30
- `duration_unit` = 'minutes'
- `conducted_by` = current user's name

**Validations:**
- Title: required, max 255 characters
- Date: required, valid date
- Location: required, max 255 characters
- Conducted by: required, max 255 characters
- Duration: required, positive integer

#### B) List Screen Behavior

**Columns Displayed:**
- Title
- Date
- Duration (with unit)
- Location
- Conducted By
- Status (with color tags)

**Actions Per Row:**
- View Details (eye icon) - always visible
- Show Check-in Codes (QR icon) - visible when status ≠ 'completed'
- Conduct & Take Attendance (team icon) - visible when status ≠ 'completed' AND status ≠ 'cancelled'
- Edit (edit icon) - visible when status = 'planned' AND user can modify
- Delete (delete icon) - visible when status = 'planned' AND user can modify

**Filtering Options:**
- By status (planned, completed, cancelled)
- By date range
- By created by user
- Search by title, location, conducted by

**Sorting Options:**
- By date (default: newest first)
- By title
- By created at
- By status

#### C) Detail Screen Behavior

**Talk Details Section:**
- Basic info: title, description, date, location, conducted by
- Duration: duration + unit display
- Status with color coding
- Created by information
- Creation and update timestamps

**Attendance Records Section:**
- List of attendees with photos
- Attendance status (present/absent)
- Face match confidence scores
- Attendance timestamps
- Evidence photo display

#### D) Attendance Flow

**Attendance Method:** Face recognition with photo capture

**Prerequisite:** Only induction-trained personnel can participate

**Process:**
1. Creator/admin opens "Conduct & Take Attendance"
2. System loads all workers and users who have completed induction training
3. System clears any existing attendance records for this talk
4. For each participant:
   - Take photo using camera
   - Compare with registered profile photo
   - Mark as present (face match) or absent (no match)
5. Take group evidence photo
6. Submit all attendance records
7. System updates talk status to 'completed'

**Who Can Start Attendance:** Creator OR project admin
**Who Can Join:** Workers and users who completed induction training in same project
**Completion Rules:**
- Attendance becomes locked after submission
- Cannot edit attendance after completion
- Talk status becomes 'completed'

**Note:** TBT has no exit attendance - participants can leave freely after joining

### Check-in Codes Logic

**Code Generation:**
- `join_code`: 6-digit PIN generated on talk creation
- `qr_token`: UUID hex string generated on talk creation
- Codes generated automatically when talk is created

**Code Expiration:**
- `qr_expires_at`: 7 days from creation
- No automatic regeneration

**User Display:**
- PIN code displayed as 6-digit number
- QR code contains JSON: {training_id, qr_token, training_type: "TBT"}
- Expiration timestamp shown

**Security Rules:**
- Only creator and project admin can view codes
- Codes shown in modal popup

### Button Visibility Rules

| Condition | View | Check-in | Conduct | Edit | Delete |
|-----------|------|----------|---------|------|--------|
| status=planned + creator | ✓ | ✓ | ✓ | ✓ | ✓ |
| status=planned + admin | ✓ | ✓ | ✓ | ✓ | ✓ |
| status=planned + other | ✓ | ✗ | ✗ | ✗ | ✗ |
| status=completed | ✓ | ✗ | ✗ | ✗ | ✗ |
| status=cancelled | ✓ | ✗ | ✗ | ✗ | ✗ |

### Edge Cases & Error Handling

**Non-inducted Participants:**
- Error: Only shows personnel who completed induction training
- Message: "Found X trained personnel eligible for toolbox talks"

**Marking Attendance Without Permission:**
- Error: "Access denied" for non-creators/non-admins

**Invalid/Expired Codes:**
- QR shows expiration timestamp
- No automatic handling of expired codes

**Deleting Completed Talk:**
- Error: Edit/delete buttons hidden for completed status

**Duplicate Attendance:**
- System clears existing attendance records before creating new ones
- Prevents duplicate attendance per participant

**No Participants Added:**
- Error: "No attendance records provided" when submitting empty attendance

---

## FINAL OUTPUT SUMMARY

### Common Patterns Across All 3 Modules

**Shared Business Logic:**
- Three-status workflow: planned → completed/cancelled
- Creator/admin permission model
- Face recognition attendance verification
- QR code + PIN check-in system
- Project-based isolation
- Evidence photo requirement

**Shared UI Patterns:**
- List view with action buttons
- Modal-based create/edit forms
- Attendance modal with camera integration
- Check-in codes modal with QR display
- Status-based button visibility

**Shared Validation Rules:**
- Required fields: title, date, location, conducted_by
- Status-based edit/delete restrictions
- Project membership requirements
- Face match confidence thresholds

### Key Differences

| Feature | Induction Training | Job Training | Toolbox Talk |
|---------|-------------------|--------------|--------------|
| **Access Control** | EPC Safety Dept only | All authenticated users | All authenticated users |
| **Participant Eligibility** | Workers with 'initiated' status + admin users | Induction-trained personnel only | Induction-trained personnel only |
| **Duration Field** | Required with unit selection | Not present | Required with unit selection |
| **Digital Signatures** | Full 4-signature workflow | Not present | Not present |
| **Post-Completion Effect** | Workers get 'deployed' status | No status change | No status change |
| **Attendance Method** | Face recognition + evidence photo | Face recognition + evidence photo | Face recognition + evidence photo |
| **Exit Attendance** | No exit tracking | No exit tracking | No exit tracking |
| **Default Duration** | 60 minutes | N/A | 30 minutes |
| **Document ID** | Auto-generated ISO format | Not present | Not present |
| **Special Features** | Trained Personnel tab | Trained Personnel endpoint | Evidence photo storage |

### Attendance Method Summary

**All modules use identical attendance flow:**
1. QR code or PIN for check-in
2. Face recognition photo capture
3. Comparison with registered profile photo
4. Present/absent marking based on face match confidence
5. Group evidence photo
6. Batch submission and status completion
7. No exit attendance tracking

**Face Recognition Rules:**
- Minimum 65% confidence for "present" status
- Below 65% marked as "absent"
- Match scores stored for audit trail
- Profile photos required for verification

This specification provides a complete framework-agnostic view of the Athens training system's business logic and user workflows.