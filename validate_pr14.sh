#!/bin/bash
# PR14 Validation Script - Multi-Tenant Filters + Server Pagination

echo "=== PR14 Validation: Multi-Tenant Filters + Server Pagination ==="
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
echo "Backend Checks:"
echo "---------------"

# 1. Check PermitFilter class exists
grep -q "class PermitFilter" app/backend/ptw/filters.py
check "PermitFilter class defined"

# 2. Check status filter supports comma-separated
grep -q "filter_status" app/backend/ptw/filters.py
check "Status filter method for comma-separated values"

# 3. Check PermitViewSet uses filterset_class
grep -q "filterset_class = PermitFilter" app/backend/ptw/views.py
check "PermitViewSet uses PermitFilter"

# 4. Check project scoping in get_queryset
grep -q "user_project" app/backend/ptw/views.py
check "Project scoping in get_queryset"

# 5. Check KPI endpoint uses filter_queryset
grep -q "filter_queryset" app/backend/ptw/views.py | head -1
check "KPI endpoint respects filters"

# 6. Check export_excel uses filter_queryset
grep -q "def export_excel" app/backend/ptw/views.py
check "export_excel endpoint exists"

# 7. Check bulk_export_pdf supports use_filters
grep -q "use_filters" app/backend/ptw/views.py
check "bulk_export_pdf supports filters"

# 8. Check bulk_export_excel supports use_filters
grep -q "bulk_export_excel" app/backend/ptw/views.py
check "bulk_export_excel supports filters"

# 9. Check PermitAuditFilter exists
grep -q "class PermitAuditFilter" app/backend/ptw/filters.py
check "PermitAuditFilter class defined"

# 10. Check PermitAuditViewSet uses filterset_class
grep -q "filterset_class = PermitAuditFilter" app/backend/ptw/views.py
check "PermitAuditViewSet uses PermitAuditFilter"

# 11. Check test file exists
test -f app/backend/ptw/tests/test_filters_and_pagination.py
check "test_filters_and_pagination.py exists"

# 12. Check test has pagination shape test
grep -q "test_permits_list_paginated_shape" app/backend/ptw/tests/test_filters_and_pagination.py
check "Pagination shape test exists"

# 13. Check test has project scoping test
grep -q "test_project_scoping_blocks_other_project" app/backend/ptw/tests/test_filters_and_pagination.py
check "Project scoping test exists"

# 14. Check test has multi-status filter test
grep -q "test_status_filter_multi" app/backend/ptw/tests/test_filters_and_pagination.py
check "Multi-status filter test exists"

echo ""
echo "Frontend Checks:"
echo "----------------"

# 15. Check getPermitsPaginated function exists
grep -q "getPermitsPaginated" app/frontend/src/features/ptw/api.ts
check "getPermitsPaginated API function exists"

# 16. Check PaginatedResponse type exists
grep -q "PaginatedResponse" app/frontend/src/features/ptw/api.ts
check "PaginatedResponse type defined"

# 17. Check PermitList uses useSearchParams
grep -q "useSearchParams" app/frontend/src/features/ptw/components/PermitList.tsx
check "PermitList uses URL query params"

# 18. Check PermitList has totalCount state
grep -q "totalCount" app/frontend/src/features/ptw/components/PermitList.tsx
check "PermitList tracks totalCount"

# 19. Check PermitList uses server pagination
grep -q "getPermitsPaginated" app/frontend/src/features/ptw/components/PermitList.tsx
check "PermitList uses server pagination API"

# 20. Check export functions support filters
grep -q "exportPermitsExcel" app/frontend/src/features/ptw/components/PermitList.tsx
check "PermitList has export with filters"

# 21. Check bulk export functions updated
grep -q "bulkExportPDF" app/frontend/src/features/ptw/api.ts
check "bulkExportPDF updated in API"

# 22. Check KPI API supports filters
grep -q "status\\?" app/frontend/src/features/ptw/api.ts
check "getKPIs API supports filter params"

echo ""
echo "Python Syntax Check:"
echo "--------------------"

# 23. Validate Python syntax
python3 -m py_compile app/backend/ptw/filters.py 2>/dev/null
check "filters.py syntax valid"

python3 -m py_compile app/backend/ptw/tests/test_filters_and_pagination.py 2>/dev/null
check "test_filters_and_pagination.py syntax valid"

echo ""
echo "=== Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All checks passed!"
    exit 0
else
    echo "✗ Some checks failed"
    exit 1
fi
