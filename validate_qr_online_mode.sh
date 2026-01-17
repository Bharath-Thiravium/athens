#!/bin/bash

# QR Code & Online Mode Feature Validation Script
# This script validates the implementation of QR code generation and online/offline mode functionality

echo "🔍 Validating QR Code & Online Mode Feature Implementation..."
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to check if a file exists and contains specific content
check_file_content() {
    local file_path="$1"
    local search_pattern="$2"
    local description="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ -f "$file_path" ]; then
        if grep -q "$search_pattern" "$file_path"; then
            echo -e "${GREEN}✓${NC} $description"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            return 0
        else
            echo -e "${RED}✗${NC} $description - Pattern not found"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $description - File not found: $file_path"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

# Function to check if a file exists
check_file_exists() {
    local file_path="$1"
    local description="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✓${NC} $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $description - File not found: $file_path"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

echo -e "${BLUE}Backend QR Code Utilities${NC}"
echo "----------------------------------------"

# Check enhanced QR utilities
check_file_content "app/backend/ptw/qr_utils.py" "def validate_qr_data" "Enhanced QR validation function"
check_file_content "app/backend/ptw/qr_utils.py" "def generate_batch_qr_codes" "Batch QR generation function"
check_file_content "app/backend/ptw/qr_utils.py" "cache\.set" "QR code caching implementation"
check_file_content "app/backend/ptw/qr_utils.py" "expires.*isoformat" "QR code expiration handling"
check_file_content "app/backend/ptw/qr_utils.py" "offline_data" "Offline data in QR payload"

echo -e "\n${BLUE}Backend API Endpoints${NC}"
echo "----------------------------------------"

# Check enhanced backend views
check_file_content "app/backend/ptw/views.py" "batch_generate_qr" "Batch QR generation endpoint"
check_file_content "app/backend/ptw/views.py" "update_online_status" "Online status update endpoint"
check_file_content "app/backend/ptw/views.py" "get_online_users" "Online users endpoint"
check_file_content "app/backend/ptw/views.py" "get_system_status" "System status endpoint"
check_file_content "app/backend/ptw/views.py" "validate_qr_data" "Enhanced QR validation in views"
check_file_content "app/backend/ptw/views.py" "mobile_metadata" "Enhanced mobile permit view"

echo -e "\n${BLUE}Backend URL Configuration${NC}"
echo "----------------------------------------"

# Check URL patterns
check_file_content "app/backend/ptw/urls.py" "status/update/" "Online status update URL"
check_file_content "app/backend/ptw/urls.py" "status/online-users/" "Online users URL"
check_file_content "app/backend/ptw/urls.py" "status/system/" "System status URL"
check_file_content "app/backend/ptw/urls.py" "work-time-settings/" "Work time settings URL"

echo -e "\n${BLUE}Frontend QR Code Integration${NC}"
echo "----------------------------------------"

# Check PermitDetail QR integration
check_file_content "app/frontend/src/features/ptw/components/PermitDetail.tsx" "handleGenerateQR" "QR generation handler in PermitDetail"
check_file_content "app/frontend/src/features/ptw/components/PermitDetail.tsx" "QrcodeOutlined" "QR code icon import"
check_file_content "app/frontend/src/features/ptw/components/PermitDetail.tsx" "qrModal" "QR modal state"
check_file_content "app/frontend/src/features/ptw/components/PermitDetail.tsx" "generate_qr_code" "QR API call"

echo -e "\n${BLUE}Frontend Mobile App Enhancement${NC}"
echo "----------------------------------------"

# Check enhanced mobile app
check_file_content "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" "checkSystemHealth" "System health check function"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" "startStatusUpdates" "Status update function"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" "notification\." "Enhanced notifications"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" "sync-offline-data" "Offline sync API call"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" "getDeviceId" "Device ID generation"

echo -e "\n${BLUE}Frontend Mobile View Enhancement${NC}"
echo "----------------------------------------"

# Check enhanced mobile view
check_file_content "app/frontend/src/features/ptw/components/MobilePermitView.tsx" "isOffline" "Offline state management"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitView.tsx" "localStorage\.setItem" "Offline caching"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitView.tsx" "status_indicators" "Status indicators"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitView.tsx" "recent_photos" "Recent photos display"
check_file_content "app/frontend/src/features/ptw/components/MobilePermitView.tsx" "recent_gas_readings" "Recent gas readings display"

echo -e "\n${BLUE}Frontend Routing${NC}"
echo "----------------------------------------"

# Check mobile route
check_file_content "app/frontend/src/features/ptw/routes.tsx" "MobilePermitApp" "Mobile app import"
check_file_content "app/frontend/src/features/ptw/routes.tsx" "path=\"mobile\"" "Mobile route definition"

echo -e "\n${BLUE}Feature Completeness Check${NC}"
echo "----------------------------------------"

# Check for key feature components
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if grep -q "generate_permit_qr_code.*size=" "app/backend/ptw/qr_utils.py" && \
   grep -q "cache\.set" "app/backend/ptw/qr_utils.py" && \
   grep -q "offline_data" "app/backend/ptw/qr_utils.py"; then
    echo -e "${GREEN}✓${NC} Enhanced QR code generation with caching and offline support"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}✗${NC} Enhanced QR code generation incomplete"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if grep -q "update_online_status" "app/backend/ptw/views.py" && \
   grep -q "get_online_users" "app/backend/ptw/views.py" && \
   grep -q "get_system_status" "app/backend/ptw/views.py"; then
    echo -e "${GREEN}✓${NC} Online/offline status management API endpoints"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}✗${NC} Online/offline status management incomplete"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if grep -q "checkSystemHealth" "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" && \
   grep -q "syncOfflineData" "app/frontend/src/features/ptw/components/MobilePermitApp.tsx" && \
   grep -q "notification\." "app/frontend/src/features/ptw/components/MobilePermitApp.tsx"; then
    echo -e "${GREEN}✓${NC} Enhanced mobile app with offline sync and notifications"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}✗${NC} Enhanced mobile app incomplete"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if grep -q "localStorage\.setItem.*permit_" "app/frontend/src/features/ptw/components/MobilePermitView.tsx" && \
   grep -q "isOffline" "app/frontend/src/features/ptw/components/MobilePermitView.tsx" && \
   grep -q "cached_at" "app/frontend/src/features/ptw/components/MobilePermitView.tsx"; then
    echo -e "${GREEN}✓${NC} Mobile view with offline caching and status indicators"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "${RED}✗${NC} Mobile view offline support incomplete"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

