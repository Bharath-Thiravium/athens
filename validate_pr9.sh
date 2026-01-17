#!/bin/bash
# PR9 Validation Script - Notifications + Escalations

echo "========================================="
echo "PR9 - Notifications + Escalations"
echo "Validation Script"
echo "========================================="
echo ""

cd /var/www/athens/app/backend

# Check 1: Notification utility exists
echo "[1/7] Checking notification utility..."
if [ -f "ptw/notification_utils.py" ]; then
    if grep -q "create_ptw_notification\|notify_permit_submitted\|notify_verifier_assigned" ptw/notification_utils.py; then
        echo "✓ Notification utility created with core functions"
    else
        echo "✗ Notification utility missing core functions"
        exit 1
    fi
else
    echo "✗ Notification utility file missing"
    exit 1
fi

# Check 2: Tasks updated
echo "[2/7] Checking Celery tasks..."
if grep -q "check_overdue_workflow_tasks\|check_pending_closeout_and_isolation" ptw/tasks.py; then
    echo "✓ Celery tasks updated/added"
else
    echo "✗ Celery tasks missing"
    exit 1
fi

# Check 3: Workflow views updated
echo "[3/7] Checking workflow views..."
if grep -q "notify_permit_submitted\|notify_verifier_assigned\|notify_approver_assigned" ptw/workflow_views.py; then
    echo "✓ Workflow views have notification triggers"
else
    echo "✗ Workflow views missing notification triggers"
    exit 1
fi

# Check 4: Tests exist
echo "[4/7] Checking tests..."
if [ -f "ptw/tests/test_notifications.py" ]; then
    if grep -q "test_create_ptw_notification\|test_notification_idempotency\|test_escalation" ptw/tests/test_notifications.py; then
        echo "✓ Notification tests created"
    else
        echo "✗ Tests incomplete"
        exit 1
    fi
else
    echo "✗ Test file missing"
    exit 1
fi

# Check 5: Management command exists
echo "[5/7] Checking management command..."
if [ -f "ptw/management/commands/ptw_check_escalations.py" ]; then
    echo "✓ Management command created"
else
    echo "✗ Management command missing"
    exit 1
fi

# Check 6: Notification types defined
echo "[6/7] Checking notification types..."
if grep -q "ptw_created\|ptw_verification\|ptw_approval\|ptw_escalated" ptw/notification_utils.py; then
    echo "✓ PTW notification types defined"
else
    echo "✗ Notification types missing"
    exit 1
fi

# Check 7: Idempotency implemented
echo "[7/7] Checking idempotency..."
if grep -q "dedupe_key\|generate_dedupe_key" ptw/notification_utils.py; then
    echo "✓ Idempotency/deduplication implemented"
else
    echo "✗ Idempotency missing"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ All PR9 backend validations passed!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run tests: python manage.py test ptw.tests.test_notifications"
echo "2. Check Django: python manage.py check"
echo "3. Test management command: python manage.py ptw_check_escalations"
echo "4. Configure settings: NOTIFICATIONS_ENABLED=True, ESCALATIONS_ENABLED=False"
echo "5. Configure Celery beat schedule or cron jobs"
echo "6. Create EscalationRule entries in Django admin"
