#!/bin/bash
# PR7 Validation Script - Permit Closeout Checklist

set -e

echo "=========================================="
echo "PR7 VALIDATION - Closeout Checklist"
echo "=========================================="
echo ""

# Check 1: Verify closeout models exist
echo "✓ Check 1: Verify closeout models added"
if grep -q "class CloseoutChecklistTemplate" app/backend/ptw/models.py && \
   grep -q "class PermitCloseout" app/backend/ptw/models.py; then
    echo "  ✓ PASS: Closeout models added to models.py"
else
    echo "  ✗ FAIL: Closeout models not found"
    exit 1
fi
echo ""

# Check 2: Verify closeout validation exists
echo "✓ Check 2: Verify closeout validation function"
if grep -q "def validate_closeout_completion" app/backend/ptw/validators.py; then
    echo "  ✓ PASS: validate_closeout_completion added to validators.py"
else
    echo "  ✗ FAIL: Closeout validation not found"
    exit 1
fi
echo ""

# Check 3: Verify serializer validation updated
echo "✓ Check 3: Verify PermitStatusUpdateSerializer enforces closeout"
if grep -q "validate_closeout_completion" app/backend/ptw/serializers.py; then
    echo "  ✓ PASS: Closeout validation integrated in serializer"
else
    echo "  ✗ FAIL: Closeout validation not integrated"
    exit 1
fi
echo ""

# Check 4: Verify closeout serializers exist
echo "✓ Check 4: Verify closeout serializers added"
if grep -q "class CloseoutChecklistTemplateSerializer" app/backend/ptw/serializers.py && \
   grep -q "class PermitCloseoutSerializer" app/backend/ptw/serializers.py; then
    echo "  ✓ PASS: Closeout serializers added"
else
    echo "  ✗ FAIL: Closeout serializers not found"
    exit 1
fi
echo ""

# Check 5: Verify closeout endpoints exist
echo "✓ Check 5: Verify closeout endpoints added"
if grep -q "def closeout" app/backend/ptw/views.py && \
   grep -q "def update_closeout" app/backend/ptw/views.py && \
   grep -q "def complete_closeout" app/backend/ptw/views.py; then
    echo "  ✓ PASS: Closeout endpoints added to views.py"
else
    echo "  ✗ FAIL: Closeout endpoints not found"
    exit 1
fi
echo ""

# Check 6: Verify migration exists
echo "✓ Check 6: Verify migration file exists"
if [ -f "app/backend/ptw/migrations/0005_closeout_checklist.py" ]; then
    echo "  ✓ PASS: Migration 0005_closeout_checklist.py exists"
else
    echo "  ✗ FAIL: Migration file not found"
    exit 1
fi
echo ""

# Check 7: Verify tests exist
echo "✓ Check 7: Verify closeout tests exist"
if [ -f "app/backend/ptw/tests/test_closeout.py" ]; then
    TEST_COUNT=$(grep -c "def test_" app/backend/ptw/tests/test_closeout.py || echo "0")
    echo "  ✓ PASS: test_closeout.py exists with $TEST_COUNT tests"
else
    echo "  ✗ FAIL: test_closeout.py not found"
    exit 1
fi
echo ""

# Check 8: Python syntax validation
echo "✓ Check 8: Python syntax validation"
if python3 -c "import ast; ast.parse(open('app/backend/ptw/models.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in models.py"
    exit 1
else
    echo "  ✓ PASS: models.py syntax valid"
fi

if python3 -c "import ast; ast.parse(open('app/backend/ptw/validators.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in validators.py"
    exit 1
else
    echo "  ✓ PASS: validators.py syntax valid"
fi

if python3 -c "import ast; ast.parse(open('app/backend/ptw/serializers.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in serializers.py"
    exit 1
else
    echo "  ✓ PASS: serializers.py syntax valid"
fi

if python3 -c "import ast; ast.parse(open('app/backend/ptw/views.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in views.py"
    exit 1
else
    echo "  ✓ PASS: views.py syntax valid"
fi

if python3 -c "import ast; ast.parse(open('app/backend/ptw/tests/test_closeout.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in test_closeout.py"
    exit 1
else
    echo "  ✓ PASS: test_closeout.py syntax valid"
fi
echo ""

echo "=========================================="
echo "✓ ALL PR7 VALIDATIONS PASSED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Closeout models added (CloseoutChecklistTemplate, PermitCloseout)"
echo "  - Closeout validation enforced on permit completion"
echo "  - Closeout serializers added"
echo "  - Closeout endpoints added (GET/POST closeout, complete)"
echo "  - Migration created (0005_closeout_checklist.py)"
echo "  - Tests created ($TEST_COUNT tests)"
echo "  - Python syntax valid"
echo ""
echo "Next Steps:"
echo "  1. Run migration: cd app/backend && python3 manage.py migrate"
echo "  2. Run tests: python3 manage.py test ptw.tests.test_closeout"
echo "  3. Create closeout templates via Django admin or API"
echo "  4. Test closeout workflow in UI"
echo ""
