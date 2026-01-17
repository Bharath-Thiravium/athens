# Database Table Structure Documentation

**Date:** January 25, 2025
**System:** UpatePro - Inspection & Incident Management System
**Status:** Production Ready

## Overview
This document outlines the database schema for the UpatePro system, covering the Inspection Management System, Incident Management Module, and the fully integrated 8D Problem Solving Methodology.

---

## 1. Core System Tables

### `users`
Stores user account information, authentication details, and role-based access control data.
- **id** (PK): Unique identifier (UUID/Integer)
- **username**: User's login name
- **email**: Contact email address
- **password_hash**: Bcrypt encrypted password
- **role**: System role (Admin, Project Manager, Safety Officer, Inspector)
- **department**: User's department
- **is_active**: Boolean status
- **created_at**: Timestamp

### `projects`
Stores project details where inspections and incidents are tracked.
- **id** (PK): Unique identifier
- **name**: Project name
- **code**: Project code/number
- **location**: Physical location/site address
- **manager_id** (FK): Reference to `users` table
- **start_date**: Project start date
- **status**: (Active, Completed, On Hold)

---

## 2. Inspection Management Module

### `inspections`
The core table for safety, quality, and environmental inspections.
- **id** (PK): Unique identifier
- **project_id** (FK): Reference to `projects`
- **inspector_id** (FK): Reference to `users`
- **type**: Inspection category (Safety, Quality, Environmental, Equipment, Housekeeping, Fire Safety, Electrical, Structural)
- **status**: Workflow state (Draft, Scheduled, In Progress, Completed, Cancelled)
- **priority**: (Low, Medium, High, Critical)
- **scheduled_date**: Date and time for the inspection
- **completed_date**: Actual completion timestamp
- **location_details**: Specific area within the project

### `inspection_items`
Individual checklist items verified during an inspection.
- **id** (PK): Unique identifier
- **inspection_id** (FK): Reference to `inspections`
- **category**: Item category (e.g., PPE, Machinery, Signage)
- **description**: The checklist question or item
- **status**: Compliance status (Pass, Fail, N/A)
- **comments**: Inspector's observations
- **photo_url**: Path to uploaded evidence photo
- **severity**: Severity if failed (Low, Medium, High)

### `inspection_reports`
Generated summaries and scoring for completed inspections.
- **id** (PK): Unique identifier
- **inspection_id** (FK): Reference to `inspections`
- **overall_score**: Calculated compliance percentage
- **summary_text**: Automated or manual summary
- **recommendations**: Key recommendations based on failures
- **generated_by** (FK): Reference to `users`
- **generated_at**: Timestamp

---

## 3. Incident Management & 8D Methodology

### `incidents`
Primary record for safety or quality incidents.
- **id** (PK): Unique identifier
- **project_id** (FK): Reference to `projects`
- **reported_by** (FK): Reference to `users`
- **title**: Brief incident title
- **description**: Detailed incident description
- **type**: (Injury, Near Miss, Property Damage, Environmental, Quality)
- **severity**: (Minor, Major, Critical, Catastrophic)
- **status**: (Open, Investigating, CAPA In Progress, Closed)
- **occurrence_date**: Date and time of incident
- **location**: Specific location of occurrence

### `investigations`
Detailed investigation records linked to incidents.
- **id** (PK): Unique identifier
- **incident_id** (FK): Reference to `incidents`
- **lead_investigator_id** (FK): Reference to `users`
- **methodology**: Investigation method used
- **findings**: Detailed investigation findings
- **evidence_files**: JSON array of file paths
- **started_at**: Timestamp
- **completed_at**: Timestamp
- **status**: (Draft, In Review, Approved)

### `capas` (Corrective & Preventive Actions)
General action tracking for incidents (outside of full 8D).
- **id** (PK): Unique identifier
- **investigation_id** (FK): Reference to `investigations`
- **description**: Action description
- **type**: (Corrective, Preventive)
- **assigned_to** (FK): Reference to `users`
- **due_date**: Target completion date
- **status**: (Pending, In Progress, Verified, Closed)
- **completion_date**: Actual completion date

