# Quick Deployment Guide

## Environment Configuration

**For venv production setup:**

### Database Configuration
- **DB_HOST**: `localhost` (PostgreSQL running locally)
- **Environment File**: `/var/www/athens/app/backend/.env.production`
- **Database**: `athens_db`
- **User**: `athens_user`

### One-Command Deployment

```bash
cd /var/www/athens
./deploy_ptw_updates.sh
```

This script will:
1. Load `.env.production` 
2. Run migrations with correct DB_HOST=localhost
3. Rebuild frontend
4. Restart backend

---

## Manual Deployment (If Script Fails)

### Step 1: Run Migrations
```bash
cd /var/www/athens/app/backend
source venv/bin/activate
export $(cat .env.production | grep -v '^#' | xargs)
python3 manage.py migrate ptw
```

### Step 2: Rebuild Frontend
```bash
cd /var/www/athens/app/frontend
npm run build
```

### Step 3: Restart Backend
```bash
cd /var/www/athens/app/backend
source venv/bin/activate
export $(cat .env.production | grep -v '^#' | xargs)
export ATHENS_BACKEND_PORT=8001

pkill -f "python.*manage.py runserver"
nohup python3 manage.py runserver 0.0.0.0:8001 > /var/log/athens_backend.log 2>&1 &
```

---

## Verification

### Check Migrations Applied
```bash
cd /var/www/athens/app/backend
source venv/bin/activate
export $(cat .env.production | grep -v '^#' | xargs)
python3 manage.py showmigrations ptw | grep "\[X\]"
```

Should show:
```
[X] 0009_webhooks
[X] 0010_canonicalize_permit_statuses
```

### Check Frontend Build
```bash
stat /var/www/athens/app/frontend/dist/index.html
# Should show recent timestamp

grep -r "ReadinessPanel" /var/www/athens/app/frontend/dist/assets/*.js
# Should find matches
```

### Check Backend Running
```bash
curl http://localhost:8001/api/v1/ptw/permits/ | head -20
# Should return JSON

curl http://localhost:8001/api/v1/ptw/webhooks/
# Should return empty list or webhooks
```

### Check Logs
```bash
tail -f /var/log/athens_backend.log
```

---

## Troubleshooting

### Migration Fails: "could not translate host name 'database'"
**Cause**: Using an environment file with DB_HOST=database  
**Fix**: Use `.env.production` which has DB_HOST=localhost

### Migration Fails: "SECRET_KEY must be set"
**Cause**: Environment not loaded  
**Fix**: `export $(cat .env.production | grep -v '^#' | xargs)`

### Frontend Build Fails
**Cause**: Missing dependencies  
**Fix**: `cd app/frontend && npm install && npm run build`

### Backend Won't Start
**Cause**: Port already in use  
**Fix**: `pkill -f "python.*manage.py" && sleep 2 && restart`

---

## Rollback (If Needed)

### Rollback Migrations
```bash
cd /var/www/athens/app/backend
source venv/bin/activate
export $(cat .env.production | grep -v '^#' | xargs)

# Rollback to before webhooks
python3 manage.py migrate ptw 0009_add_version_and_idempotency
```

### Rollback Frontend
```bash
cd /var/www/athens
git checkout HEAD~1 app/frontend/src/features/ptw/components/
cd app/frontend && npm run build
```

---

## Summary

**Correct Setup for Production (venv)**:
- Environment: `.env.production` in `app/backend/`
- DB Host: `localhost` (not "database")
- Run from: `/var/www/athens/`
- Script: `./deploy_ptw_updates.sh`

**Estimated Time**: 2-3 minutes  
**Downtime**: ~30 seconds (backend restart only)
