# PTW Validation Rules

## Source: app/backend/ptw/validators.py

## Validation by Status Transition

### Draft → Submitted
**No special validation** - Basic field validation only

### Submitted/Under Review → Approved
**Function**: `validate_permit_requirements(permit, action='approve')`

**Required Checks**:

1. **Gas Testing** (if `permit_type.requires_gas_testing = true`)
   - At least one gas reading with `status='safe'` must exist
   - Error: "Gas testing is required before approve. At least one safe gas reading must be recorded."
   - Field: `gas_readings`

2. **Isolation Details** (if `permit_type.requires_isolation = true` OR `permit.requires_isolation = true`)
   - `permit.isolation_details` must not be empty
   - Error: "Isolation details are required before approve."
   - Field: `isolation_details`

3. **Mandatory PPE** (if `permit_type.mandatory_ppe` is not empty)
   - All items in `permit_type.mandatory_ppe` must be present in `permit.ppe_requirements`
   - Comparison is case-insensitive
   - Error: "Missing mandatory PPE: {list of missing items}"
   - Field: `ppe_requirements`

4. **Safety Checklist** (if `permit_type.safety_checklist` is not empty)
   - All required items in `permit_type.safety_checklist` must be completed in `permit.safety_checklist`
   - Error: "Checklist incomplete: {list of missing items}"
   - Field: `safety_checklist`

5. **Structured Isolation** (if `permit_type.requires_structured_isolation = true`)
   - Function: `validate_structured_isolation(permit, action='approve')`
   - At least one isolation point must be assigned
   - All required isolation points must be verified
   - Error: "Isolation points must be assigned and verified before approve."
   - Field: `isolation`

### Approved → Active
**Same validation as Approved** - Calls `validate_permit_requirements(permit, action='activate')`

### Active/Suspended → Completed
**Function**: `validate_closeout_completion(permit)` + `validate_deisolation_completion(permit)`

**Required Checks**:

1. **Closeout Completion** (if closeout template exists)
   - All required items in closeout checklist must be marked as done
   - Error: "Closeout checklist must be completed before marking permit as completed. Missing: {items}"
   - Field: `closeout`

2. **De-isolation** (if `permit_type.requires_deisolation_on_closeout = true`)
   - All verified isolation points must be de-isolated
   - Error: "All isolation points must be de-isolated before completing permit."
   - Field: `isolation`

## Cross-Field Validation

### Time Validation
**Source**: `PermitCreateUpdateSerializer.validate()`

- `planned_end_time` must be after `planned_start_time`
- Error: "End time must be after start time"
- Field: `planned_end_time`

### Permit Type Validation
**Source**: `PermitCreateUpdateSerializer.validate_permit_type()`

- Permit type must exist
- Permit type must be active (`is_active = true`)
- Error: "Invalid permit type ID" or "Selected permit type is not active"
- Field: `permit_type`

## Status Transition Rules

### Valid Transitions
**Source**: `Permit.can_transition_to(new_status)`

```
draft → [submitted, cancelled]
submitted → [under_review, rejected, draft]
under_review → [approved, rejected, submitted]
approved → [active, cancelled]
active → [completed, suspended]
suspended → [active, cancelled]
completed → []
cancelled → []
expired → []
rejected → [draft]
```

### Transition Validation
**Source**: `PermitStatusUpdateSerializer.validate_status()`

- Status must be a valid transition from current status
- Error: "Cannot transition from {current} to {new}"
- Field: `status`

## Extension Validation

### Extension Limit
**Source**: `validate_extension_limit(permit)`

- Maximum extensions allowed: `permit_type.max_extensions`
- Current extensions: Count of approved PermitExtension records
- Error: "Maximum extensions ({max}) reached for this permit type"

## Readiness Checks

### Source: app/backend/ptw/readiness.py :: get_permit_readiness()

**Returns readiness summary**:
```json
{
  "requires": {
    "gas_testing": boolean,
    "structured_isolation": boolean,
    "closeout": boolean,
    "deisolation": boolean
  },
  "readiness": {
    "can_verify": boolean,
    "can_approve": boolean,
    "can_activate": boolean,
    "can_complete": boolean
  },
  "missing": {
    "approve": [list of missing items],
    "activate": [list of missing items],
    "complete": [list of missing items]
  },
  "details": {
    "gas": {...},
    "isolation": {...},
    "ppe": {...},
    "checklist": {...},
    "closeout": {...}
  }
}
```

## Workflow-Driven Requirements

### Verification Step
- Requires verifier assignment
- Verifier must have appropriate role/grade
- Comments optional

### Approval Step
- Requires approver assignment
- Approver must have appropriate role/grade
- All validation checks must pass
- Comments optional

### Activation
- Permit must be in 'approved' status
- All validation checks must pass
- Sets `actual_start_time`

### Completion
- Permit must be in 'active' or 'suspended' status
- Closeout must be complete (if required)
- De-isolation must be complete (if required)
- Sets `actual_end_time`
