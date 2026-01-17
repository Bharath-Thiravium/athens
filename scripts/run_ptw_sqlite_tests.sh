#!/bin/bash
# Run PTW tests using SQLite (no PostgreSQL socket required)
set -e

export DJANGO_SETTINGS_MODULE=backend.settings_sqlite_ci
export SECRET_KEY=test-key-for-ci

cd /var/www/athens/app/backend

echo "=========================================="
echo "PTW SQLite CI Test Suite"
echo "=========================================="
echo ""

echo "[1/4] Django system check..."
python3 manage.py check
echo "✓ Check passed"
echo ""

echo "[2/4] Running migrations..."
python3 manage.py migrate --noinput
echo "✓ Migrations applied"
echo ""

echo "[3/4] Running PTW tests..."
python3 manage.py test \
    ptw.tests.test_tbt \
    ptw.tests.test_signature_mapping \
    --verbosity=2
echo ""

echo "[4/4] Complete"
echo "=========================================="
