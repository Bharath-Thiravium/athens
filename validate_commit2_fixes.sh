#!/bin/bash
# Validation for Commit 2 fixes

echo "========================================"
echo "Commit 2 Fixes Validation"
echo "========================================"
echo ""

PASS=0
FAIL=0

echo "[1/3] Checking Python syntax for permissions.py..."
if python3 -m py_compile app/backend/ptw/permissions.py 2>/dev/null; then
    echo "✅ Python syntax valid"
    ((PASS++))
else
    echo "❌ Python syntax error"
    ((FAIL++))
fi

echo "[2/3] Checking for remaining .usertype references..."
if grep -q "\.usertype" app/backend/ptw/permissions.py 2>/dev/null; then
    USERTYPE_COUNT=$(grep -c "\.usertype" app/backend/ptw/permissions.py)
    echo "❌ Found $USERTYPE_COUNT .usertype references"
    ((FAIL++))
else
    echo "✅ No .usertype references found (all fixed)"
    ((PASS++))
fi

echo "[3/3] Checking for admin_type usage..."
ADMIN_TYPE_COUNT=$(grep -c "\.admin_type" app/backend/ptw/permissions.py 2>/dev/null || echo "0")
if [ "$ADMIN_TYPE_COUNT" -gt "0" ]; then
    echo "✅ Found $ADMIN_TYPE_COUNT .admin_type references (correct)"
    ((PASS++))
else
    echo "❌ No .admin_type references found"
    ((FAIL++))
fi

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo "Passed: $PASS/3"
echo "Failed: $FAIL/3"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    echo ""
    echo "Commit 2 fixes complete!"
    echo "All usertype → admin_type references fixed."
    exit 0
else
    echo "❌ SOME CHECKS FAILED"
    exit 1
fi
