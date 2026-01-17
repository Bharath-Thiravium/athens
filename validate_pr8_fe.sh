#!/bin/bash
# PR8 Frontend Validation Script - Isolation Points Management

echo "========================================="
echo "PR8 Frontend - Isolation Points Management"
echo "Validation Script"
echo "========================================="
echo ""

cd /var/www/athens/app/frontend

# Check 1: API functions added
echo "[1/6] Checking API functions..."
if grep -q "listIsolationPoints\|getPermitIsolation\|assignPermitIsolation\|updatePermitIsolation" src/features/ptw/api.ts; then
    echo "✓ Isolation API functions added"
else
    echo "✗ Isolation API functions missing"
    exit 1
fi

# Check 2: TypeScript types added
echo "[2/6] Checking TypeScript types..."
if grep -q "IsolationPointLibrary\|PermitIsolationPoint\|PermitIsolationResponse" src/features/ptw/types/index.ts; then
    echo "✓ Isolation types added"
else
    echo "✗ Isolation types missing"
    exit 1
fi

# Check 3: PermitDetail imports
echo "[3/6] Checking PermitDetail imports..."
if grep -q "getPermitIsolation\|assignPermitIsolation\|updatePermitIsolation" src/features/ptw/components/PermitDetail.tsx; then
    echo "✓ Isolation imports added to PermitDetail"
else
    echo "✗ Isolation imports missing from PermitDetail"
    exit 1
fi

# Check 4: Isolation state variables
echo "[4/6] Checking isolation state..."
if grep -q "isolation.*useState\|isolationLoading\|libraryPoints\|activeTabKey" src/features/ptw/components/PermitDetail.tsx; then
    echo "✓ Isolation state variables added"
else
    echo "✗ Isolation state variables missing"
    exit 1
fi

# Check 5: Isolation tab in UI
echo "[5/6] Checking Isolation tab..."
if grep -q "key=\"isolation\"\|fetchIsolation\|handleAssignLibraryPoint\|handleIsolationAction" src/features/ptw/components/PermitDetail.tsx; then
    echo "✓ Isolation tab and handlers added"
else
    echo "✗ Isolation tab missing"
    exit 1
fi

# Check 6: Error handling for gating
echo "[6/6] Checking error handling..."
if grep -q "error\.response\.data\.isolation\|setActiveTabKey.*isolation" src/features/ptw/components/PermitDetail.tsx; then
    echo "✓ Isolation error handling added"
else
    echo "✗ Isolation error handling missing"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ All PR8 frontend validations passed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Build frontend: npm run build"
echo "2. Test in browser with structured isolation enabled"
echo "3. Verify error routing to Isolation tab on gating"
