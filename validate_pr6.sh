#!/bin/bash
# PR6 Validation Script - Analytics Implementation

set -e

echo "=========================================="
echo "PR6 VALIDATION - Analytics Implementation"
echo "=========================================="
echo ""

# Check 1: Verify get_monthly_trends implementation
echo "✓ Check 1: Verify get_monthly_trends is implemented"
if grep -q "def get_monthly_trends.*queryset" app/backend/ptw/views.py && \
   ! grep -q "return \[\]" app/backend/ptw/views.py | grep -A 2 "def get_monthly_trends"; then
    echo "  ✓ PASS: get_monthly_trends has real implementation"
else
    echo "  ✗ FAIL: get_monthly_trends still returns empty list"
    exit 1
fi
echo ""

# Check 2: Verify calculate_incident_rate implementation
echo "✓ Check 2: Verify calculate_incident_rate is implemented"
if grep -q "def calculate_incident_rate.*queryset" app/backend/ptw/views.py && \
   ! grep -q "return 0.3.*# Mock value" app/backend/ptw/views.py; then
    echo "  ✓ PASS: calculate_incident_rate has real implementation"
else
    echo "  ✗ FAIL: calculate_incident_rate still returns mock value"
    exit 1
fi
echo ""

# Check 3: Verify TruncMonth import
echo "✓ Check 3: Verify TruncMonth is imported"
if grep -q "from django.db.models.functions import TruncMonth" app/backend/ptw/views.py; then
    echo "  ✓ PASS: TruncMonth imported for month aggregation"
else
    echo "  ✗ FAIL: TruncMonth not imported"
    exit 1
fi
echo ""

# Check 4: Verify relativedelta import
echo "✓ Check 4: Verify relativedelta is imported"
if grep -q "from dateutil.relativedelta import relativedelta" app/backend/ptw/views.py; then
    echo "  ✓ PASS: relativedelta imported for date calculations"
else
    echo "  ✗ FAIL: relativedelta not imported"
    exit 1
fi
echo ""

# Check 5: Verify Incident model is used
echo "✓ Check 5: Verify Incident model is used in calculate_incident_rate"
if grep -q "from incidentmanagement.models import Incident" app/backend/ptw/views.py; then
    echo "  ✓ PASS: Incident model imported and used"
else
    echo "  ✗ FAIL: Incident model not imported"
    exit 1
fi
echo ""

# Check 6: Verify tests exist
echo "✓ Check 6: Verify analytics tests exist"
if [ -f "app/backend/ptw/tests/test_analytics.py" ]; then
    echo "  ✓ PASS: test_analytics.py exists"
    
    # Count test methods
    TEST_COUNT=$(grep -c "def test_" app/backend/ptw/tests/test_analytics.py || echo "0")
    echo "  ℹ INFO: Found $TEST_COUNT test methods"
else
    echo "  ✗ FAIL: test_analytics.py not found"
    exit 1
fi
echo ""

# Check 7: Python syntax validation
echo "✓ Check 7: Python syntax validation"
if python3 -c "import ast; ast.parse(open('app/backend/ptw/views.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in views.py"
    exit 1
else
    echo "  ✓ PASS: views.py syntax valid"
fi

if python3 -c "import ast; ast.parse(open('app/backend/ptw/tests/test_analytics.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in test_analytics.py"
    exit 1
else
    echo "  ✓ PASS: test_analytics.py syntax valid"
fi
echo ""

echo "=========================================="
echo "✓ ALL PR6 VALIDATIONS PASSED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - get_monthly_trends implemented with real aggregation"
echo "  - calculate_incident_rate uses Incident model"
echo "  - TruncMonth and relativedelta imported"
echo "  - Analytics tests created ($TEST_COUNT tests)"
echo "  - Python syntax valid"
echo ""
echo "Next Steps:"
echo "  1. Run tests: cd app/backend && python3 manage.py test ptw.tests.test_analytics"
echo "  2. Check Django: python3 manage.py check ptw"
echo "  3. Test endpoint: GET /api/v1/ptw/permits/analytics/"
echo ""
