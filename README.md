# Athens EHS System

## Quick Start

### Quick Start
```bash
# Backend
export ATHENS_BACKEND_PORT=8001
cd backend && source venv/bin/activate && python startup_guard.py && python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT}

# Frontend  
export VITE_PORT=3000
cd frontend && npm run dev
```

### Production
```bash
./setup_https_config.sh
```

This project does not use Docker at runtime. Any remaining references are vendor text or optional infra templates.

## Troubleshooting & Maintenance

### Quick Diagnostic
Run system health check:
```bash
./diagnose_system.sh
```

### Common Issues

#### Mixed Content Error (HTTPS/HTTP)
- **Problem**: Browser blocks HTTP content on HTTPS site
- **Solution**: Run `./setup_https_config.sh` or see `docs/ops/MIXED_CONTENT_TROUBLESHOOTING.md`

#### 502 Bad Gateway
- **Problem**: Backend not responding
- **Quick Fix**: 
  ```bash
  cd /var/www/athens/backend
  source venv/bin/activate
  export ATHENS_BACKEND_PORT=8001
  python startup_guard.py  # Validates port configuration
  python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT} &
  ```

#### Frontend Not Loading
- **Problem**: Vite server crashed
- **Quick Fix**:
  ```bash
  cd /var/www/athens/frontend
  pkill -f vite
  npm run dev &
  ```

### Emergency Recovery
```bash
# Complete system restart
./setup_https_config.sh

# Or manual restart
pkill -f vite
pkill -f "python.*manage.py"
export ATHENS_BACKEND_PORT=8001
cd /var/www/athens/backend && source venv/bin/activate && python startup_guard.py && python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT} &
cd /var/www/athens/frontend && VITE_PORT=3000 npm run dev &
systemctl restart nginx
```

### Maintenance Files
- `docs/ops/MIXED_CONTENT_TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `setup_https_config.sh` - Automated HTTPS setup
- `diagnose_system.sh` - System health checker
- `docs/ops/SYSTEM_STATUS.md` - Current system status

## Repository Layout

- `app/` - Runtime application code (backend, frontend, plugins)
- `infra/` - nginx, systemd, deployment scaffolding
- `scripts/` - Ops, admin, maintenance, and debug utilities
- `tests/` - Manual test and validation scripts
- `docs/` - Architecture, runbooks, and reports

Legacy paths at repo root are maintained as compatibility symlinks for production safety.

## Offline Attendance Sync

- Attendance events are queued in IndexedDB (`athens_offline.attendance_events`) with localStorage fallback.
- Sync auto-runs when online and posts to `/api/attendance/events/bulk/` with idempotent client IDs.
- Rejected events remain in the queue with an error reason; check the dashboard indicator for counts.
- Debugging: inspect queue items in DevTools > Application > IndexedDB, and query `/api/attendance/sync-status/` for last receipt time.
