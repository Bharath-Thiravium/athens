#!/bin/bash
# Production Deployment Script for PTW Updates
# Run from /var/www/athens

set -e  # Exit on error

echo "========================================="
echo "PTW Production Deployment"
echo "========================================="
echo ""

# Step 1: Run Migrations
echo "[1/3] Running database migrations..."
cd /var/www/athens/app/backend

# Source production environment
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
    echo "✅ Loaded .env.production"
else
    echo "❌ .env.production not found"
    exit 1
fi

# Activate venv
if [ -d venv ]; then
    source venv/bin/activate
    echo "✅ Activated venv"
else
    echo "❌ venv not found"
    exit 1
fi

# Run migrations
echo "Running: python3 manage.py migrate ptw"
python3 manage.py migrate ptw

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed"
else
    echo "❌ Migrations failed"
    exit 1
fi

# Step 2: Rebuild Frontend
echo ""
echo "[2/3] Rebuilding frontend..."
cd /var/www/athens/app/frontend

if [ -f package.json ]; then
    npm run build
    if [ $? -eq 0 ]; then
        echo "✅ Frontend build completed"
    else
        echo "❌ Frontend build failed"
        exit 1
    fi
else
    echo "❌ package.json not found"
    exit 1
fi

# Step 3: Restart Backend
echo ""
echo "[3/3] Restarting backend..."
cd /var/www/athens/app/backend

# Kill existing backend
pkill -f "python.*manage.py runserver" || echo "No existing backend process"

# Start backend
export ATHENS_BACKEND_PORT=8001
source venv/bin/activate
export $(cat .env.production | grep -v '^#' | xargs)

nohup python3 manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT} > /var/log/athens_backend.log 2>&1 &

sleep 2

if pgrep -f "python.*manage.py runserver" > /dev/null; then
    echo "✅ Backend restarted"
else
    echo "❌ Backend failed to start"
    exit 1
fi

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Verification:"
echo "- Check migrations: cd app/backend && python3 manage.py showmigrations ptw"
echo "- Check frontend: ls -lh app/frontend/dist/index.html"
echo "- Check backend: curl http://localhost:8001/api/v1/ptw/permits/"
echo "- Check logs: tail -f /var/log/athens_backend.log"
echo ""
echo "New features available:"
echo "- Readiness Panel: /dashboard/ptw/view/{id} → Readiness tab"
echo "- Reports Page: /dashboard/ptw/reports"
echo "- Webhooks API: /api/v1/ptw/webhooks/"
