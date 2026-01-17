#!/bin/bash
# Validation script for PR15.B, PR16, PR17

echo "========================================="
echo "PR15.B, PR16, PR17 Validation"
echo "========================================="
echo ""

PASS=0
FAIL=0

# Check frontend files
echo "[1/10] Checking ReadinessPanel component..."
if [ -f "app/frontend/src/features/ptw/components/ReadinessPanel.tsx" ]; then
    echo "✅ ReadinessPanel.tsx exists"
    ((PASS++))
else
    echo "❌ ReadinessPanel.tsx missing"
    ((FAIL++))
fi

echo "[2/10] Checking PTWReports component..."
if [ -f "app/frontend/src/features/ptw/components/PTWReports.tsx" ]; then
    echo "✅ PTWReports.tsx exists"
    ((PASS++))
else
    echo "❌ PTWReports.tsx missing"
    ((FAIL++))
fi

echo "[3/10] Checking ReadinessPanel import in PermitDetail..."
if grep -q "ReadinessPanel" app/frontend/src/features/ptw/components/PermitDetail.tsx; then
    echo "✅ ReadinessPanel imported in PermitDetail"
    ((PASS++))
else
    echo "❌ ReadinessPanel not imported"
    ((FAIL++))
fi

echo "[4/10] Checking webhook dispatcher..."
if [ -f "app/backend/ptw/webhook_dispatcher.py" ]; then
    echo "✅ webhook_dispatcher.py exists"
    ((PASS++))
else
    echo "❌ webhook_dispatcher.py missing"
    ((FAIL++))
fi

echo "[5/10] Checking webhook models in models.py..."
if grep -q "class WebhookEndpoint" app/backend/ptw/models.py; then
    echo "✅ WebhookEndpoint model exists"
    ((PASS++))
else
    echo "❌ WebhookEndpoint model missing"
    ((FAIL++))
fi

echo "[6/10] Checking webhook serializers..."
if [ -f "app/backend/ptw/webhook_serializers.py" ]; then
    echo "✅ webhook_serializers.py exists"
    ((PASS++))
else
    echo "❌ webhook_serializers.py missing"
    ((FAIL++))
fi

echo "[7/10] Checking webhook views..."
if [ -f "app/backend/ptw/webhook_views.py" ]; then
    echo "✅ webhook_views.py exists"
    ((PASS++))
else
    echo "❌ webhook_views.py missing"
    ((FAIL++))
fi

echo "[8/10] Checking webhook tests..."
if [ -f "app/backend/ptw/tests/test_webhooks.py" ]; then
    echo "✅ test_webhooks.py exists"
    ((PASS++))
else
    echo "❌ test_webhooks.py missing"
    ((FAIL++))
fi

echo "[9/10] Checking webhook migration..."
if [ -f "app/backend/ptw/migrations/0009_webhooks.py" ]; then
    echo "✅ Webhook migration exists"
    ((PASS++))
else
    echo "❌ Webhook migration missing"
    ((FAIL++))
fi

echo "[10/10] Checking webhook documentation..."
if [ -f "docs/PR17_WEBHOOKS.md" ]; then
    echo "✅ Webhook documentation exists"
    ((PASS++))
else
    echo "❌ Webhook documentation missing"
    ((FAIL++))
fi

echo ""
echo "========================================="
echo "Validation Summary"
echo "========================================="
echo "Passed: $PASS/10"
echo "Failed: $FAIL/10"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED"
    echo ""
    echo "Next steps:"
    echo "1. Run: cd app/backend && python manage.py migrate"
    echo "2. Run: cd app/backend && python manage.py test ptw.tests.test_webhooks"
    echo "3. Test in browser: Open permit detail → Check 'Readiness' tab"
    echo "4. Test in browser: Navigate to /dashboard/ptw/reports"
    exit 0
else
    echo "❌ SOME CHECKS FAILED"
    exit 1
fi
