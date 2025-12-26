#!/bin/bash

# Athens EHS System Monitor
# Monitors and maintains frontend/backend services

LOG_FILE="/var/log/athens-monitor.log"
BACKEND_URL="http://localhost:8000/admin/"
FRONTEND_URL="http://localhost:3000/"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_backend() {
    if curl -s -f "$BACKEND_URL" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_frontend() {
    if curl -s -f "$FRONTEND_URL" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

restart_backend() {
    log_message "Restarting backend service..."
    systemctl restart athens-backend.service
    sleep 5
    if check_backend; then
        log_message "Backend service restarted successfully"
    else
        log_message "Backend service restart failed"
    fi
}

restart_frontend() {
    log_message "Restarting frontend service..."
    systemctl restart athens-frontend.service
    sleep 10
    if check_frontend; then
        log_message "Frontend service restarted successfully"
    else
        log_message "Frontend service restart failed"
    fi
}

# Main monitoring loop
log_message "Athens monitor started"

while true; do
    # Check backend
    if ! check_backend; then
        log_message "Backend is down, attempting restart..."
        restart_backend
    fi
    
    # Check frontend
    if ! check_frontend; then
        log_message "Frontend is down, attempting restart..."
        restart_frontend
    fi
    
    # Wait 30 seconds before next check
    sleep 30
done