#!/bin/bash
set -e

echo "PTW Validation Script"
echo "===================="

# Backend validation
echo "1. Django check..."
cd /var/www/athens/app/backend
python3 manage.py check --deploy

echo "2. PTW migrations check..."
python3 manage.py makemigrations --dry-run --check

echo "3. PTW tests..."
if [ -d "ptw/tests" ] || [ -f "ptw/tests.py" ]; then
    python3 manage.py test ptw.tests
else
    echo "No PTW tests found, skipping..."
fi

# Frontend validation
echo "4. Frontend build..."
cd /var/www/athens/app/frontend
npm run build

echo "5. TypeScript check..."
npx tsc --noEmit

echo "All validations passed!"
exit 0