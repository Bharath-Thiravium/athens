#!/bin/bash

# Athens EHS System Startup Script
# Ensures consistent port configuration and prevents mismatches

echo "🚀 Starting Athens EHS System..."

# Load environment variables
export ATHENS_BACKEND_PORT=${ATHENS_BACKEND_PORT:-8001}
ENV_FILE="/var/www/athens/backend/.env"
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi
DB_HOST="${PG_DB_HOST:-${DB_HOST:-127.0.0.1}}"
DB_PORT="${PG_DB_PORT:-${DB_PORT:-5432}}"

# Validate port configuration
if [ "$ATHENS_BACKEND_PORT" = "8000" ]; then
    echo "❌ CRITICAL ERROR: Port 8000 is FORBIDDEN!"
    echo "   Set ATHENS_BACKEND_PORT=8001"
    exit 1
fi

# Kill any existing processes
echo "Stopping existing processes..."
sudo pkill -f "python.*manage.py" 2>/dev/null
sudo pkill -f "vite" 2>/dev/null
sleep 2

# Ensure database is running before starting backend
if command -v systemctl >/dev/null 2>&1; then
    if systemctl list-units --type=service --all | grep -q "postgresql@"; then
        sudo systemctl start postgresql@16-main 2>/dev/null || true
    else
        sudo systemctl start postgresql 2>/dev/null || true
    fi
fi

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
if command -v pg_isready >/dev/null 2>&1; then
    for i in {1..30}; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
        echo "❌ PostgreSQL is not ready on ${DB_HOST}:${DB_PORT}"
        exit 1
    fi
else
    echo "⚠️ pg_isready not found; skipping DB readiness check."
fi

# Start backend on configured port
echo "Starting backend on port $ATHENS_BACKEND_PORT..."
cd /var/www/athens/backend
source venv/bin/activate

# Run startup guard
python startup_guard.py

# Start backend
python manage.py runserver 0.0.0.0:$ATHENS_BACKEND_PORT &
sleep 3

# Verify backend is running
if curl -s http://localhost:$ATHENS_BACKEND_PORT > /dev/null; then
    echo "✅ Backend running on port $ATHENS_BACKEND_PORT"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
frontend_listening=false
if command -v ss >/dev/null 2>&1; then
    if ss -lntp 2>/dev/null | grep -q ':3000'; then
        frontend_listening=true
    fi
elif command -v lsof >/dev/null 2>&1; then
    if lsof -i :3000 >/dev/null 2>&1; then
        frontend_listening=true
    fi
fi

if $frontend_listening && pgrep -fa "vite|npm.*run.*dev" >/dev/null 2>&1; then
    echo "✅ Frontend already running on :3000; skipping start."
else
    echo "Starting frontend on port 3000..."
    cd /var/www/athens/frontend
    VITE_PORT=3000 npm run dev > /tmp/frontend.log 2>&1 &
    sleep 3
fi

echo "✅ Athens EHS System started successfully"
echo "Frontend: https://prozeal.athenas.co.in (port 3000)"
echo "Backend: Port $ATHENS_BACKEND_PORT (via nginx)"