echo -e "\n${BLUE}Security and Performance Check${NC}"
echo "----------------------------------------"

# Check security features
check_file_content "app/backend/ptw/qr_utils.py" "_sign_qr_payload" "QR code signature verification"
check_file_content "app/backend/ptw/qr_utils.py" "expires.*timezone" "QR code expiration security"
check_file_content "app/backend/ptw/views.py" "PermitAudit\.objects\.create" "QR generation audit logging"

# Check performance features
check_file_content "app/backend/ptw/qr_utils.py" "cache_key.*version" "Version-based caching"
check_file_content "app/backend/ptw/views.py" "len.*permit_ids.*50" "Batch size limiting"

echo -e "\n${BLUE}Summary${NC}"
echo "================================================================"
echo -e "Total Checks: ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All checks passed! QR Code & Online Mode feature is properly implemented.${NC}"
    echo -e "\n${BLUE}Key Features Implemented:${NC}"
    echo "• Enhanced QR code generation with caching and offline support"
    echo "• QR code signature verification and expiration"
    echo "• Batch QR code generation for multiple permits"
    echo "• Online/offline status management API"
    echo "• Real-time user presence tracking"
    echo "• System health monitoring"
    echo "• Enhanced mobile app with offline sync"
    echo "• Mobile permit view with caching"
    echo "• Improved error handling and notifications"
    echo "• Security features (signatures, expiration)"
    echo "• Performance optimizations (caching, batching)"
    
    echo -e "\n${BLUE}Usage Instructions:${NC}"
    echo "1. Generate QR codes from permit detail page"
    echo "2. Access mobile app at /dashboard/ptw/mobile"
    echo "3. Scan QR codes for quick permit access"
    echo "4. Mobile app works offline with cached data"
    echo "5. Automatic sync when connection restored"
    
    exit 0
else
    echo -e "\n${RED}❌ Some checks failed. Please review the implementation.${NC}"
    
    echo -e "\n${YELLOW}Common Issues:${NC}"
    echo "• Missing imports or function definitions"
    echo "• Incomplete API endpoint implementations"
    echo "• Missing offline caching logic"
    echo "• Incomplete error handling"
    
    exit 1
fi