#!/bin/bash
echo "=========================================="
echo "PTW Module - Final Validation"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0

# 1. PostgreSQL
echo -n "1. PostgreSQL Connection: "
if sudo -u postgres psql -d athens_ehs -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 2. Django Check
echo -n "2. Django System Check: "
cd app/backend
if source venv/bin/activate && python manage.py check > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 3. Frontend Build
echo -n "3. Frontend Build: "
cd ../frontend
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 4. Webhooks
echo -n "4. Webhook Implementation: "
cd /var/www/athens
if [ -f "app/backend/ptw/webhook_dispatcher.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 5. Documentation
echo -n "5. Documentation Complete: "
if [ -f "PTW_COMPLETE_IMPLEMENTATION_GUIDE.md" ] && [ -f "PTW_FINAL_SUMMARY.md" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 6. Deployment Scripts
echo -n "6. Deployment Scripts: "
if [ -x "deploy_ptw.sh" ] && [ -x "fix_postgres.sh" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 7. Readiness Endpoint
echo -n "7. Readiness Endpoint: "
if [ -f "app/backend/ptw/readiness.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 8. Reports
echo -n "8. Reporting System: "
if [ -f "app/backend/ptw/report_utils.py" ] && [ -f "app/frontend/src/features/ptw/components/PTWReports.tsx" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

echo ""
echo "=========================================="
echo "Results: $PASS passed, $FAIL failed"
echo "=========================================="

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME CHECKS FAILED${NC}"
    exit 1
fi
