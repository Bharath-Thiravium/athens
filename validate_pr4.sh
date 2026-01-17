#!/bin/bash
# PR4 Validation Script - API Contract Alignment

set -e

echo "=== PR4 VALIDATION: API Contract Alignment ==="
echo ""

cd /var/www/athens

# Check for removed endpoints
echo "1. Checking for removed endpoints..."
REMOVED_COUNT=$(grep -rn "/start/\|/complete/\|/close/\|submit_for_approval\|submit_for_verification\|reject_verification" app/frontend/src/features/ptw/ 2>/dev/null | grep -v "node_modules" | wc -l)

if [ "$REMOVED_COUNT" -eq 0 ]; then
    echo "✓ No problematic endpoints found"
else
    echo "✗ Found $REMOVED_COUNT problematic endpoint references"
    grep -rn "/start/\|/complete/\|/close/\|submit_for_approval\|submit_for_verification\|reject_verification" app/frontend/src/features/ptw/ 2>/dev/null | grep -v "node_modules"
    exit 1
fi
echo ""

# Check for incorrect base paths
echo "2. Checking for incorrect base paths..."
INCORRECT_PATHS=$(grep -rn "'/api/permits'" app/frontend/src/features/ptw/ 2>/dev/null | grep -v "node_modules" | wc -l)

if [ "$INCORRECT_PATHS" -eq 0 ]; then
    echo "✓ No incorrect base paths found"
else
    echo "✗ Found $INCORRECT_PATHS incorrect base path references"
    grep -rn "'/api/permits'" app/frontend/src/features/ptw/ 2>/dev/null | grep -v "node_modules"
    exit 1
fi
echo ""

# Check backend
echo "3. Running backend system check..."
cd app/backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi

if python3 manage.py check ptw 2>&1 | grep -q "System check identified no issues"; then
    echo "✓ Backend checks passed"
else
    echo "✗ Backend checks failed"
    python3 manage.py check ptw
    exit 1
fi
echo ""

# Summary
echo "=== PR4 Validation Summary ==="
echo "✓ All non-existent endpoints removed"
echo "✓ All base paths corrected to /api/v1/ptw/"
echo "✓ Backend system check passed"
echo ""
echo "Files modified:"
echo "  - app/frontend/src/features/ptw/api.ts"
echo "  - app/frontend/src/features/ptw/hooks/useOfflineSync.ts"
echo "  - app/frontend/src/features/ptw/components/MobilePermitView.tsx"
echo "  - app/frontend/src/features/ptw/utils/ptwConstants.ts"
echo "  - app/frontend/src/features/ptw/components/IntegrationHub.tsx"
echo ""
echo "Ready for frontend build test:"
echo "  cd /var/www/athens/app/frontend && npm run build"
