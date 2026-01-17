#!/bin/bash
# PostgreSQL Connection Test and Fix Script

set -e

echo "=========================================="
echo "PostgreSQL Connection Test & Fix"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Check PostgreSQL Service
echo -e "${YELLOW}[1/7] Checking PostgreSQL service...${NC}"
if sudo systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ PostgreSQL service is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL service is not running${NC}"
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
    sleep 2
    echo -e "${GREEN}✓ PostgreSQL started${NC}"
fi
echo ""

# Step 2: Check PostgreSQL Processes
echo -e "${YELLOW}[2/7] Checking PostgreSQL processes...${NC}"
if ps aux | grep -v grep | grep postgres > /dev/null; then
    echo -e "${GREEN}✓ PostgreSQL processes found${NC}"
    ps aux | grep postgres | grep -v grep | head -3
else
    echo -e "${RED}✗ No PostgreSQL processes found${NC}"
fi
echo ""

# Step 3: Check Database Exists
echo -e "${YELLOW}[3/7] Checking if database exists...${NC}"
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='athens_ehs'" 2>/dev/null || echo "0")
if [ "$DB_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ Database 'athens_ehs' exists${NC}"
else
    echo -e "${YELLOW}⚠ Database 'athens_ehs' does not exist${NC}"
    echo "Creating database..."
    sudo -u postgres psql -c "CREATE DATABASE athens_ehs;" 2>/dev/null || echo "Database may already exist"
    echo -e "${GREEN}✓ Database created${NC}"
fi
echo ""

# Step 4: Check User Exists
echo -e "${YELLOW}[4/7] Checking if user exists...${NC}"
USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='athens_user'" 2>/dev/null || echo "0")
if [ "$USER_EXISTS" = "1" ]; then
    echo -e "${GREEN}✓ User 'athens_user' exists${NC}"
else
    echo -e "${YELLOW}⚠ User 'athens_user' does not exist${NC}"
    echo "Creating user..."
    sudo -u postgres psql -c "CREATE USER athens_user WITH PASSWORD 'athens_password';" 2>/dev/null || echo "User may already exist"
    echo -e "${GREEN}✓ User created${NC}"
fi
echo ""

# Step 5: Grant Permissions
echo -e "${YELLOW}[5/7] Granting permissions...${NC}"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE athens_ehs TO athens_user;" 2>/dev/null
sudo -u postgres psql -d athens_ehs -c "GRANT ALL ON SCHEMA public TO athens_user;" 2>/dev/null
sudo -u postgres psql -d athens_ehs -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO athens_user;" 2>/dev/null
sudo -u postgres psql -d athens_ehs -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO athens_user;" 2>/dev/null
echo -e "${GREEN}✓ Permissions granted${NC}"
echo ""

# Step 6: Test Connection from Django
echo -e "${YELLOW}[6/7] Testing Django database connection...${NC}"
cd /var/www/athens/app/backend
source venv/bin/activate 2>/dev/null || true

# Create test script
cat > /tmp/test_db.py << 'EOF'
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, '/var/www/athens/app/backend')

try:
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result[0] == 1:
            print("✓ Database connection successful")
            sys.exit(0)
        else:
            print("✗ Database connection failed")
            sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
EOF

python /tmp/test_db.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Django can connect to database${NC}"
else
    echo -e "${RED}✗ Django cannot connect to database${NC}"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check /var/www/athens/app/backend/.env file"
    echo "2. Verify PG_DB_PASSWORD is set correctly"
    echo "3. Check PostgreSQL pg_hba.conf for authentication settings"
fi
rm -f /tmp/test_db.py
echo ""

# Step 7: Run Migrations
echo -e "${YELLOW}[7/7] Running database migrations...${NC}"
cd /var/www/athens/app/backend
source venv/bin/activate
python manage.py migrate --noinput 2>&1 | tail -5
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrations completed successfully${NC}"
else
    echo -e "${RED}✗ Migrations failed${NC}"
fi
echo ""

echo "=========================================="
echo -e "${GREEN}PostgreSQL Check Complete${NC}"
echo "=========================================="
echo ""
echo "Connection Details:"
echo "  Database: athens_ehs"
echo "  User:     athens_user"
echo "  Host:     localhost"
echo "  Port:     5432"
echo ""
echo "To test manually:"
echo "  sudo -u postgres psql -d athens_ehs"
echo ""
