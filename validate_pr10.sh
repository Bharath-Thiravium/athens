#!/bin/bash
# PR10 Validation Script
# Validates KPI Dashboard + Overdue/SLA Alerts implementation

echo "=== PR10: KPI Dashboard + Overdue/SLA Alerts Validation ==="
echo ""

BACKEND_DIR="app/backend"
FRONTEND_DIR="app/frontend/src"
PASS=0
FAIL=0

# Check 1: KPI utilities module exists
echo "✓ Check 1: KPI utilities module"
if [ -f "$BACKEND_DIR/ptw/kpi_utils.py" ]; then
    echo "  ✓ kpi_utils.py found"
    PASS=$((PASS + 1))
else
    echo "  ✗ kpi_utils.py NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 2: KPI endpoint added to views
echo "✓ Check 2: KPI endpoint in views"
if grep -q "def kpis" "$BACKEND_DIR/ptw/views.py"; then
    echo "  ✓ KPI endpoint found"
    PASS=$((PASS + 1))
else
    echo "  ✗ KPI endpoint NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 3: KPI tests exist
echo "✓ Check 3: KPI tests"
if [ -f "$BACKEND_DIR/ptw/tests/test_kpis.py" ]; then
    echo "  ✓ test_kpis.py found"
    PASS=$((PASS + 1))
else
    echo "  ✗ test_kpis.py NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 4: Frontend KPI API function
echo "✓ Check 4: Frontend KPI API function"
if grep -q "getKPIs" "$FRONTEND_DIR/features/ptw/api.ts"; then
    echo "  ✓ getKPIs function found"
    PASS=$((PASS + 1))
else
    echo "  ✗ getKPIs function NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 5: PTWKPIDashboard component
echo "✓ Check 5: PTWKPIDashboard component"
if [ -f "$FRONTEND_DIR/features/ptw/components/PTWKPIDashboard.tsx" ]; then
    echo "  ✓ PTWKPIDashboard.tsx found"
    PASS=$((PASS + 1))
else
    echo "  ✗ PTWKPIDashboard.tsx NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 6: Route added
echo "✓ Check 6: KPI dashboard route"
if grep -q "PTWKPIDashboard" "$FRONTEND_DIR/features/ptw/routes.tsx"; then
    echo "  ✓ Route found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Route NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 7: Overdue logic implemented
echo "✓ Check 7: Overdue calculation logic"
if grep -q "calculate_overdue_stats" "$BACKEND_DIR/ptw/kpi_utils.py"; then
    echo "  ✓ Overdue logic found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Overdue logic NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 8: Expiring soon logic
echo "✓ Check 8: Expiring soon logic"
if grep -q "get_expiring_soon_permits" "$BACKEND_DIR/ptw/kpi_utils.py"; then
    echo "  ✓ Expiring soon logic found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Expiring soon logic NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 9: Isolation pending logic
echo "✓ Check 9: Isolation pending logic"
if grep -q "get_isolation_pending_count" "$BACKEND_DIR/ptw/kpi_utils.py"; then
    echo "  ✓ Isolation pending logic found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Isolation pending logic NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 10: Closeout pending logic
echo "✓ Check 10: Closeout pending logic"
if grep -q "get_closeout_pending_count" "$BACKEND_DIR/ptw/kpi_utils.py"; then
    echo "  ✓ Closeout pending logic found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Closeout pending logic NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 11: Python syntax
echo "✓ Check 11: Python syntax validation"
if python3 -m py_compile "$BACKEND_DIR/ptw/kpi_utils.py" 2>/dev/null; then
    echo "  ✓ kpi_utils.py syntax OK"
    PASS=$((PASS + 1))
else
    echo "  ✗ kpi_utils.py syntax error"
    FAIL=$((FAIL + 1))
fi

# Check 12: Frontend build
echo "✓ Check 12: Frontend build validation"
if [ -d "app/frontend/dist" ]; then
    echo "  ✓ Frontend build exists"
    PASS=$((PASS + 1))
else
    echo "  ✗ Frontend build NOT found"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Validation Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All checks passed! PR10 is ready."
    exit 0
else
    echo "✗ Some checks failed. Please review."
    exit 1
fi
