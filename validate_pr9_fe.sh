#!/bin/bash
# PR9-FE Validation Script
# Validates Notifications UI implementation

echo "=== PR9-FE: Notifications UI Validation ==="
echo ""

BACKEND_DIR="app/backend"
FRONTEND_DIR="app/frontend/src"
PASS=0
FAIL=0

# Check 1: Notifications page exists
echo "✓ Check 1: Notifications page exists"
if [ -f "$FRONTEND_DIR/pages/Notifications.tsx" ]; then
    echo "  ✓ Notifications.tsx found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Notifications.tsx NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 2: Route added to App.tsx
echo "✓ Check 2: Route added to App.tsx"
if grep -q "path=\"notifications\"" "$FRONTEND_DIR/app/App.tsx"; then
    echo "  ✓ Notifications route found in App.tsx"
    PASS=$((PASS + 1))
else
    echo "  ✗ Notifications route NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 3: NotificationCenter updated with View All button
echo "✓ Check 3: NotificationCenter has View All button"
if grep -q "View All Notifications" "$FRONTEND_DIR/features/dashboard/components/NotificationCenter.tsx"; then
    echo "  ✓ View All button found"
    PASS=$((PASS + 1))
else
    echo "  ✗ View All button NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 4: Backend notification APIs exist
echo "✓ Check 4: Backend notification APIs exist"
if grep -q "NotificationListView" "$BACKEND_DIR/authentication/notification_views.py"; then
    echo "  ✓ Notification APIs found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Notification APIs NOT found"
    FAIL=$((FAIL + 1))
fi

# Check 5: PTW notification links use correct format
echo "✓ Check 5: PTW notification links format"
if grep -q "/dashboard/ptw/view/" "$BACKEND_DIR/ptw/notification_utils.py"; then
    echo "  ✓ Correct PTW link format found"
    PASS=$((PASS + 1))
else
    echo "  ✗ Incorrect PTW link format"
    FAIL=$((FAIL + 1))
fi

# Check 6: Frontend uses NotificationsContext
echo "✓ Check 6: Frontend uses NotificationsContext"
if grep -q "useNotificationsContext" "$FRONTEND_DIR/pages/Notifications.tsx"; then
    echo "  ✓ NotificationsContext used"
    PASS=$((PASS + 1))
else
    echo "  ✗ NotificationsContext NOT used"
    FAIL=$((FAIL + 1))
fi

# Check 7: Notification type colors defined
echo "✓ Check 7: Notification type colors"
if grep -q "getNotificationTypeColor" "$FRONTEND_DIR/pages/Notifications.tsx"; then
    echo "  ✓ Type colors defined"
    PASS=$((PASS + 1))
else
    echo "  ✗ Type colors NOT defined"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Validation Summary ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✓ All checks passed! PR9-FE is ready."
    exit 0
else
    echo "✗ Some checks failed. Please review."
    exit 1
fi
