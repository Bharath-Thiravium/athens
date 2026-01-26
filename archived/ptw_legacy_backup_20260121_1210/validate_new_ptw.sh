#!/bin/bash
# PTW Implementation Validation Script

echo "=== PTW Implementation Validation ==="

# Backend validation
echo "1. Django system check..."
cd /var/www/athens/app/backend
source venv/bin/activate
python manage.py check
if [ $? -ne 0 ]; then
    echo "✗ Django check failed"
    exit 1
fi
echo "✓ Django check passed"

# PTW tests
echo "2. PTW module tests..."
python manage.py test ptw.tests --verbosity=1
if [ $? -ne 0 ]; then
    echo "✗ PTW tests failed"
    exit 1
fi
echo "✓ PTW tests passed"

# Frontend build
echo "3. Frontend build test..."
cd /var/www/athens/app/frontend
if [ -f package.json ]; then
    npm run build
    if [ $? -ne 0 ]; then
        echo "✗ Frontend build failed"
        exit 1
    fi
    echo "✓ Frontend build passed"
else
    echo "⚠ Frontend package.json not found, skipping build test"
fi

echo "✓ All PTW validation checks passed"