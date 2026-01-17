# Port Configuration Guide

## 🔒 Authoritative Port Ownership

**CRITICAL: These port assignments are FIXED and must not be changed**

| Service | Port | Environment Variable | Status |
|---------|------|---------------------|---------|
| Athens Backend (Django) | 8001 | `ATHENS_BACKEND_PORT=8001` | ✅ Active |
| Athens Frontend (React/Vite) | 3000 | `VITE_PORT=3000` | ✅ Active |
| **Port 8000** | **FORBIDDEN** | ❌ Must never be used | 🚫 Blocked |

## 🛡️ Port Conflict Prevention

### Backend Protection
- **Startup Guard**: `backend/startup_guard.py` validates port configuration
- **Environment Required**: `ATHENS_BACKEND_PORT` must be set
- **Port 8000 Blocked**: Script fails if port 8000 is attempted

### Frontend Protection  
- **Strict Port Mode**: `strictPort: true` in `vite.config.ts`
- **No Auto-switching**: Vite will fail rather than use different port
- **Environment Driven**: Uses `VITE_PORT=3000`

## 🚀 Startup Commands

### Environment Setup
```bash
# Required environment variables
export ATHENS_BACKEND_PORT=8001
export VITE_PORT=3000
```

### Backend Startup
```bash
cd /var/www/athens/backend
source venv/bin/activate
python startup_guard.py  # Validates configuration
python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT}
```

### Frontend Startup
```bash
cd /var/www/athens/frontend
npm run dev  # Uses VITE_PORT=3000 with strictPort: true
```

## 🔧 Configuration Files

### Backend Environment
- `/var/www/athens/backend/.env`: `ATHENS_BACKEND_PORT=8001`
- `/var/www/athens/backend/.env.example`: Template with port configuration

### Frontend Environment
- `/var/www/athens/frontend/.env`: `VITE_PORT=3000`
- `/var/www/athens/frontend/.env.example`: Template with port configuration
- `/var/www/athens/frontend/vite.config.ts`: `strictPort: true`

## 🌐 Nginx Routing

The nginx configuration routes traffic correctly:
- Backend: `proxy_pass http://127.0.0.1:8001`
- Frontend: `proxy_pass http://127.0.0.1:3000`

## ✅ Validation Checklist

Run these commands to verify configuration:

```bash
# Check environment variables
echo "Backend Port: $ATHENS_BACKEND_PORT"
echo "Frontend Port: $VITE_PORT"

# Validate backend configuration
cd /var/www/athens/backend && python startup_guard.py

# Check running processes
ps aux | grep -E "(vite|python.*manage)" | grep -v grep

# Check port usage
netstat -tlnp | grep -E ":(3000|8001)"

# Verify no forbidden port usage
netstat -tlnp | grep ":8000" && echo "❌ Port 8000 in use!" || echo "✅ Port 8000 free"
```

## 🚨 Troubleshooting

### Port 8000 Error
If you see port 8000 being used:
```bash
# Kill processes using port 8000
sudo lsof -ti:8000 | xargs kill -9
# Restart with correct configuration
export ATHENS_BACKEND_PORT=8001
./start_athens.sh
```

### Vite Port Switching
If Vite tries to use a different port:
- Check `VITE_PORT=3000` is set
- Verify `strictPort: true` in `vite.config.ts`
- Kill any process using port 3000: `sudo lsof -ti:3000 | xargs kill -9`

### Backend Won't Start
```bash
cd /var/www/athens/backend
source venv/bin/activate
python startup_guard.py  # This will show the exact error
```

## 📋 Emergency Recovery

```bash
# Complete system reset with correct ports
pkill -f vite
pkill -f "python.*manage.py"
export ATHENS_BACKEND_PORT=8001
export VITE_PORT=3000
./start_athens.sh
```