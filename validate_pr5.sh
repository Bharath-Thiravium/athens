#!/bin/bash
# PR5 Validation Script - Frontend Data Shape + Links + Audit Log Naming

set -e

echo "=========================================="
echo "PR5 VALIDATION - Frontend Data Shape Fix"
echo "=========================================="
echo ""

# Check 1: Verify no broken PTW route links remain
echo "✓ Check 1: Verify no broken /ptw/permits/ route links (excluding API endpoints)"
BROKEN_LINKS=$(grep -rn "/ptw/permits/" app/frontend/src/features/ptw --include="*.tsx" --include="*.ts" 2>/dev/null | grep -v "api/v1/ptw/permits" | grep -v "PERMITS:" | grep -v "url:" || true)
if [ -z "$BROKEN_LINKS" ]; then
    echo "  ✓ PASS: No broken route links found"
else
    echo "  ✗ FAIL: Found broken route links:"
    echo "$BROKEN_LINKS"
    exit 1
fi
echo ""

# Check 2: Verify correct route usage
echo "✓ Check 2: Verify /dashboard/ptw/view/ route is used"
CORRECT_ROUTES=$(grep -rn "/dashboard/ptw/view/" app/frontend/src/features/ptw --include="*.tsx" --include="*.ts" 2>/dev/null | wc -l)
if [ "$CORRECT_ROUTES" -gt 0 ]; then
    echo "  ✓ PASS: Found $CORRECT_ROUTES usages of correct route"
else
    echo "  ✗ FAIL: No correct route usages found"
    exit 1
fi
echo ""

# Check 3: Verify backend serializer has alias fields
echo "✓ Check 3: Verify UserMinimalSerializer has alias fields"
if grep -q "first_name = serializers.CharField(source='name'" app/backend/ptw/serializers.py && \
   grep -q "last_name = serializers.CharField(source='surname'" app/backend/ptw/serializers.py && \
   grep -q "usertype = serializers.CharField(source='user_type'" app/backend/ptw/serializers.py; then
    echo "  ✓ PASS: UserMinimalSerializer has first_name, last_name, usertype aliases"
else
    echo "  ✗ FAIL: UserMinimalSerializer missing alias fields"
    exit 1
fi
echo ""

# Check 4: Verify audit_trail alias exists
echo "✓ Check 4: Verify PermitSerializer has audit_trail alias"
if grep -q "audit_trail = PermitAuditSerializer.*source='audit_logs'" app/backend/ptw/serializers.py; then
    echo "  ✓ PASS: PermitSerializer has audit_trail alias for audit_logs"
else
    echo "  ✗ FAIL: PermitSerializer missing audit_trail alias"
    exit 1
fi
echo ""

# Check 5: Python syntax check
echo "✓ Check 5: Python syntax validation"
if python3 -c "import ast; ast.parse(open('app/backend/ptw/serializers.py').read())" 2>&1 | grep -q "SyntaxError"; then
    echo "  ✗ FAIL: Syntax errors in serializers.py"
    exit 1
else
    echo "  ✓ PASS: Serializers syntax valid"
fi
echo ""

# Check 6: Frontend build check (optional)
echo "✓ Check 6: Frontend TypeScript check (optional)"
if [ -d "app/frontend" ]; then
    echo "  ℹ INFO: Frontend build skipped (run 'npm run build' manually to verify)"
else
    echo "  ℹ INFO: Frontend directory not found"
fi
echo ""

echo "=========================================="
echo "✓ ALL PR5 VALIDATIONS PASSED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - No broken /ptw/permits/ route links"
echo "  - Correct /dashboard/ptw/view/ routes in use"
echo "  - UserMinimalSerializer has first_name, last_name, usertype aliases"
echo "  - PermitSerializer has audit_trail alias"
echo "  - Python syntax validation passed"
echo ""
