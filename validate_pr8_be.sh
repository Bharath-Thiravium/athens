#!/bin/bash
# PR8 Validation Script - Isolation Points Management

echo "========================================="
echo "PR8 - Isolation Points Management"
echo "Validation Script"
echo "========================================="
echo ""

cd /var/www/athens/app/backend

# Check 1: Models exist
echo "[1/8] Checking models..."
if grep -q "class IsolationPointLibrary" ptw/models.py && \
   grep -q "class PermitIsolationPoint" ptw/models.py && \
   grep -q "requires_structured_isolation" ptw/models.py; then
    echo "✓ Models added: IsolationPointLibrary, PermitIsolationPoint, PermitType flags"
else
    echo "✗ Models missing"
    exit 1
fi

# Check 2: Validators exist
echo "[2/8] Checking validators..."
if grep -q "validate_structured_isolation" ptw/validators.py && \
   grep -q "validate_deisolation_completion" ptw/validators.py; then
    echo "✓ Validators added: validate_structured_isolation, validate_deisolation_completion"
else
    echo "✗ Validators missing"
    exit 1
fi

# Check 3: Serializers exist
echo "[3/8] Checking serializers..."
if grep -q "IsolationPointLibrarySerializer" ptw/serializers.py && \
   grep -q "PermitIsolationPointSerializer" ptw/serializers.py; then
    echo "✓ Serializers added"
else
    echo "✗ Serializers missing"
    exit 1
fi

# Check 4: Views/endpoints exist
echo "[4/8] Checking views..."
if grep -q "def isolation" ptw/views.py && \
   grep -q "def assign_isolation" ptw/views.py && \
   grep -q "def update_isolation" ptw/views.py && \
   grep -q "IsolationPointLibraryViewSet" ptw/views.py; then
    echo "✓ Views added: isolation, assign_isolation, update_isolation, IsolationPointLibraryViewSet"
else
    echo "✗ Views missing"
    exit 1
fi

# Check 5: URLs registered
echo "[5/8] Checking URLs..."
if grep -q "isolation-points" ptw/urls.py && \
   grep -q "permit-isolation-points" ptw/urls.py; then
    echo "✓ URLs registered"
else
    echo "✗ URLs missing"
    exit 1
fi

# Check 6: Admin registered
echo "[6/8] Checking admin..."
if grep -q "IsolationPointLibraryAdmin" ptw/admin.py && \
   grep -q "PermitIsolationPointAdmin" ptw/admin.py; then
    echo "✓ Admin registered"
else
    echo "✗ Admin missing"
    exit 1
fi

# Check 7: Migration exists
echo "[7/8] Checking migration..."
if [ -f "ptw/migrations/0006_isolation_points.py" ]; then
    echo "✓ Migration file exists: 0006_isolation_points.py"
else
    echo "✗ Migration file missing"
    exit 1
fi

# Check 8: Tests exist
echo "[8/8] Checking tests..."
if [ -f "ptw/tests/test_isolation_points.py" ]; then
    echo "✓ Test file exists: test_isolation_points.py"
else
    echo "✗ Test file missing"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ All PR8 backend validations passed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run migration: python3 manage.py migrate"
echo "2. Run tests: python3 manage.py test ptw.tests.test_isolation_points"
echo "3. Check Django admin: python3 manage.py check ptw"
echo "4. Implement frontend UI"
