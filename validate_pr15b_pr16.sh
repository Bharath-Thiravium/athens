#!/bin/bash
# Final validation script for PR15.B + PR16

echo "=== PR15.B + PR16 Validation ==="
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

# Backend checks
echo "Backend Validation:"
echo "-------------------"

# Check readiness files exist
test -f app/backend/ptw/readiness.py
check "readiness.py exists"

test -f app/backend/ptw/report_utils.py
check "report_utils.py exists"

test -f app/backend/ptw/tests/test_readiness_endpoint.py
check "test_readiness_endpoint.py exists"

test -f app/backend/ptw/tests/test_reports.py
check "test_reports.py exists"

# Check Python syntax
python3 -m py_compile app/backend/ptw/readiness.py 2>/dev/null
check "readiness.py syntax valid"

python3 -m py_compile app/backend/ptw/report_utils.py 2>/dev/null
check "report_utils.py syntax valid"

# Check endpoints exist in views
grep -q "def readiness" app/backend/ptw/views.py
check "readiness endpoint in views.py"

grep -q "def reports_summary" app/backend/ptw/views.py
check "reports_summary endpoint in views.py"

grep -q "def reports_exceptions" app/backend/ptw/views.py
check "reports_exceptions endpoint in views.py"

echo ""
echo "Frontend Validation:"
echo "--------------------"

# Check frontend files exist
test -f app/frontend/src/features/ptw/components/ReadinessPanel.tsx
check "ReadinessPanel.tsx exists"

test -f app/frontend/src/features/ptw/components/PTWReports.tsx
check "PTWReports.tsx exists"

# Check API functions added
grep -q "getPermitReadiness" app/frontend/src/features/ptw/api.ts
check "getPermitReadiness in api.ts"

grep -q "getReportsSummary" app/frontend/src/features/ptw/api.ts
check "getReportsSummary in api.ts"

grep -q "getReportsExceptions" app/frontend/src/features/ptw/api.ts
check "getReportsExceptions in api.ts"

# Check routes
grep -q "PTWReports" app/frontend/src/features/ptw/routes.tsx
check "PTWReports imported in routes"

grep -q 'path="reports"' app/frontend/src/features/ptw/routes.tsx
check "reports route defined"

# Check PermitDetail integration
grep -q "ReadinessPanel" app/frontend/src/features/ptw/components/PermitDetail.tsx
check "ReadinessPanel integrated in PermitDetail"

echo ""
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All validation checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Run backend tests: cd app/backend && python manage.py test ptw.tests.test_readiness_endpoint ptw.tests.test_reports"
    echo "2. Build frontend: cd app/frontend && npm run build"
    echo "3. Deploy to staging"
    exit 0
else
    echo "✗ Some validation checks failed"
    exit 1
fi
