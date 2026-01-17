#!/bin/bash
echo "=== E2E Test Quick Start ==="
echo ""
echo "1. Edit .env.e2e with real credentials"
echo "2. Run: npm run test:athens"
echo "3. Run: npm run test:sap"
echo ""
echo "Current config:"
grep -E "^(ATHENS|SAP)" .env.e2e 2>/dev/null || echo ".env.e2e not configured"
