# Backend Test Instructions

## Current Issues Fixed:
1. ✅ **API URL**: Changed from localhost:5173 to localhost:8000
2. ✅ **ESG Overview Forms**: Added actual forms instead of placeholders
3. ✅ **Backend Configuration**: Environment app is properly configured

## Steps to Test:

### 1. Start Backend Server
```bash
cd backend
source venv/bin/activate  # or activate venv
python manage.py runserver 8000
```

### 2. Test API Endpoints
Open browser and test these URLs:
- http://localhost:8000/api/v1/environment/aspects/
- http://localhost:8000/api/v1/environment/reports/

Should return JSON responses, not 404 errors.

### 3. Check Database Migrations
```bash
cd backend
python manage.py showmigrations environment
```

If migrations are missing, run:
```bash
python manage.py makemigrations environment
python manage.py migrate
```

### 4. Test Frontend
1. Refresh browser (Ctrl+F5)
2. Navigate to ESG Management → ESG Overview
3. Click on Waste Management and Biodiversity tabs
4. Should now show forms instead of "coming soon"

### 5. Test Form Submission
1. Fill out any form
2. Click submit
3. Check browser console - should show success, not 404 errors

## Expected Results:
- ✅ Forms show in both Environment page and ESG Overview
- ✅ API calls go to localhost:8000 (not 5173)
- ✅ Form submissions work without 404 errors
- ✅ Report generation works

## If Still Getting 404 Errors:
1. Verify backend server is running on port 8000
2. Check if environment app URLs are included in main urls.py
3. Ensure migrations are applied
4. Check Django logs for errors