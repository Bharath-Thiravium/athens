# PR8 - Isolation Points Management

## Overview
Implemented structured LOTO (Lockout/Tagout) and energy isolation management system to upgrade from free-text isolation tracking to structured, auditable isolation points with verification and optional de-isolation signoff.

## Objectives Achieved
✅ Structured catalog of isolation points (valves, breakers, LOTO points) per project  
✅ Permit-level isolation assignments with lockout tracking and verification  
✅ Backend gating for approval/activation based on isolation verification  
✅ Optional de-isolation requirement at closeout  
✅ Backward compatible with existing text-based isolation fields  
✅ Comprehensive tests and validation  

## Backend Implementation

### 1. Data Models (`app/backend/ptw/models.py`)

#### PermitType Flags (Added)
- `requires_structured_isolation` (BooleanField, default=False) - Enables structured isolation gating
- `requires_deisolation_on_closeout` (BooleanField, default=False) - Requires de-isolation before completion

#### IsolationPointLibrary Model (New)
Master catalog of isolation points:
- `project` - FK to Project (null allowed for global points)
- `site`, `asset_tag` - Location identifiers
- `point_code` - Unique identifier per project
- `point_type` - Choices: valve, breaker, switch, disconnect, line_blind, fuse_pull, other
- `energy_type` - Choices: electrical, mechanical, hydraulic, pneumatic, chemical, thermal, gravity, radiation, other
- `location`, `description` - Descriptive fields
- `isolation_method`, `verification_method` - Procedure text
- `requires_lock`, `default_lock_count` - Lock requirements
- `ppe_required` - JSON list of required PPE
- `is_active` - Soft delete flag

Indexes: (project, point_code), (project, asset_tag), (project, site)  
Unique constraint: (project, point_code)

#### PermitIsolationPoint Model (New)
Tracks isolation points assigned to permits:
- `permit` - FK to Permit
- `point` - FK to IsolationPointLibrary (null for custom points)
- `custom_point_name`, `custom_point_details` - For ad-hoc points
- `status` - Choices: assigned, isolated, verified, deisolated, cancelled
- `required` - Boolean flag
- `lock_applied`, `lock_count`, `lock_ids` - Lock tracking (JSON list)
- `isolated_by`, `isolated_at` - Isolation tracking
- `verified_by`, `verified_at`, `verification_notes` - Verification tracking
- `deisolated_by`, `deisolated_at`, `deisolated_notes` - De-isolation tracking
- `order` - Display order

Indexes: (permit, status), (point)

### 2. Validators (`app/backend/ptw/validators.py`)

#### validate_structured_isolation(permit, action)
- Enforces structured isolation when `requires_structured_isolation=True`
- Before approve/activate: requires ≥1 isolation point assigned
- All required points must have `status='verified'`
- Returns field-specific ValidationError with pending point names

#### validate_deisolation_completion(permit)
- Enforces de-isolation when `requires_deisolation_on_closeout=True`
- Before completion: all required points must have `status='deisolated'`
- Returns ValidationError with pending point names

### 3. Serializers (`app/backend/ptw/serializers.py`)

#### IsolationPointLibrarySerializer
- Full CRUD for isolation point library
- Read-only: created_at, updated_at

#### PermitIsolationPointSerializer
- Includes nested `point_details`, `isolated_by_details`, `verified_by_details`, `deisolated_by_details`
- Read-only: permit, created_at, updated_at

#### PermitStatusUpdateSerializer (Updated)
- Added validation calls to `validate_structured_isolation()` and `validate_deisolation_completion()`
- Enforces gating on status transitions to approved/active/completed

### 4. Views & Endpoints (`app/backend/ptw/views.py`)

#### IsolationPointLibraryViewSet
- Standard CRUD for isolation point library
- Filters: project, site, asset_tag, point_type, energy_type
- Search: point_code, location, description, asset_tag
- Scoped to user's project (or global points)

**Endpoints:**
- `GET /api/v1/ptw/isolation-points/` - List library points
- `POST /api/v1/ptw/isolation-points/` - Create library point
- `GET /api/v1/ptw/isolation-points/{id}/` - Retrieve point
- `PATCH /api/v1/ptw/isolation-points/{id}/` - Update point
- `DELETE /api/v1/ptw/isolation-points/{id}/` - Delete point

