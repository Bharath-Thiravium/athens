#!/bin/bash
# PR8 Isolation Points Management - Validation Script

echo "=========================================="
echo "PR8 - Isolation Points Management"
echo "Validation Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

echo "1. Backend Model Validation"
echo "-------------------------------------------"

# Check IsolationPointLibrary model
if grep -q "class IsolationPointLibrary" app/backend/ptw/models.py; then
    pass "IsolationPointLibrary model exists"
else
    fail "IsolationPointLibrary model not found"
fi

# Check PermitIsolationPoint model
if grep -q "class PermitIsolationPoint" app/backend/ptw/models.py; then
    pass "PermitIsolationPoint model exists"
else
    fail "PermitIsolationPoint model not found"
fi

# Check requires_structured_isolation field
if grep -q "requires_structured_isolation" app/backend/ptw/models.py; then
    pass "requires_structured_isolation field exists on PermitType"
else
    fail "requires_structured_isolation field not found"
fi

# Check requires_deisolation_on_closeout field
if grep -q "requires_deisolation_on_closeout" app/backend/ptw/models.py; then
    pass "requires_deisolation_on_closeout field exists on PermitType"
else
    fail "requires_deisolation_on_closeout field not found"
fi

echo ""
echo "2. Backend Validator Validation"
echo "-------------------------------------------"

# Check validate_structured_isolation
if grep -q "def validate_structured_isolation" app/backend/ptw/validators.py; then
    pass "validate_structured_isolation function exists"
else
    fail "validate_structured_isolation function not found"
fi

# Check validate_deisolation_completion
if grep -q "def validate_deisolation_completion" app/backend/ptw/validators.py; then
    pass "validate_deisolation_completion function exists"
else
    fail "validate_deisolation_completion function not found"
fi

echo ""
echo "3. Backend Serializer Validation"
echo "-------------------------------------------"

# Check IsolationPointLibrarySerializer
if grep -q "IsolationPointLibrarySerializer" app/backend/ptw/serializers.py; then
    pass "IsolationPointLibrarySerializer exists"
else
    fail "IsolationPointLibrarySerializer not found"
fi

# Check PermitIsolationPointSerializer
if grep -q "PermitIsolationPointSerializer" app/backend/ptw/serializers.py; then
    pass "PermitIsolationPointSerializer exists"
else
    fail "PermitIsolationPointSerializer not found"
fi

echo ""
echo "4. Backend Views/Endpoints Validation"
echo "-------------------------------------------"

# Check IsolationPointLibraryViewSet
if grep -q "class IsolationPointLibraryViewSet" app/backend/ptw/views.py; then
    pass "IsolationPointLibraryViewSet exists"
else
    fail "IsolationPointLibraryViewSet not found"
fi

# Check isolation action endpoints
if grep -q "def isolation" app/backend/ptw/views.py; then
    pass "Isolation summary endpoint exists"
else
    fail "Isolation summary endpoint not found"
fi

if grep -q "def assign_isolation" app/backend/ptw/views.py; then
    pass "Assign isolation endpoint exists"
else
    fail "Assign isolation endpoint not found"
fi

if grep -q "def update_isolation" app/backend/ptw/views.py; then
    pass "Update isolation endpoint exists"
else
    fail "Update isolation endpoint not found"
fi

echo ""
echo "5. Migration Validation"
echo "-------------------------------------------"

# Check migration file
if [ -f "app/backend/ptw/migrations/0006_isolation_points.py" ]; then
    pass "Migration 0006_isolation_points.py exists"
else
    fail "Migration 0006_isolation_points.py not found"
fi

echo ""
echo "6. Backend Tests Validation"
echo "-------------------------------------------"

# Check test file
if [ -f "app/backend/ptw/tests/test_isolation_points.py" ]; then
    pass "Test file test_isolation_points.py exists"
    
    # Count test methods
    TEST_COUNT=$(grep -c "def test_" app/backend/ptw/tests/test_isolation_points.py)
    if [ "$TEST_COUNT" -ge 10 ]; then
        pass "Found $TEST_COUNT test cases (expected >= 10)"
    else
        warn "Found only $TEST_COUNT test cases (expected >= 10)"
    fi
else
    fail "Test file test_isolation_points.py not found"
fi

echo ""
echo "7. Frontend Types Validation"
echo "-------------------------------------------"

# Check IsolationPointLibrary interface
if grep -q "interface IsolationPointLibrary" app/frontend/src/features/ptw/types/index.ts; then
    pass "IsolationPointLibrary interface exists"
else
    fail "IsolationPointLibrary interface not found"
fi

# Check PermitIsolationPoint interface
if grep -q "interface PermitIsolationPoint" app/frontend/src/features/ptw/types/index.ts; then
    pass "PermitIsolationPoint interface exists"
else
    fail "PermitIsolationPoint interface not found"
fi

echo ""
echo "8. Frontend API Functions Validation"
echo "-------------------------------------------"

# Check API functions
if grep -q "getPermitIsolation" app/frontend/src/features/ptw/api.ts; then
    pass "Get isolation summary API function exists (getPermitIsolation)"
else
    fail "Get isolation summary API function not found"
fi

if grep -q "assignPermitIsolation" app/frontend/src/features/ptw/api.ts; then
    pass "Assign isolation API function exists (assignPermitIsolation)"
else
    fail "Assign isolation API function not found"
fi

if grep -q "updatePermitIsolation" app/frontend/src/features/ptw/api.ts; then
    pass "Update isolation API function exists (updatePermitIsolation)"
else
    fail "Update isolation API function not found"
fi

if grep -q "listIsolationPoints\|createIsolationPoint" app/frontend/src/features/ptw/api.ts; then
    pass "Isolation library API functions exist (listIsolationPoints, createIsolationPoint)"
else
    fail "Isolation library API functions not found"
fi

echo ""
echo "9. Frontend UI Component Validation"
echo "-------------------------------------------"

# Check isolation tab in PermitDetail
if grep -q "isolation" app/frontend/src/features/ptw/components/PermitDetail.tsx; then
    pass "Isolation tab exists in PermitDetail"
else
    fail "Isolation tab not found in PermitDetail"
fi

echo ""
echo "10. Django System Check"
echo "-------------------------------------------"

cd app/backend
if SECRET_KEY=dev python3 manage.py check > /dev/null 2>&1; then
    pass "Django system check passed"
else
    fail "Django system check failed"
fi
cd ../..

echo ""
echo "11. Frontend Build Check"
echo "-------------------------------------------"

cd app/frontend
if npm run build > /dev/null 2>&1; then
    pass "Frontend build successful"
else
    fail "Frontend build failed"
fi
cd ../..

echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "${GREEN}Passed:${NC} $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ PR8 validation successful!${NC}"
    exit 0
else
    echo -e "${RED}✗ PR8 validation failed with $FAIL errors${NC}"
    exit 1
fi
