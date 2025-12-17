#!/bin/bash

# ============================================================================
# CORS Testing Script for EHS Management System
# ============================================================================

echo "🔍 Testing CORS Headers for All Endpoints"
echo "=========================================="

# Test endpoints
endpoints=(
    "/authentication/dashboard/overview/?period=week"
    "/authentication/company-data/"
    "/authentication/userdetail/"
    "/authentication/admin/me/"
)

for endpoint in "${endpoints[@]}"; do
    echo ""
    echo "🔗 Testing: $endpoint"
    echo "----------------------------------------"
    
    # Test with CORS headers
    response=$(curl -s -I -H "Origin: http://localhost:5173" -H "Content-Type: application/json" "http://localhost:8000$endpoint")
    
    # Check if CORS headers are present
    if echo "$response" | grep -q "access-control-allow-origin"; then
        echo "✅ CORS Headers: PRESENT"
        echo "   Origin: $(echo "$response" | grep "access-control-allow-origin" | cut -d' ' -f2-)"
        echo "   Credentials: $(echo "$response" | grep "access-control-allow-credentials" | cut -d' ' -f2-)"
    else
        echo "❌ CORS Headers: MISSING"
    fi
    
    # Check HTTP status
    status=$(echo "$response" | head -n1 | cut -d' ' -f2)
    echo "   HTTP Status: $status"
done

echo ""
echo "🎯 CORS Test Complete!"
echo "If all endpoints show 'CORS Headers: PRESENT', then CORS is working correctly."
echo "The 401 status is expected for unauthenticated requests."
