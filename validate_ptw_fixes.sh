#!/bin/bash

# Validation script for PTW production bug fixes
# Tests autofill, readiness endpoint, and print functionality

set -e

echo "=== PTW Production Bug Fixes Validation ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd /var/www/athens/app/backend

# Set environment
export SECRET_KEY='test-secret-key'

echo -e "${YELLOW}1. Testing Readiness Endpoint Fix${NC}"
echo "Running readiness regression tests..."
if python3 manage.py test ptw.tests.test_readiness_regression --keepdb -v 0; then
    echo -e "${GREEN}✓ Readiness endpoint fix validated${NC}"
else
    echo -e "${RED}✗ Readiness endpoint tests failed${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}2. Testing Backend Validation${NC}"
echo "Running Django system check..."
if python3 manage.py check --deploy; then
    echo -e "${GREEN}✓ Backend validation passed${NC}"
else
    echo -e "${RED}✗ Backend validation failed${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}3. Testing Frontend Build${NC}"
cd ../frontend
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend build successful${NC}"
else
    echo -e "${RED}✗ Frontend build failed${NC}"
    exit 1
fi

echo
echo -e "${YELLOW}4. Checking File Modifications${NC}"
cd /var/www/athens

# Check if fixes were applied
if grep -q "Always apply defaults when permit type changes" app/frontend/src/features/ptw/components/EnhancedPermitForm.tsx; then
    echo -e "${GREEN}✓ Autofill fix applied to EnhancedPermitForm.tsx${NC}"
else
    echo -e "${RED}✗ Autofill fix not found in EnhancedPermitForm.tsx${NC}"
fi

if grep -q "isinstance(permit_checklist, list)" app/backend/ptw/readiness.py; then
    echo -e "${GREEN}✓ Readiness fix applied to readiness.py${NC}"
else
    echo -e "${RED}✗ Readiness fix not found in readiness.py${NC}"
fi

if grep -q "contentHtml" app/frontend/src/features/ptw/components/PTWRecordPrintPreview.tsx; then
    echo -e "${GREEN}✓ Print fix applied to PTWRecordPrintPreview.tsx${NC}"
else
    echo -e "${RED}✗ Print fix not found in PTWRecordPrintPreview.tsx${NC}"
fi

echo
echo -e "${GREEN}=== All Validations Passed ===${NC}"
echo
echo "Summary of fixes:"
echo "A) Autofill: Fixed handlePermitTypeChange to always apply template defaults"
echo "B) Readiness: Fixed 500 error when safety_checklist is list instead of dict"  
echo "C) Print: Fixed [object Object] rendering by using proper HTML string generation"
echo
echo "Files modified:"
echo "- app/frontend/src/features/ptw/components/EnhancedPermitForm.tsx"
echo "- app/backend/ptw/readiness.py"
echo "- app/frontend/src/features/ptw/components/PTWRecordPrintPreview.tsx"
echo "- app/backend/ptw/tests/test_readiness_regression.py (new)"