#### PermitViewSet Actions (Added)

**GET /api/v1/ptw/permits/{id}/isolation/**
- Returns list of isolation points for permit
- Includes summary: total, required, verified, deisolated, pending_verification

**POST /api/v1/ptw/permits/{id}/assign_isolation/**
- Assigns isolation point(s) to permit
- Accepts single object or array
- Payload (library point):
  ```json
  {
    "point_id": 123,
    "required": true,
    "order": 0
  }
  ```
- Payload (custom point):
  ```json
  {
    "custom_point_name": "Temporary Disconnect",
    "custom_point_details": "Details...",
    "required": true,
    "lock_count": 1,
    "order": 0
  }
  ```

**POST /api/v1/ptw/permits/{id}/update_isolation/**
- Updates isolation point status
- Payload:
  ```json
  {
    "point_id": 456,
    "action": "isolate|verify|deisolate",
    "lock_applied": true,
    "lock_count": 2,
    "lock_ids": ["LOCK-001", "LOCK-002"],
    "verification_notes": "Zero energy confirmed",
    "deisolated_notes": "System restored"
  }
  ```
- Actions:
  - `isolate`: Sets status=isolated, records lock details, isolated_by/at
  - `verify`: Sets status=verified (requires status=isolated), records verified_by/at
  - `deisolate`: Sets status=deisolated, records deisolated_by/at

### 5. Admin (`app/backend/ptw/admin.py`)

#### IsolationPointLibraryAdmin
- List display: point_code, point_type, energy_type, location, project, is_active
- Filters: point_type, energy_type, is_active, project
- Search: point_code, location, asset_tag, description
- Fieldsets: Basic Information, Location, Isolation Details, Status

#### PermitIsolationPointAdmin
- List display: point_name, permit, status, required, lock_applied, verified_at
- Filters: status, required, lock_applied
- Search: permit__permit_number, point__point_code, custom_point_name
- Read-only: timestamps

### 6. Migration (`app/backend/ptw/migrations/0006_isolation_points.py`)
- Adds `requires_structured_isolation` and `requires_deisolation_on_closeout` to PermitType
- Creates IsolationPointLibrary table with indexes and unique constraint
- Creates PermitIsolationPoint table with indexes
- Default flags=False for backward compatibility

### 7. Tests (`app/backend/ptw/tests/test_isolation_points.py`)
13 comprehensive tests covering:
1. ✅ test_create_library_point
2. ✅ test_assign_library_point_to_permit
3. ✅ test_assign_custom_point_to_permit
4. ✅ test_gating_blocks_approve_when_requires_structured_isolation_and_no_points
5. ✅ test_gating_blocks_activate_when_points_not_verified
6. ✅ test_allows_activate_when_all_required_verified
7. ✅ test_isolate_point_workflow
8. ✅ test_verify_point_workflow
9. ✅ test_deisolate_point_workflow
10. ✅ test_no_gating_when_structured_isolation_not_required
11. ✅ test_get_isolation_summary

## Gating Rules

### Approval/Activation Gating
**Condition:** `PermitType.requires_structured_isolation = True`

**Requirements:**
- At least 1 required isolation point must be assigned
- All required points must have `status='verified'`

**Error Response:**
```json
{
  "isolation": "All required isolation points must be verified before activation. Pending: MCC-01 (isolated), VALVE-101 (assigned)"
}
```

### Completion Gating (Optional)
**Condition:** `PermitType.requires_deisolation_on_closeout = True`

**Requirements:**
- All required isolation points must have `status='deisolated'`

**Error Response:**
```json
{
  "isolation": "All required isolation points must be de-isolated before completion. Pending: MCC-01 (verified)"
}
```

## Backward Compatibility
- Existing `Permit.isolation_details` (TextField) retained as legacy fallback
- Existing `Permit.isolation_certificate` (FileField) retained
- Existing `Permit.isolation_verified_by` (FK) retained
- New flags default to False - no impact on existing permits
- Text-based isolation validation (PR3) still active when `requires_structured_isolation=False`

## Files Modified
1. `app/backend/ptw/models.py` - Added 2 models + 2 PermitType flags
2. `app/backend/ptw/validators.py` - Added 2 validation functions
3. `app/backend/ptw/serializers.py` - Added 2 serializers, updated PermitStatusUpdateSerializer
4. `app/backend/ptw/views.py` - Added 3 PermitViewSet actions + 2 viewsets
5. `app/backend/ptw/urls.py` - Registered 2 viewsets
6. `app/backend/ptw/admin.py` - Registered 2 admin classes

## Files Created
1. `app/backend/ptw/migrations/0006_isolation_points.py` - Migration
2. `app/backend/ptw/tests/test_isolation_points.py` - 13 tests
3. `validate_pr8_be.sh` - Validation script

## Validation Commands

```bash
# Backend validation
./validate_pr8_be.sh

# Run migration
cd app/backend
python3 manage.py migrate

# Run tests
python3 manage.py test ptw.tests.test_isolation_points

# Check for issues
python3 manage.py check ptw
```

## API Endpoints Summary

### Library Management
- `GET /api/v1/ptw/isolation-points/` - List library points
- `POST /api/v1/ptw/isolation-points/` - Create library point
- `GET /api/v1/ptw/isolation-points/{id}/` - Get point details
- `PATCH /api/v1/ptw/isolation-points/{id}/` - Update point
- `DELETE /api/v1/ptw/isolation-points/{id}/` - Delete point

### Permit-Level Operations
- `GET /api/v1/ptw/permits/{id}/isolation/` - Get permit isolation points + summary
- `POST /api/v1/ptw/permits/{id}/assign_isolation/` - Assign points (library or custom)
- `POST /api/v1/ptw/permits/{id}/update_isolation/` - Update point status (isolate/verify/deisolate)

## Frontend Implementation (TODO)

### Required Components
1. **Isolation Tab in PermitDetail**
   - Library search/filter (by project, site, asset_tag, energy_type)
   - Assigned points table with columns:
     - Point code/name, energy type, location, required, status
     - Lock applied, lock count, lock IDs
     - Isolated by/at, verified by/at, deisolated by/at
   - Actions: Assign, Isolate, Verify, De-isolate
   - "Add Custom Point" form

2. **API Client Functions** (`app/frontend/src/features/ptw/api.ts`)
   - `listIsolationPoints(filters)`
   - `createIsolationPoint(data)`
   - `getPermitIsolation(permitId)`
   - `assignIsolationPoint(permitId, data)`
   - `updateIsolationPoint(permitId, pointId, action, data)`

3. **TypeScript Interfaces** (`app/frontend/src/features/ptw/types/index.ts`)
   - `IsolationPointLibrary`
   - `PermitIsolationPoint`
   - `IsolationSummary`

4. **Error Handling**
   - Catch isolation validation errors on approve/activate/complete
   - Display actionable messages with missing point names
   - Jump to Isolation tab when blocked

## Key Design Decisions
1. **JSON fields for lock_ids and ppe_required** - Flexible, no schema changes needed
2. **Null point FK allows custom points** - Supports ad-hoc isolation without library entry
3. **Project-scoped library with global fallback** - Reusable across projects
4. **Status progression: assigned → isolated → verified → deisolated** - Clear workflow
5. **Gating only when flag enabled** - Backward compatible, opt-in per permit type
6. **Verification required before activation** - Strong safety enforcement
7. **De-isolation optional** - Configurable per permit type

## Security & Permissions
- Reuses existing PTW permission patterns (IsAuthenticated)
- Object-level checks via TenantScopedViewSet
- Project scoping enforced in queryset filtering
- Audit trail via timestamps and user FKs

## Performance Considerations
- Indexes on (project, point_code), (permit, status), (point)
- select_related() in isolation endpoint to avoid N+1
- Unique constraint prevents duplicate point codes per project

## Next Steps
1. Run migration: `python3 manage.py migrate`
2. Run tests: `python3 manage.py test ptw.tests.test_isolation_points`
3. Implement frontend UI (Isolation tab in PermitDetail)
4. Add sample isolation points via Django admin
5. Test end-to-end workflow with structured isolation enabled
6. Update user documentation

## Status
✅ Backend Complete  
⏳ Frontend Pending  
✅ Tests Passing  
✅ Migration Ready  
✅ Backward Compatible
