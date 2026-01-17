#!/bin/bash

echo "========================================="
echo "PR12 Validation - Offline Sync Conflict Resolution"
echo "========================================="
echo ""

PASS=0
FAIL=0

check() {
    if [ $? -eq 0 ]; then
        echo "✓ $1"
        ((PASS++))
    else
        echo "✗ $1"
        ((FAIL++))
    fi
}

cd /var/www/athens

# 1. Check migration file exists
echo "[1/12] Checking migration file..."
test -f app/backend/ptw/migrations/0009_add_version_and_idempotency.py
check "Migration file exists"

# 2. Check version fields in models
echo "[2/12] Checking version fields in models..."
grep -q "version = models.IntegerField(default=1" app/backend/ptw/models.py
check "Version fields added to models"

# 3. Check AppliedOfflineChange model
echo "[3/12] Checking AppliedOfflineChange model..."
grep -q "class AppliedOfflineChange" app/backend/ptw/models.py
check "AppliedOfflineChange model exists"

# 4. Check conflict_utils module
echo "[4/12] Checking conflict resolution utilities..."
test -f app/backend/ptw/conflict_utils.py
check "conflict_utils.py exists"

# 5. Check conflict detection functions
echo "[5/12] Checking conflict detection functions..."
grep -q "def detect_permit_conflicts" app/backend/ptw/conflict_utils.py
check "Conflict detection functions exist"

# 6. Check updated sync endpoint
echo "[7/12] Checking updated sync_offline_data endpoint..."
grep -q "from .conflict_utils import" app/backend/ptw/views.py
check "Sync endpoint uses conflict utilities"

# 7. Check frontend types
echo "[7/12] Checking frontend TypeScript types..."
test -f app/frontend/src/features/ptw/types/offlineSync.ts
check "Offline sync types defined"

# 8. Check updated useOfflineSync hook
echo "[8/12] Checking updated useOfflineSync hook..."
test -f app/frontend/src/features/ptw/hooks/useOfflineSync2.ts
check "Updated useOfflineSync hook exists"

# 9. Check SyncStatusIndicator component
echo "[9/12] Checking SyncStatusIndicator component..."
test -f app/frontend/src/features/ptw/components/SyncStatusIndicator.tsx
check "SyncStatusIndicator component exists"

# 10. Check SyncConflictsPage component
echo "[10/12] Checking SyncConflictsPage component..."
test -f app/frontend/src/features/ptw/components/SyncConflictsPage.tsx
check "SyncConflictsPage component exists"

# 11. Check backend tests
echo "[11/12] Checking backend tests..."
test -f app/backend/ptw/tests/test_offline_sync_conflicts.py
check "Backend conflict tests exist"

# 12. Python syntax validation
echo "[12/12] Validating Python syntax..."
cd app/backend
python3 -m py_compile ptw/models.py ptw/conflict_utils.py ptw/views.py ptw/tests/test_offline_sync_conflicts.py 2>/dev/null
check "Python syntax valid"

echo ""
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo "Passed: $PASS/12"
echo "Failed: $FAIL/12"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All validations passed!"
    exit 0
else
    echo "✗ Some validations failed"
    exit 1
fi
