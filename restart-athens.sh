#!/bin/bash

# Athens EHS System Complete Restart Script
# Kills all existing processes and starts fresh with uvicorn backend

echo "🔄 Athens EHS System Complete Restart"
echo "======================================"

# Configuration
ATHENS_BACKEND_PORT=8001
ATHENS_FRONTEND_PORT=3000
RAYZEN_BACKEND_PORT=8002
SAP_BACKEND_PORT=8003

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local service_name=$2
    echo "🔪 Killing processes on port $port ($service_name)..."
    
    # Kill using lsof if available
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:$port | xargs -r kill -9 2>/dev/null
    fi
    
    # Kill using netstat and awk
    netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | xargs -r kill -9 2>/dev/null
    
    sleep 1
}

# Function to kill processes by pattern
kill_pattern() {
    local pattern=$1
    local service_name=$2
    echo "🔪 Killing $service_name processes..."
    pkill -f "$pattern" 2>/dev/null || true
    sleep 1
}

echo "🛑 Stopping all existing services..."

# Kill specific processes
kill_pattern "python.*manage.py" "Django"
kill_pattern "uvicorn.*backend" "Uvicorn Backend"
kill_pattern "vite" "Vite Frontend"
kill_pattern "npm.*run.*dev" "NPM Dev Server"

# Kill by ports
kill_port $ATHENS_BACKEND_PORT "Athens Backend"
kill_port $ATHENS_FRONTEND_PORT "Athens Frontend"
kill_port $RAYZEN_BACKEND_PORT "Rayzen Backend"
kill_port $SAP_BACKEND_PORT "SAP Backend"

echo "⏳ Waiting for processes to terminate..."
sleep 3

# Verify ports are free
echo "🔍 Checking port availability..."
for port in $ATHENS_BACKEND_PORT $ATHENS_FRONTEND_PORT; do
    if netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "⚠️  Port $port still in use, force killing..."
        kill_port $port "Force Kill"
        sleep 2
    fi
done

# Start PostgreSQL if not running
echo "🗄️  Ensuring PostgreSQL is running..."
if command -v systemctl >/dev/null 2>&1; then
    if systemctl list-units --type=service --all | grep -q "postgresql@"; then
        sudo systemctl start postgresql@16-main 2>/dev/null || sudo systemctl start postgresql 2>/dev/null || true
    else
        sudo systemctl start postgresql 2>/dev/null || true
    fi
fi

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
for i in {1..10}; do
    if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    sleep 1
done

# Start Athens Backend with uvicorn
echo "🚀 Starting Athens Backend (uvicorn) on port $ATHENS_BACKEND_PORT..."
cd /var/www/athens/backend
source venv/bin/activate

# Set environment variable
export ATHENS_BACKEND_PORT=$ATHENS_BACKEND_PORT

# Run startup guard
python startup_guard.py

# Start backend with uvicorn
python -m uvicorn backend.asgi:application --host 0.0.0.0 --port $ATHENS_BACKEND_PORT --workers 2 --limit-concurrency 30 --proxy-headers --forwarded-allow-ips=* &
ATHENS_BACKEND_PID=$!

sleep 8

# Verify Athens backend
echo "🔍 Verifying Athens Backend..."
for i in {1..10}; do
    if curl -s http://localhost:$ATHENS_BACKEND_PORT >/dev/null 2>&1; then
        echo "✅ Athens Backend running on port $ATHENS_BACKEND_PORT (PID: $ATHENS_BACKEND_PID)"
        break
    elif [ $i -eq 10 ]; then
        echo "❌ Athens Backend failed to start after 10 attempts"
        echo "📋 Checking if process is still running..."
        if ps -p $ATHENS_BACKEND_PID > /dev/null 2>&1; then
            echo "⚠️  Backend process is running but not responding to HTTP requests"
        else
            echo "❌ Backend process has died"
        fi
        exit 1
    else
        echo "⏳ Waiting for backend to respond... ($i/10)"
        sleep 2
    fi
done

# Start Athens Frontend
echo "🚀 Starting Athens Frontend on port $ATHENS_FRONTEND_PORT..."
cd /var/www/athens/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

VITE_PORT=$ATHENS_FRONTEND_PORT npm run dev > /tmp/athens-frontend.log 2>&1 &
ATHENS_FRONTEND_PID=$!

sleep 5

# Verify frontend
if netstat -tlnp 2>/dev/null | grep -q ":$ATHENS_FRONTEND_PORT "; then
    echo "✅ Athens Frontend running on port $ATHENS_FRONTEND_PORT (PID: $ATHENS_FRONTEND_PID)"
else
    echo "❌ Athens Frontend failed to start"
    echo "📋 Frontend log:"
    tail -10 /tmp/athens-frontend.log
fi

# Start other services if they exist
echo "🚀 Starting other services..."

# Rayzen Backend
if [ -d "/var/www/Rayzen/athenas-backend" ]; then
    echo "🚀 Starting Rayzen Backend on port $RAYZEN_BACKEND_PORT..."
    cd /var/www/Rayzen/athenas-backend
    source venv/bin/activate
    uvicorn config.asgi:application --host 127.0.0.1 --port $RAYZEN_BACKEND_PORT --workers 1 --proxy-headers --forwarded-allow-ips=* &
    sleep 2
    if netstat -tlnp 2>/dev/null | grep -q ":$RAYZEN_BACKEND_PORT "; then
        echo "✅ Rayzen Backend running on port $RAYZEN_BACKEND_PORT"
    fi
fi

# SAP Backend
if [ -d "/var/www/SAP-Python/backend" ]; then
    echo "🚀 Starting SAP Backend on port $SAP_BACKEND_PORT..."
    cd /var/www/SAP-Python/backend
    source venv/bin/activate
    uvicorn sap_backend.asgi:application --host 127.0.0.1 --port $SAP_BACKEND_PORT --workers 1 --proxy-headers --forwarded-allow-ips=* &
    sleep 2
    if netstat -tlnp 2>/dev/null | grep -q ":$SAP_BACKEND_PORT "; then
        echo "✅ SAP Backend running on port $SAP_BACKEND_PORT"
    fi
fi

# Restart nginx
echo "🔄 Restarting nginx..."
sudo systemctl restart nginx 2>/dev/null || true

echo ""
echo "🎉 Athens EHS System Restart Complete!"
echo "======================================"
echo "✅ Athens Backend:  http://localhost:$ATHENS_BACKEND_PORT (uvicorn)"
echo "✅ Athens Frontend: http://localhost:$ATHENS_FRONTEND_PORT (vite)"
echo "🌐 Public Access:   https://prozeal.athenas.co.in"
echo ""
echo "📊 Process Status:"
ps aux | grep -E "(uvicorn|vite|npm.*dev)" | grep -v grep | while read line; do
    echo "   $line"
done
echo ""
echo "🔍 Port Status:"
netstat -tlnp 2>/dev/null | grep -E ":($ATHENS_BACKEND_PORT|$ATHENS_FRONTEND_PORT|$RAYZEN_BACKEND_PORT|$SAP_BACKEND_PORT) " | while read line; do
    echo "   $line"
done