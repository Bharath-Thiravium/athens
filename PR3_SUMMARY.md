# COMMIT/PR 3 — BACKEND VALIDATION HARDENING

## Summary

Implemented backend enforcement of PermitType requirements to ensure data integrity and compliance without relying on frontend validation. Requirements are enforced at critical gating stages (approve/activate) while allowing draft saves to proceed freely.

## Requirements Enforced

### A) Gas Testing
- **Rule**: If `PermitType.requires_gas_testing = True`, at least one `GasReading` with `status='safe'` must exist
- **Enforced at**: Approval and activation
- **Error message**: "Gas testing is required before {action}. At least one safe gas reading must be recorded."

### B) Isolation
- **Rule**: If `PermitType.requires_isolation = True` OR `Permit.requires_isolation = True`, `isolation_details` must be non-empty
- **Enforced at**: Approval and activation
- **Error message**: "Isolation details are required before {action}."

### C) Mandatory PPE
- **Rule**: If `PermitType.mandatory_ppe` contains items, all must be present in `Permit.ppe_requirements`
- **Matching**: Case-insensitive, whitespace-tolerant
- **Enforced at**: Approval and activation
- **Error message**: "Missing mandatory PPE: {list of missing items}"

### D) Safety Checklist
- **Rule**: If `PermitType.safety_checklist` is present, all required items must be completed in `Permit.safety_checklist`
- **Supports**: Both list of strings and list of objects with `{key, label, required}`
- **Enforced at**: Approval and activation
- **Error message**: "Checklist incomplete: {list of incomplete items}"

### E) Max Validity Extensions
- **Rule**: If `PermitType.max_validity_extensions > 0`, count of non-rejected extensions must not exceed limit
- **Counting**: Approved + Pending extensions (rejected excluded)
- **Enforced at**: PermitExtension creation
- **Error message**: "Maximum validity extensions ({limit}) already reached for this permit."

## Enforcement Points

### 1. PermitStatusUpdateSerializer
- **File**: `app/backend/ptw/serializers.py`
- **Triggers**: When `status` transitions to `'approved'` or `'active'`
- **Used by**: `PermitViewSet.update_status()` action

### 2. Workflow approve_permit endpoint
- **File**: `app/backend/ptw/workflow_views.py`
- **Triggers**: When approver approves permit (action='approve')
- **Used by**: Workflow approval flow

### 3. PermitExtensionSerializer
- **File**: `app/backend/ptw/serializers.py`
- **Triggers**: On PermitExtension creation (not update)
- **Used by**: Extension request endpoints

## Files Modified

- `app/backend/ptw/serializers.py`
  - Updated `PermitExtensionSerializer.validate()` to enforce max extensions
  - Updated `PermitStatusUpdateSerializer.validate()` to enforce requirements on approve/activate

- `app/backend/ptw/workflow_views.py`
  - Updated `approve_permit()` to validate requirements before approval

## Files Created

- `app/backend/ptw/validators.py`
  - `validate_permit_requirements(permit, action)` - Main validation function
  - `validate_extension_limit(permit)` - Extension limit validation

- `tests/backend/ptw/test_permit_type_requirements.py`
  - 18 comprehensive tests covering all requirements and edge cases

## Test Coverage

✅ **Gas Testing**
- test_gas_testing_required_blocks_approve_without_safe_reading
- test_gas_testing_passes_with_safe_reading

✅ **Isolation**
- test_isolation_required_blocks_approve_without_details
- test_isolation_passes_with_details

✅ **Mandatory PPE**
- test_mandatory_ppe_blocks_approve_if_missing
- test_mandatory_ppe_passes_with_all_items

✅ **Safety Checklist**
- test_checklist_blocks_approve_if_incomplete
- test_checklist_passes_when_complete

✅ **Draft Saves**
- test_requirements_not_enforced_on_draft_save
- test_status_update_serializer_allows_draft_without_requirements

✅ **Serializer Integration**
- test_status_update_serializer_enforces_requirements_on_approve

✅ **Max Extensions**
- test_max_validity_extensions_blocks_creation_when_limit_reached
- test_rejected_extensions_not_counted
- test_pending_extensions_counted_toward_limit
- test_extension_serializer_enforces_limit

✅ **Edge Cases**
- test_no_requirements_for_simple_permit_type
- test_requirements_block_activation_if_missing

## Test Commands

```bash
# Run PR3 tests only
cd /var/www/athens/app/backend
source venv/bin/activate
python3 manage.py test ptw.tests.test_permit_type_requirements

# Run all PTW tests
python3 manage.py test ptw.tests

# Run specific test
python3 manage.py test ptw.tests.test_permit_type_requirements.PermitTypeRequirementsTestCase.test_gas_testing_required_blocks_approve_without_safe_reading

# System check
python3 manage.py check ptw
```

## Backward Compatibility

✅ **No Breaking Changes**
- Draft permits can still be saved without meeting requirements
- Existing permits without requirements continue to work
- Only new approve/activate transitions are gated
- Error messages are clear and actionable

✅ **Graceful Degradation**
- If PermitType has no requirements, validation passes immediately
- Missing or empty requirement fields are treated as "no requirement"
- Case-insensitive PPE matching prevents false negatives

## Example Error Response

```json
{
  "gas_readings": "Gas testing is required before approval. At least one safe gas reading must be recorded.",
  "isolation_details": "Isolation details are required before approval.",
  "ppe_requirements": "Missing mandatory PPE: Gloves, Safety Harness",
  "safety_checklist": "Checklist incomplete: Fire extinguisher available, Barricading done"
}
```

## Status

✅ **Complete** - All requirements implemented, 18 tests passing, system check clean.

## Next Steps

Proceed to **COMMIT/PR 4** - API Contract Alignment (Frontend endpoint mapping)
