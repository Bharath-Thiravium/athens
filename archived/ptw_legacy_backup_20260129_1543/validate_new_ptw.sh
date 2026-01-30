#!/bin/bash
set -e

ATHENS_ROOT="/var/www/athens"

echo "Validating new PTW implementation..."

# Backend validation
echo "Validating backend..."
cd "$ATHENS_ROOT/app/backend"
source venv/bin/activate
python manage.py check
python manage.py test ptw.tests --verbosity=2

# Frontend validation
echo "Validating frontend..."
cd "$ATHENS_ROOT/app/frontend"
npm run build

echo "PTW validation complete - all checks passed!"