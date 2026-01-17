# COMMIT/PR 2 — FIX BROKEN FIELD REFERENCES (PermitExtension)

## Summary of Changes

Fixed `PermitExtension._check_work_nature_change()` method that was referencing non-existent fields on the Permit model, causing crashes when saving permit extensions.

## Problem Fixed

**Before:** Method referenced these non-existent Permit fields:
- `self.permit.day_work_start`
- `self.permit.day_work_end`
- `self.permit.night_work_end`

**After:** Method now uses the existing `get_work_time_settings()` utility from `ptw.utils` which provides:
- `day_start`: time(8, 0)
- `day_end`: time(18, 0)
- `night_start`: time(20, 0)
- `night_end`: time(6, 0)

## Logic Explanation

The `_check_work_nature_change()` method now:

1. Gets work time settings from centralized utility
2. Checks if `new_end_time` crosses work nature boundaries:
   - **Day work** → Returns `True` if extending past 6 PM (day_end) or before 6 AM (night_end)
   - **Night work** → Returns `True` if extending into day hours (8 AM - 6 PM)
   - **Both** → Returns `False` (no restriction)
3. Sets `affects_work_nature` flag accordingly
4. Never crashes due to missing fields

## Files Modified

- `app/backend/ptw/models.py` - Fixed `PermitExtension._check_work_nature_change()`

## Files Created

- `tests/backend/ptw/test_permit_extension.py` - Comprehensive test suite with 11 tests

## Test Coverage

Tests verify:
- ✅ Extension save does not crash
- ✅ Extension hours calculated correctly
- ✅ Day-to-night crossing detected
- ✅ Night-to-day crossing detected
- ✅ Same-window extensions don't trigger flag
- ✅ 'Both' work nature handling
- ✅ Multiple extensions per permit
- ✅ Status workflow transitions

## Commands to Run

### Syntax Check (Quick validation - no DB needed)
```bash
cd /var/www/athens/app/backend
export SECRET_KEY='test-key'
python3 manage.py check ptw
```

### Run Tests (REQUIRES PostgreSQL)
```bash
cd /var/www/athens/app/backend

# Option 1: Use existing database configuration
source venv/bin/activate
python3 manage.py test ptw.tests.test_permit_extension

# Option 2: With explicit PostgreSQL connection
export DATABASE_URL='postgresql://user:password@localhost:5432/athens_db'
python3 manage.py test ptw.tests.test_permit_extension

# Option 3: Run all PTW tests
python3 manage.py test ptw
```

### Run Tests via Docker (Recommended for CI/CD)
```bash
cd /var/www/athens
docker-compose -f docker-compose.dev.yml exec backend python manage.py test ptw.tests.test_permit_extension
```

## Status

✅ **Complete** - All changes implemented, syntax validated, ready for PostgreSQL testing.

## Next Steps

After running tests successfully:
- Proceed to **COMMIT/PR 3** - Backend Validation Hardening (PermitType requirements)
