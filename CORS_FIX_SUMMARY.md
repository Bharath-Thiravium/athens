# CORS Error Fix Summary

## Root Cause

The CORS (Cross-Origin Resource Sharing) error was caused by a **security policy violation**:

### Error Message
```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at 'https://prozeal.athenas.co.in/authentication/notifications/'. 
(Reason: Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '*').
```

### Why This Happened

1. **Frontend Configuration** (`/var/www/athens/app/frontend/src/common/utils/axiosetup.ts`):
   - Configured with `withCredentials: true` to send cookies and authentication headers
   - Base URL: `https://prozeal.athenas.co.in`

2. **Backend Misconfiguration** (`/var/www/athens/app/backend/backend/settings.py`):
   - Line 130: `CORS_ALLOW_CREDENTIALS = True` ✓ (Correct - allows credentials)
   - Line 145: `CORS_ALLOW_ALL_ORIGINS = True` ✗ (CONFLICT - sends `Access-Control-Allow-Origin: *`)

3. **Browser Security Policy**:
   - When credentials are included in requests (`withCredentials: true`), browsers enforce:
     - ✓ `Access-Control-Allow-Credentials: true`
     - ✗ `Access-Control-Allow-Origin` **CANNOT be `*`** (must be a specific origin)

This is a security measure to prevent CSRF (Cross-Site Request Forgery) attacks.

---

## The Fix

### Changes Made

#### 1. **Django Settings** (`/var/www/athens/app/backend/backend/settings.py`)

**Removed line 145:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # Temporarily allow all origins  ← REMOVED
```

**Kept proper configuration:**
```python
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1', 'yes', 'on')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if os.getenv('CORS_ALLOWED_ORIGINS') else []
```

Now `CORS_ALLOW_ALL_ORIGINS` defaults to `False` and can only be enabled via environment variable.

#### 2. **Environment Variables** (`/var/www/athens/app/backend/.env`)

**Changed from:**
```
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://prozeal.athenas.co.in,https://rayzen.athenas.co.in,https://sap.athenas.co.in
```

**Changed to:**
```
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://prozeal.athenas.co.in,https://rayzen.athenas.co.in,https://sap.athenas.co.in
```

#### 3. **Production Environment** (`/var/www/athens/app/backend/.env.production`)

**Updated CORS configuration:**
```
CORS_ALLOWED_ORIGINS=https://prozeal.athenas.co.in,https://rayzen.athenas.co.in,https://sap.athenas.co.in
CSRF_TRUSTED_ORIGINS=https://prozeal.athenas.co.in,https://rayzen.athenas.co.in,https://sap.athenas.co.in
```

---

## How It Works Now

1. **Backend receives request** from `https://prozeal.athenas.co.in`
2. **Django CORS middleware checks** if origin is in `CORS_ALLOWED_ORIGINS`
3. **If match found**, responds with:
   ```
   Access-Control-Allow-Origin: https://prozeal.athenas.co.in
   Access-Control-Allow-Credentials: true
   ```
4. **Browser allows request** with credentials (cookies, JWT tokens, etc.)
5. **No CORS errors** ✓

---

## Allowed Origins (Production)

The system now supports these origins:

- `https://prozeal.athenas.co.in` (Main Athens instance)
- `https://rayzen.athenas.co.in` (Rayzen instance)
- `https://sap.athenas.co.in` (SAP integration instance)

For local development:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

---

## To Apply Changes

### Option 1: Restart Backend Service
```bash
systemctl restart athens-uvicorn
```

### Option 2: Manual Restart (Development)
```bash
cd /var/www/athens/backend
source venv/bin/activate
pkill -f "python.*manage.py"
export ATHENS_BACKEND_PORT=8001
python startup_guard.py
python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT}
```

---

## Why This Fix Maintains Security

✓ **CORS_ALLOW_CREDENTIALS = True** - Allows authenticated requests  
✓ **Specific CORS_ALLOWED_ORIGINS** - Only trusted domains can make requests  
✓ **No wildcard (*) allowed** - Prevents CSRF attacks  
✓ **CSRF_TRUSTED_ORIGINS** - Additional CSRF token validation layer  

This is the **secure way** to handle CORS with credentials, recommended by:
- MDN Web Docs
- OWASP Security Guidelines
- Browser security standards (SOP - Same Origin Policy)

---

## Verification

After applying the fix, notification requests to `/authentication/notifications/` should work without CORS errors. Check browser DevTools Network tab to verify:

**Expected Response Headers:**
```
Access-Control-Allow-Origin: https://prozeal.athenas.co.in
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
```

**No more errors like:**
- `Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '*'`
- `Cross-Origin Request Blocked`
