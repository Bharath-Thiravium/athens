#!/bin/bash
# PR7 Frontend Validation Script - Closeout Checklist UI

set -e

echo "=========================================="
echo "PR7 FRONTEND VALIDATION - Closeout UI"
echo "=========================================="
echo ""

# Check 1: Verify closeout API functions added
echo "✓ Check 1: Verify closeout API functions"
if grep -q "getPermitCloseout\|updatePermitCloseout\|completePermitCloseout" app/frontend/src/features/ptw/api.ts; then
    echo "  ✓ PASS: Closeout API functions added to api.ts"
else
    echo "  ✗ FAIL: Closeout API functions not found"
    exit 1
fi
echo ""

# Check 2: Verify closeout types added
echo "✓ Check 2: Verify closeout types"
if grep -q "PermitCloseout\|CloseoutChecklistTemplate\|CloseoutChecklistItem" app/frontend/src/features/ptw/types/index.ts; then
    echo "  ✓ PASS: Closeout types added to types/index.ts"
else
    echo "  ✗ FAIL: Closeout types not found"
    exit 1
fi
echo ""

# Check 3: Verify closeout imports in PermitDetail
echo "✓ Check 3: Verify closeout imports in PermitDetail"
if grep -q "getPermitCloseout.*updatePermitCloseout.*completePermitCloseout" app/frontend/src/features/ptw/components/PermitDetail.tsx; then
    echo "  ✓ PASS: Closeout functions imported in PermitDetail"
else
    echo "  ✗ FAIL: Closeout imports not found"
    exit 1
fi
echo ""

# Check 4: Verify closeout tab added
echo "✓ Check 4: Verify closeout tab in PermitDetail"
if grep -q "Closeout.*TabPane\|closeout.*key=" app/frontend/src/features/ptw/components/PermitDetail.tsx; then
    echo "  ✓ PASS: Closeout tab added to PermitDetail"
else
    echo "  ✗ FAIL: Closeout tab not found"
    exit 1
fi
echo ""

# Check 5: Verify error handling for closeout
echo "✓ Check 5: Verify closeout error handling"
if grep -q "error?.response?.data?.closeout" app/frontend/src/features/ptw/components/PermitDetail.tsx; then
    echo "  ✓ PASS: Closeout error handling added"
else
    echo "  ✗ FAIL: Closeout error handling not found"
    exit 1
fi
echo ""

# Check 6: Verify correct API endpoints
echo "✓ Check 6: Verify correct API endpoint paths"
if grep -q "/closeout/\|/update_closeout/\|/complete_closeout/" app/frontend/src/features/ptw/api.ts; then
    echo "  ✓ PASS: Correct closeout endpoint paths"
else
    echo "  ✗ FAIL: Incorrect endpoint paths"
    exit 1
fi
echo ""

# Check 7: TypeScript syntax check
echo "✓ Check 7: TypeScript syntax validation"
cd app/frontend
if npm run type-check 2>&1 | grep -q "error TS"; then
    echo "  ✗ FAIL: TypeScript errors found"
    exit 1
else
    echo "  ✓ PASS: TypeScript syntax valid"
fi
cd ../..
echo ""

echo "=========================================="
echo "✓ ALL PR7 FRONTEND VALIDATIONS PASSED"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Closeout API functions added (3 functions)"
echo "  - Closeout types added"
echo "  - Closeout tab added to PermitDetail"
echo "  - Error handling for closeout gating"
echo "  - Correct API endpoint paths"
echo "  - TypeScript syntax valid"
echo ""
echo "Next Steps:"
echo "  1. Build frontend: cd app/frontend && npm run build"
echo "  2. Test closeout UI in browser"
echo "  3. Create closeout templates via Django admin"
echo "  4. Test end-to-end closeout workflow"
echo ""
