# PTW API Payload Examples

## Example 1: Minimal Valid Permit Creation (Draft)

### POST /api/v1/ptw/permits/

```json
{
  "permit_type": 1,
  "description": "Welding work on pipeline section A-12",
  "location": "Plant Area 3, Building A",
  "planned_start_time": "2024-01-20T08:00:00Z",
  "planned_end_time": "2024-01-20T17:00:00Z"
}
```

**Response**: 201 Created
```json
{
  "id": 123,
  "permit_number": "PTW-2024-00123",
  "status": "draft",
  "permit_type": 1,
  "description": "Welding work on pipeline section A-12",
  "location": "Plant Area 3, Building A",
  "planned_start_time": "2024-01-20T08:00:00Z",
  "planned_end_time": "2024-01-20T17:00:00Z",
  "created_by": 5,
  "project": 13,
  "created_at": "2024-01-15T10:30:00Z",
  ...
}
```

## Example 2: Complete Permit Creation with All Fields

### POST /api/v1/ptw/permits/

```json
{
  "permit_type": 1,
  "title": "Hot Work - Pipeline Welding",
  "description": "Welding repair on pipeline section A-12 due to corrosion damage. Work includes grinding, welding, and post-weld inspection.",
  "work_order_id": "WO-2024-5678",
  "location": "Plant Area 3, Building A, Level 2",
  "gps_coordinates": "12.9716,77.5946",
  "planned_start_time": "2024-01-20T08:00:00Z",
  "planned_end_time": "2024-01-20T17:00:00Z",
  "work_nature": "day",
  "priority": "high",
  "risk_assessment_id": "RA-2024-001",
  "risk_assessment_completed": true,
  "probability": 3,
  "severity": 4,
  "control_measures": "Fire watch assigned, combustibles removed, fire extinguisher available, hot work permit displayed",
  "ppe_requirements": [
    "Hard Hat",
    "Safety Boots",
    "Welding Helmet",
    "Leather Gloves",
    "Fire-resistant Coveralls"
  ],
  "special_instructions": "Maintain 10m clearance from flammable materials. Fire watch to remain for 30 minutes after work completion.",
  "safety_checklist": {
    "work_scope_defined": true,
    "work_area_checked": true,
    "tools_inspected": true,
    "hot_work_area_cleared": true,
    "fire_watch_assigned": true,
    "spark_containment_in_place": true
  },
  "requires_isolation": true,
  "isolation_details": "Valve V-123 closed and locked, pressure relieved, line blanked",
  "compliance_standards": ["OSHA 1910.252", "NFPA 51B"],
  "permit_parameters": {
    "hot_work_area_cleared": true,
    "fire_watch_assigned": true,
    "spark_containment_in_place": true
  }
}
```

## Example 3: Submit Permit (Draft → Submitted)

### POST /api/v1/ptw/permits/123/update_status/

```json
{
  "status": "submitted",
  "comments": "All safety requirements completed, ready for verification"
}
```

**Response**: 200 OK
```json
{
  "id": 123,
  "permit_number": "PTW-2024-00123",
  "status": "submitted",
  "submitted_at": "2024-01-15T11:00:00Z",
  ...
}
```

## Example 4: Verify Permit (Submitted → Under Review)

### POST /api/v1/ptw/permits/123/verify/

```json
{
  "action": "approve",
  "comments": "Safety checklist verified, all requirements met",
  "selected_approver_id": 10
}
```

**Response**: 200 OK
```json
{
  "id": 123,
  "status": "under_review",
  "verifier": 8,
  "verified_at": "2024-01-15T11:30:00Z",
  "verification_comments": "Safety checklist verified, all requirements met",
  ...
}
```

## Example 5: Approve Permit (Under Review → Approved)

### POST /api/v1/ptw/permits/123/approve/

```json
{
  "comments": "Approved with condition: Fire watch must remain for 1 hour after completion"
}
```

**Response**: 200 OK
```json
{
  "id": 123,
  "status": "approved",
  "approved_by": 10,
  "approved_at": "2024-01-15T12:00:00Z",
  "approval_comments": "Approved with condition: Fire watch must remain for 1 hour after completion",
  ...
}
```

## Example 6: Activate Permit (Approved → Active)

### POST /api/v1/ptw/permits/123/update_status/

```json
{
  "status": "active",
  "comments": "Work started, all personnel briefed"
}
```

**Response**: 200 OK
```json
{
  "id": 123,
  "status": "active",
  "actual_start_time": "2024-01-20T08:15:00Z",
  ...
}
```

## Example 7: Complete Permit (Active → Completed)

### POST /api/v1/ptw/permits/123/update_status/

```json
{
  "status": "completed",
  "comments": "Work completed successfully, area cleaned, fire watch maintained for 1 hour"
}
```

