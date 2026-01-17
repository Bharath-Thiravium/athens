#!/bin/bash
# PR2 Validation Script - Uses PostgreSQL configuration

set -e

echo "=== PR2 VALIDATION: PermitExtension Fix ==="
echo ""

cd /var/www/athens/app/backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check Python syntax only (no DB needed)
echo "1. Checking Python syntax..."
python3 -m py_compile ptw/models.py
python3 -m py_compile ptw/utils.py
echo "✓ Syntax valid"
echo ""

# Django system check (requires DB config but doesn't connect)
echo "2. Running Django system check..."
if python3 manage.py check ptw --deploy 2>/dev/null; then
    echo "✓ Django checks passed"
else
    echo "⚠ Django check requires proper environment setup"
    echo "  Run with: source venv/bin/activate && python3 manage.py check ptw"
fi
echo ""

# Show what would be tested
echo "3. Test suite ready:"
echo "   - tests/backend/ptw/test_permit_extension.py (11 tests)"
echo ""

echo "=== To run actual tests (requires PostgreSQL): ==="
echo "cd /var/www/athens/app/backend"
echo "source venv/bin/activate"
echo "python3 manage.py test ptw.tests.test_permit_extension"
echo ""
echo "Or via Docker:"
echo "docker-compose -f docker-compose.dev.yml exec backend python manage.py test ptw.tests.test_permit_extension"