### `eight_d_processes`
Master table for the 8D Problem Solving lifecycle.
- **id** (PK): Unique identifier
- **incident_id** (FK): Reference to `incidents`
- **champion_id** (FK): Executive sponsor/Champion
- **problem_statement**: Refined problem description (D2)
- **target_date**: Target completion date for the 8D
- **current_stage**: (D1, D2, D3, D4, D5, D6, D7, D8)
- **status**: (Open, In Progress, Completed)
- **created_at**: Timestamp
- **updated_at**: Timestamp

### `eight_d_teams` (D1)
Team members assigned to specific 8D processes.
- **id** (PK): Unique identifier
- **process_id** (FK): Reference to `eight_d_processes`
- **user_id** (FK): Reference to `users`
- **role**: (Champion, Team Leader, SME, Member, Scribe)
- **expertise_area**: Specific domain knowledge contributed
- **responsibilities**: Defined duties for this 8D

### `eight_d_containment_actions` (D3)
Interim containment actions to protect the customer/process.
- **id** (PK): Unique identifier
- **process_id** (FK): Reference to `eight_d_processes`
- **description**: Action details
- **rationale**: Why this action was chosen
- **responsible_person_id** (FK): Reference to `users`
- **status**: (Planned, Implemented, Verified)
- **effectiveness_rating**: (0-100%)
- **verification_method**: How effectiveness was verified
- **date_implemented**: Date

### `eight_d_root_causes` (D4)
Root cause analysis data.
- **id** (PK): Unique identifier
- **process_id** (FK): Reference to `eight_d_processes`
- **description**: Root cause description
- **cause_type**: (Immediate, Contributing, Root, Systemic)
- **analysis_method**: (5-Why, Fishbone, Fault Tree)
- **likelihood**: (Low, Medium, High)
- **evidence**: Supporting data/observations
- **is_verified**: Boolean

### `eight_d_corrective_actions` (D5)
Permanent corrective actions (PCA) selection.
- **id** (PK): Unique identifier
- **process_id** (FK): Reference to `eight_d_processes`
- **root_cause_id** (FK): Reference to `eight_d_root_causes`
- **description**: Action description
- **rationale**: Why this will fix the root cause
- **estimated_cost**: Monetary value
- **success_criteria**: Metrics for validation
- **status**: (Proposed, Approved, Rejected)

### `eight_d_implementations` (D6)
Tracking the implementation of PCAs.
- **id** (PK): Unique identifier
- **corrective_action_id** (FK): Reference to `eight_d_corrective_actions`
- **assigned_to** (FK): Reference to `users`
- **start_date**: Planned start
- **target_date**: Planned finish
- **completion_percentage**: (0-100)
- **status**: (Not Started, In Progress, Completed, Validated)
- **validation_evidence**: Notes or file links

### `eight_d_preventions` (D7)
Systemic actions to prevent recurrence.
- **id** (PK): Unique identifier
- **process_id** (FK): Reference to `eight_d_processes`
- **action_type**: (Policy Update, Process Change, Training, Audit Update)
- **description**: Prevention measure details
- **scope**: Where this applies (Global, Local, Similar Lines)
- **rollout_plan**: Strategy for implementation
- **status**: (Planned, In Progress, Completed)

### `eight_d_recognitions` (D8)
Team and individual recognition records.
- **id** (PK): Unique identifier
- **process_id** (FK): Reference to `eight_d_processes`
- **recipient_id** (FK): Reference to `users`
- **recognition_type**: (Certificate, Announcement, Bonus, Mention)
- **message**: Personalized recognition message
- **awarded_by** (FK): Reference to `users`
- **awarded_date**: Date

---

## 4. Supporting Modules

### `manpower_records`
Daily attendance and manpower tracking.
- **id** (PK)
- **project_id** (FK)
- **date**: Date
- **total_count**: Integer
- **contractor_details**: JSON/Text

### `training_records`
Records of inductions and toolbox talks.
- **id** (PK)
- **type**: (Induction, Toolbox Talk)
- **topic**: Training subject
- **trainer_id** (FK)
- **date**: DateTime
- **attendees**: JSON array of names/IDs

### `safety_observations`
Ad-hoc safety observations.
- **id** (PK)
- **project_id** (FK)
- **observer_id** (FK)
- **category**: Observation category
- **description**: Text
- **risk_level**: (Low, Medium, High)
- **action_taken**: Text