**Response**: 200 OK (if closeout complete)
```json
{
  "id": 123,
  "status": "completed",
  "actual_end_time": "2024-01-20T16:45:00Z",
  ...
}
```

**Response**: 400 Bad Request (if closeout incomplete)
```json
{
  "closeout": "Closeout checklist must be completed before marking permit as completed. Missing: Equipment inspection, Area cleanup verification"
}
```

## Example 8: Reject Permit

### POST /api/v1/ptw/permits/123/reject/

```json
{
  "comments": "Insufficient risk assessment. Please provide detailed HIRA before resubmission."
}
```

**Response**: 200 OK
```json
{
  "id": 123,
  "status": "rejected",
  ...
}
```

## Example 9: Add Gas Reading

### POST /api/v1/ptw/gas-readings/

```json
{
  "permit": 123,
  "gas_type": "LEL",
  "reading_value": 0.5,
  "unit": "%",
  "status": "safe",
  "tested_by": 15,
  "tested_at": "2024-01-20T07:45:00Z",
  "location": "Inside pipeline section A-12",
  "remarks": "Reading taken after 10 minutes ventilation"
}
```

## Example 10: Assign Isolation Point

### POST /api/v1/ptw/permits/123/assign_isolation/

```json
{
  "point_id": 45,
  "required": true,
  "lock_count": 2,
  "order": 1
}
```

Or assign custom point:
```json
{
  "custom_point_name": "Temporary Electrical Disconnect",
  "custom_point_details": "Main power supply to welding area",
  "required": true,
  "lock_count": 1,
  "order": 2
}
```

## Example 11: Update Isolation Point Status

### POST /api/v1/ptw/permits/123/update_isolation/

```json
{
  "point_id": 45,
  "action": "isolate",
  "lock_applied": true,
  "lock_count": 2,
  "lock_ids": ["LOCK-001", "LOCK-002"]
}
```

Then verify:
```json
{
  "point_id": 45,
  "action": "verify",
  "verification_notes": "Zero energy confirmed, locks secure"
}
```

Then de-isolate (at closeout):
```json
{
  "point_id": 45,
  "action": "deisolate",
  "deisolated_notes": "System restored to normal operation"
}
```

## Example 12: Complete Closeout Checklist

### GET /api/v1/ptw/permits/123/closeout/
Returns current closeout status

### POST /api/v1/ptw/permits/123/update_closeout/

```json
{
  "checklist": {
    "equipment_inspection": {
      "done": true,
      "comments": "All equipment inspected and stored"
    },
    "area_cleanup": {
      "done": true,
      "comments": "Work area cleaned and debris removed"
    },
    "tools_returned": {
      "done": true,
      "comments": "All tools accounted for and returned"
    }
  },
  "remarks": "Work completed as per plan, no incidents"
}
```

### POST /api/v1/ptw/permits/123/complete_closeout/

```json
{}
```

**Response**: 200 OK (if all required items done)
```json
{
  "id": 5,
  "permit": 123,
  "completed": true,
  "completed_at": "2024-01-20T16:40:00Z",
  "is_complete": true,
  "missing_items": []
}
```

## Example 13: Add Toolbox Talk

### POST /api/v1/ptw/toolbox-talks/

```json
{
  "permit": 123,
  "conducted_by": 15,
  "conducted_at": "2024-01-20T07:30:00Z",
  "topics_covered": [
    "Hot work hazards",
    "Fire prevention",
    "Emergency procedures",
    "PPE requirements"
  ],
  "attendees": [20, 21, 22, 23]
}
```

## Example 14: Request Extension

### POST /api/v1/ptw/extensions/

```json
{
  "permit": 123,
  "new_end_time": "2024-01-20T20:00:00Z",
  "reason": "Additional welding required due to discovered corrosion in adjacent section"
}
```

## Validation Error Examples

### Missing Required Field
```json
{
  "description": ["This field is required."]
}
```

### Invalid Time Range
```json
{
  "planned_end_time": ["End time must be after start time"]
}
```

### Missing Gas Testing
```json
{
  "gas_readings": ["Gas testing is required before approve. At least one safe gas reading must be recorded."]
}
```

### Missing PPE
```json
{
  "ppe_requirements": ["Missing mandatory PPE: Welding Helmet, Fire-resistant Coveralls"]
}
```

### Incomplete Checklist
```json
{
  "safety_checklist": ["Checklist incomplete: hot_work_area_cleared, fire_watch_assigned"]
}
```

### Invalid Status Transition
```json
{
  "status": ["Cannot transition from draft to active"]
}
```

### Closeout Incomplete
```json
{
  "closeout": ["Closeout checklist must be completed before marking permit as completed. Missing: Equipment inspection, Area cleanup verification"]
}
```
