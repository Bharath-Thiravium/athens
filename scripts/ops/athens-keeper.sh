#!/bin/bash

# Athens Process Keeper - Ensures continuous operation
# Monitors and auto-restarts frontend/backend services

BACKEND_DIR="/var/www/athens/backend"
FRONTEND_DIR="/var/www/athens/frontend"
LOG_FILE="/var/log/athens-keeper.log"
PID_FILE="/var/run/athens-keeper.pid"
MAINTENANCE_FILE="/var/www/athens/.maintenance"

# Configuration
BACKEND_PORT=${ATHENS_BACKEND_PORT:-8001}
FRONTEND_PORT=3000
CHECK_INTERVAL=10

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [KEEPER] $1" | tee -a "$LOG_FILE"
}

cleanup() {
    log "Shutting down Athens Keeper..."
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Check if maintenance mode is enabled
is_maintenance() {
    [ -f "$MAINTENANCE_FILE" ]
}

# Check if backend is running
check_backend() {
    pgrep -f "uvicorn.*backend.asgi.*$BACKEND_PORT" > /dev/null
}

# Check if frontend is running
check_frontend() {
    pgrep -f "vite.*--port.*$FRONTEND_PORT" > /dev/null || pgrep -f "npm.*run.*dev" > /dev/null
}

# Start backend
start_backend() {
    log "Starting backend on port $BACKEND_PORT..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    export ATHENS_BACKEND_PORT=$BACKEND_PORT
    python startup_guard.py
    nohup python -m uvicorn backend.asgi:application --host 0.0.0.0 --port $BACKEND_PORT --workers ${UVICORN_WORKERS:-3} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-70} --limit-concurrency ${UVICORN_LIMIT_CONCURRENCY:-100} --proxy-headers --forwarded-allow-ips=* > /tmp/backend.log 2>&1 &
    sleep 3
    if check_backend; then
        log "Backend started successfully"
    else
        log "Backend failed to start"
    fi
}

# Start frontend
start_frontend() {
    log "Starting frontend on port $FRONTEND_PORT..."
    cd "$FRONTEND_DIR"
    export VITE_PORT=$FRONTEND_PORT
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    sleep 5
    if check_frontend; then
        log "Frontend started successfully"
    else
        log "Frontend failed to start"
    fi
}

# Stop services
stop_services() {
    log "Stopping services for maintenance..."
    pkill -f "uvicorn.*backend.asgi"
    pkill -f "vite"
    pkill -f "npm.*run.*dev"
}

# Main keeper loop
main() {
    echo $$ > "$PID_FILE"
    log "Athens Keeper started (PID: $$)"
    
    while true; do
        if is_maintenance; then
            if check_backend || check_frontend; then
                stop_services
                log "Services stopped - maintenance mode active"
            fi
        else
            # Check and restart backend if needed
            if ! check_backend; then
                log "Backend not running, restarting..."
                pkill -f "uvicorn.*backend.asgi" 2>/dev/null
                start_backend
            fi
            
            # Check and restart frontend if needed
            if ! check_frontend; then
                log "Frontend not running, restarting..."
                pkill -f "vite" 2>/dev/null
                pkill -f "npm.*run.*dev" 2>/dev/null
                start_frontend
            fi
        fi
        
        sleep $CHECK_INTERVAL
    done
}

# Commands
case "${1:-start}" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Athens Keeper already running (PID: $(cat $PID_FILE))"
            exit 1
        fi
        main
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            kill $(cat "$PID_FILE") 2>/dev/null
            rm -f "$PID_FILE"
            echo "Athens Keeper stopped"
        else
            echo "Athens Keeper not running"
        fi
        ;;
    maintenance)
        touch "$MAINTENANCE_FILE"
        log "Maintenance mode enabled"
        echo "Maintenance mode enabled. Services will stop automatically."
        ;;
    resume)
        rm -f "$MAINTENANCE_FILE"
        log "Maintenance mode disabled"
        echo "Maintenance mode disabled. Services will start automatically."
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            echo "Athens Keeper: RUNNING (PID: $(cat $PID_FILE))"
        else
            echo "Athens Keeper: STOPPED"
        fi
        
        if is_maintenance; then
            echo "Maintenance Mode: ENABLED"
        else
            echo "Maintenance Mode: DISABLED"
        fi
        
        if check_backend; then
            echo "Backend: RUNNING"
        else
            echo "Backend: STOPPED"
        fi
        
        if check_frontend; then
            echo "Frontend: RUNNING"
        else
            echo "Frontend: STOPPED"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|maintenance|resume|status}"
        exit 1
        ;;
esac
