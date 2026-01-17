#!/bin/bash

echo "=== Digital Signature CSS Debug Script ==="
echo "Timestamp: $(date)"
echo ""

# Check if CSS files exist and their timestamps
echo "1. Checking CSS files:"
echo "   Source CSS:"
ls -la /var/www/athens/frontend/src/components/DigitalSignature.css 2>/dev/null || echo "   ❌ DigitalSignature.css not found"
ls -la /var/www/athens/frontend/src/common/styles/global.css 2>/dev/null || echo "   ❌ global.css not found"
ls -la /var/www/athens/frontend/src/styles/alignment-fix.css 2>/dev/null || echo "   ❌ alignment-fix.css not found"

echo ""
echo "   Built CSS:"
ls -la /var/www/athens/frontend/dist/assets/*.css 2>/dev/null || echo "   ❌ No built CSS found"

echo ""

# Check if our CSS rules are in the built file
echo "2. Checking if Digital Signature CSS is in built file:"
BUILT_CSS=$(find /var/www/athens/frontend/dist/assets -name "*.css" | head -1)
if [ -f "$BUILT_CSS" ]; then
    echo "   Built CSS file: $BUILT_CSS"
    echo "   Digital Signature rules found:"
    grep -c "digital-signature-container" "$BUILT_CSS" && echo "   ✅ digital-signature-container found" || echo "   ❌ digital-signature-container missing"
    grep -c "signature-left-section" "$BUILT_CSS" && echo "   ✅ signature-left-section found" || echo "   ❌ signature-left-section missing"
    grep -c "signature-right-section" "$BUILT_CSS" && echo "   ✅ signature-right-section found" || echo "   ❌ signature-right-section missing"
    grep -c "text-align:right" "$BUILT_CSS" && echo "   ✅ text-align:right found" || echo "   ❌ text-align:right missing"
    grep -c "white-space:normal" "$BUILT_CSS" && echo "   ✅ white-space:normal found" || echo "   ❌ white-space:normal missing"
else
    echo "   ❌ No built CSS file found"
fi

echo ""

# Check nginx configuration
echo "3. Checking nginx configuration:"
nginx -t 2>&1 | head -5
echo ""

# Check if nginx is serving the correct files
echo "4. Testing CSS delivery:"
curl -s -I "https://prozeal.athenas.co.in/assets/index-3eWiNpfD.css" | head -5 2>/dev/null || echo "   ❌ CSS file not accessible via HTTPS"

echo ""

# Check browser cache headers
echo "5. Checking cache headers:"
curl -s -I "https://prozeal.athenas.co.in/" | grep -i cache 2>/dev/null || echo "   No cache headers found"

echo ""

# Test if the main site is accessible
echo "6. Testing main site accessibility:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}, Total Time: %{time_total}s\n" "https://prozeal.athenas.co.in/" 2>/dev/null || echo "   ❌ Site not accessible"

echo ""

# Check if there are any conflicting CSS files
echo "7. Checking for conflicting CSS:"
find /var/www/athens -name "*.css" -exec grep -l "signature-left-section\|signature-right-section" {} \; 2>/dev/null | head -10

echo ""

# Check current processes
echo "8. Checking running processes:"
ps aux | grep -E "(nginx|node|vite)" | grep -v grep | head -5

echo ""
echo "=== Debug Complete ==="