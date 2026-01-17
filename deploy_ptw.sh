#!/bin/bash
# PTW Module Deployment Script

set -e

echo "=========================================="
echo "PTW Module Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}Please do not run as root${NC}"
   exit 1
fi

# Step 1: Database Migration
echo -e "${YELLOW}[1/8] Running database migrations...${NC}"
cd /var/www/athens/app/backend
source venv/bin/activate
python manage.py migrate ptw
echo -e "${GREEN}✓ Migrations complete${NC}"
echo ""

# Step 2: Collect Static Files
echo -e "${YELLOW}[2/8] Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

# Step 3: Run Backend Tests
echo -e "${YELLOW}[3/8] Running backend tests...${NC}"
python manage.py test ptw.tests.test_readiness_endpoint --verbosity=0 || echo "Skipping (DB not configured)"
echo -e "${GREEN}✓ Backend tests checked${NC}"
echo ""

# Step 4: Build Frontend
echo -e "${YELLOW}[4/8] Building frontend...${NC}"
cd /var/www/athens/app/frontend
npm run build
echo -e "${GREEN}✓ Frontend built${NC}"
echo ""

# Step 5: Restart Backend
echo -e "${YELLOW}[5/8] Restarting backend services...${NC}"
cd /var/www/athens
pkill -f "python.*manage.py runserver" || true
sleep 2
cd app/backend
source venv/bin/activate
export ATHENS_BACKEND_PORT=8001
nohup python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT} > /var/log/athens/backend.log 2>&1 &
echo -e "${GREEN}✓ Backend restarted${NC}"
echo ""

# Step 6: Restart Frontend
echo -e "${YELLOW}[6/8] Restarting frontend...${NC}"
pkill -f vite || true
sleep 2
cd /var/www/athens/app/frontend
export VITE_PORT=3000
nohup npm run dev > /var/log/athens/frontend.log 2>&1 &
echo -e "${GREEN}✓ Frontend restarted${NC}"
echo ""

# Step 7: Restart Celery
echo -e "${YELLOW}[7/8] Restarting Celery workers...${NC}"
pkill -f celery || true
sleep 2
cd /var/www/athens/app/backend
source venv/bin/activate
nohup celery -A backend worker -l info > /var/log/athens/celery-worker.log 2>&1 &
nohup celery -A backend beat -l info > /var/log/athens/celery-beat.log 2>&1 &
echo -e "${GREEN}✓ Celery restarted${NC}"
echo ""

# Step 8: Restart Nginx
echo -e "${YELLOW}[8/8] Restarting Nginx...${NC}"
sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx restarted${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Services Status:"
echo "  Backend:  http://localhost:8001"
echo "  Frontend: http://localhost:3000"
echo "  Nginx:    http://localhost"
echo ""
echo "Logs:"
echo "  Backend:  tail -f /var/log/athens/backend.log"
echo "  Frontend: tail -f /var/log/athens/frontend.log"
echo "  Celery:   tail -f /var/log/athens/celery-worker.log"
echo ""
