# PTW Test Suite Improvements

## Summary

Added shared test helpers and test runner script to improve PTW test maintainability and reduce code duplication.

## Changes Made

### 1. Shared Test Helpers (`tests_common/fixtures.py`)

Added two new helper functions to reduce test setup duplication:

#### `create_ptw_permit_fixtures(user=None, project=None, permit_type_name='Hot Work', permit_type_category='hot_work')`
- Creates complete permit fixtures: permit type and permit
- Automatically creates user/project/tenant/induction if not provided
- Configurable permit type name and category
- Returns dict with all created fixtures

#### `create_ptw_closeout_fixtures(permit=None, template_items=None)`
- Creates closeout template and closeout record
- Creates permit fixtures if permit not provided
- Configurable template items (uses sensible defaults)
- Returns dict with template, closeout, and permit fixtures

### 2. Updated Exports (`tests_common/__init__.py`)
- Added new helper functions to module exports
- Available for import across all test files

### 3. Test Runner Script (`run_ptw_tests.sh`)
- Automated PTW test execution with `--keepdb` flag
- Proper environment variable setup
- Database availability checking
- Colored output for better readability
- Error handling and exit codes

### 4. Example Usage (`ptw/tests/test_shared_helpers_example.py`)
- Demonstrates how to use the new helpers
- Shows before/after comparison of test setup
- Examples of basic and advanced usage patterns

## Benefits

### Reduced Code Duplication
- **Before**: Each test class creates its own user, project, permit type, permit, template, closeout
- **After**: One-line fixture creation with sensible defaults

### Improved Maintainability
- Centralized fixture creation logic
- Consistent test data across all PTW tests
- Easy to modify default test data in one place

### Better Test Performance
- `--keepdb` flag preserves test database between runs
- Faster subsequent test executions
- Automated environment setup

## Usage Examples

### Basic Permit Test
```python
def test_permit_functionality(self):
    fixtures = create_ptw_permit_fixtures()
    permit = fixtures['permit']
    # Test permit logic...
```

### Basic Closeout Test
```python
def test_closeout_functionality(self):
    fixtures = create_ptw_closeout_fixtures()
    closeout = fixtures['closeout']
    # Test closeout logic...
```

### Custom Configuration
```python
def test_electrical_permit(self):
    fixtures = create_ptw_permit_fixtures(
        permit_type_name='Electrical Work',
        permit_type_category='electrical'
    )
    # Test electrical-specific logic...
```

## Running Tests

### With New Script (Recommended)
```bash
./run_ptw_tests.sh
```

### Manual Execution
```bash
cd app/backend
export SECRET_KEY='test-secret-key'
python3 manage.py test ptw.tests --keepdb -v 2
```

## Files Modified/Created

1. **Modified**: `app/backend/tests_common/fixtures.py` - Added PTW helpers
2. **Modified**: `app/backend/tests_common/__init__.py` - Updated exports
3. **Created**: `run_ptw_tests.sh` - Test runner script
4. **Created**: `app/backend/ptw/tests/test_shared_helpers_example.py` - Usage examples

## Next Steps

1. **Run Test Suite**: Execute `./run_ptw_tests.sh` when database is available
2. **Refactor Existing Tests**: Update existing PTW tests to use new helpers
3. **Verify No Regressions**: Confirm all tests pass with `--keepdb`

## Database Requirements

The test runner requires:
- PostgreSQL running on localhost
- Ability to create/access test database
- Standard Django test database permissions

If database connection fails, the script provides clear error messages and suggestions.