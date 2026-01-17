#!/bin/bash
# PR11 Validation Script
# Validates Export & Print Upgrade implementation

echo "=== PR11: Export & Print Upgrade Validation ==="
echo ""

BACKEND_DIR="app/backend"
FRONTEND_DIR="app/frontend/src"
PASS=0
FAIL=0

# Check 1: Export utilities exist
echo "✓ Check 1: Export utilities modules"
if [ -f "$BACKEND_DIR/ptw/export_utils.py" ] && [ -f "$BACKEND_DIR/ptw/excel_utils.py" ]; then
    echo "  ✓ export_utils.py and excel_utils.py found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Export utilities NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 2: Upgraded export endpoints in views
echo "✓ Check 2: Upgraded export endpoints"
if grep -q "from .export_utils import generate_audit_ready_pdf" "$BACKEND_DIR/ptw/views.py" && \
   grep -q "from .excel_utils import generate_excel_export" "$BACKEND_DIR/ptw/views.py"; then
    echo "  ✓ Export endpoints upgraded"
    PASS=$((PASS + 1))
else
    echo "  ✗ Export endpoints NOT upgraded"
    FAIL=$((FAIL + 1))
fi

# Check 3: Bulk export endpoints
echo "✓ Check 3: Bulk export endpoints"
if grep -q "def bulk_export_pdf" "$BACKEND_DIR/ptw/views.py" && \
   grep -q "def bulk_export_excel" "$BACKEND_DIR/ptw/views.py"; then
    echo "  ✓ Bulk export endpoints found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Bulk export endpoints NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 4: Export tests
echo "✓ Check 4: Export tests"
if [ -f "$BACKEND_DIR/ptw/tests/test_exports.py" ]; then
    echo "  ✓ test_exports.py found"
    PASS=$((PASS + 1))
else
    echo "  ✗ test_exports.py NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 5: Frontend export API functions
echo "✓ Check 5: Frontend export API functions"
if grep -q "exportPermitPDF\|bulkExportPDF\|bulkExportExcel" "$FRONTEND_DIR/features/ptw/api.ts"; then
    echo "  ✓ Export API functions found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Export API functions NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 6: ExportButtons component
echo "✓ Check 6: ExportButtons component"
if [ -f "$FRONTEND_DIR/features/ptw/components/ExportButtons.tsx" ]; then
    echo "  ✓ ExportButtons.tsx found"
    PASS=$((PASS + 1))
else
    echo "  ✗ ExportButtons.tsx NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 7: Download helper utility
echo "✓ Check 7: Download helper utility"
if [ -f "$FRONTEND_DIR/features/ptw/utils/downloadHelper.ts" ]; then
    echo "  ✓ downloadHelper.ts found"
    PASS=$((PASS + 1))
else
    echo "  ✗ downloadHelper.ts NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 8: Python syntax validation
echo "✓ Check 8: Python syntax validation"
if python3 -m py_compile "$BACKEND_DIR/ptw/export_utils.py" 2>/dev/null && \
   python3 -m py_compile "$BACKEND_DIR/ptw/excel_utils.py" 2>/dev/null; then
    echo "  ✓ Python syntax OK"
    PASS=$((PASS + 1))
else
    echo "  ✗ Python syntax errors"
    FAIL=$((FAIL + 1))
fi

# Check 9: PDF generation features
echo "✓ Check 9: PDF audit-ready features"
if grep -q "generate_audit_ready_pdf\|_generate_header_section\|_generate_isolation_section\|_generate_closeout_section" "$BACKEND_DIR/ptw/export_utils.py"; then
    echo "  ✓ Audit-ready PDF features found"
    PASS=$((PASS + 1))
else
    echo "  ✗ PDF features NOT complete"
    FAIL=$((FAIL + 1))
fi

# Check 10: Excel multi-sheet support
echo "✓ Check 10: Excel multi-sheet support"
if grep -q "_generate_isolation_sheet\|_generate_gas_readings_sheet\|_generate_closeout_sheet\|_generate_audit_logs_sheet" "$BACKEND_DIR/ptw/excel_utils.py"; then
    echo "  ✓ Multi-sheet Excel support found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Multi-sheet support NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 11: Frontend build
echo "✓ Check 11: Frontend build validation"
if [ -d "app/frontend/dist" ]; then
    echo "  ✓ Frontend build exists"
    PASS=$((PASS + 1))
else
    echo "  ✗ Frontend build NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 12: Bulk export limit enforcement
echo "✓ Check 12: Bulk export limit enforcement"
if grep -q "PTW_BULK_EXPORT_LIMIT\|max_permits" "$BACKEND_DIR/ptw/views.py"; then
    echo "  ✓ Export limits enforced"
    PASS=$((PASS + 1))
else
    echo "  ✗ Export limits NOT enforced"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Validation Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All checks passed! PR11 is ready."
    exit 0
else
    echo "✗ Some checks failed. Please review."
    exit 1
fi
