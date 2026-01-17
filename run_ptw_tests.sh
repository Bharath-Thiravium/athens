#!/bin/bash

# PTW Test Runner with --keepdb
# Runs the full PTW test suite with database preservation

set -e

# Change to backend directory
cd "$(dirname "$0")/app/backend"

# Set required environment variables for testing
export SECRET_KEY='test-secret-key-for-ptw-testing'
export DEBUG=True
export DATABASE_URL='postgresql://localhost/test_athens_ehs'

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running PTW Test Suite with --keepdb${NC}"
echo "=================================="

# Check if database is available
if ! pg_isready -q; then
    echo -e "${RED}PostgreSQL is not running. Please start PostgreSQL first.${NC}"
    echo "Try: sudo systemctl start postgresql"
    exit 1
fi

# Run PTW tests with keepdb
echo -e "${YELLOW}Running all PTW tests...${NC}"
python3 manage.py test ptw.tests --keepdb -v 2

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All PTW tests passed!${NC}"
else
    echo -e "${RED}✗ Some PTW tests failed.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Test Summary:${NC}"
echo "- Used --keepdb to preserve test database"
echo "- All PTW test modules executed"
echo "- Database: test_athens_ehs (preserved)"
echo ""
echo -e "${GREEN}PTW test suite completed successfully!${NC}"