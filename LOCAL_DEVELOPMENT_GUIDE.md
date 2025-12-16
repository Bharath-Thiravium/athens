# 🛠️ **EHS Management System - Local Development Guide**

## 🚀 **Quick Start**

### **Prerequisites**
- PostgreSQL 12+ installed and running
- Node.js 18+ installed
- Python 3.11+ with virtual environment

### **1. Start PostgreSQL**
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check if running
pg_isready -h localhost -p 5432 -U postgres
```

### **2. Start the Application**
```bash
# Option 1: Automated startup
./start_local_dev.sh

# Option 2: Manual startup
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2 - Frontend
cd frontedn
npm run dev
```

### **3. Access the Application**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

---

## 🔧 **Configuration Details**

### **Environment Configuration**
The system is configured for local development with:
- **DEBUG**: True (development mode)
- **Database**: PostgreSQL (localhost:5432)
- **CORS**: Enabled for localhost:5173
- **SSL**: Disabled for local development
- **WebSocket**: Enabled for real-time notifications

### **Database Settings**
```bash
DB_NAME=final
DB_USER=postgres
DB_PASSWORD=apple
DB_HOST=localhost
DB_PORT=5432
```

---

## 🐛 **Common Issues & Solutions**

### **1. Database Connection Issues**

**Problem**: `django.db.utils.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if not running
sudo systemctl start postgresql

# Check if database exists
psql -U postgres -c "\l" | grep final

# Create database if missing
psql -U postgres -c "CREATE DATABASE final;"

# Test connection
psql -U postgres -d final -c "SELECT version();"
```

### **2. Migration Issues**

**Problem**: Migration errors or "no such table" errors

**Solutions**:
```bash
cd backend
source venv/bin/activate

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset migrations (if needed)
python manage.py migrate --fake-initial
```

### **3. WebSocket Authentication Issues**

**Problem**: WebSocket connections rejected with 403 errors

**Solutions**:
- ✅ **FIXED**: Local development settings now properly configured
- Ensure you're logged in to the frontend
- Check that JWT tokens are valid
- Verify CORS settings allow WebSocket connections

### **4. CORS Issues**

**Problem**: Frontend can't connect to backend API

**Solutions**:
```bash
# Verify CORS settings in backend/.env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Restart backend server after changes
```

### **5. Frontend Build Issues**

**Problem**: Frontend won't start or build errors

**Solutions**:
```bash
cd frontedn

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite

# Start development server
npm run dev
```

### **6. Port Already in Use**

**Problem**: `Error: listen EADDRINUSE: address already in use :::8000`

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
python manage.py runserver 0.0.0.0:8001
```

---

## 📊 **Development Tools**

### **Database Management**
```bash
# Access PostgreSQL shell
psql -U postgres -d final

# View all tables
\dt

# View specific table
\d authentication_user

# Exit PostgreSQL shell
\q
```

### **Django Management Commands**
```bash
cd backend
source venv/bin/activate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test

# Check for issues
python manage.py check
```

### **Frontend Development**
```bash
cd frontedn

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint

# Run type checking
npm run type-check
```

---

## 🔍 **Debugging Tips**

### **Backend Debugging**
1. **Check Django logs** in the terminal running the server
2. **Use Django Debug Toolbar** (already installed in development)
3. **Check database queries** with Django's logging
4. **Use Python debugger**: Add `import pdb; pdb.set_trace()` in your code

### **Frontend Debugging**
1. **Browser Developer Tools**: F12 → Console/Network tabs
2. **React Developer Tools**: Install browser extension
3. **Vite logs**: Check terminal running `npm run dev`
4. **Network requests**: Monitor API calls in browser

### **WebSocket Debugging**
1. **Browser Network tab**: Filter by WS (WebSocket)
2. **Check authentication**: Verify JWT token in WebSocket URL
3. **Backend logs**: Monitor WebSocket connection logs
4. **Test WebSocket**: Use browser console or WebSocket testing tools

---

## 🚀 **Performance Optimization**

### **Development Performance**
```bash
# Backend optimizations
export DJANGO_DEBUG=True
export DJANGO_LOG_LEVEL=INFO

# Frontend optimizations
export VITE_DEBUG=true
export NODE_ENV=development
```

### **Database Performance**
```bash
# PostgreSQL optimizations for development
# Add to postgresql.conf:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
```

---

## 📞 **Getting Help**

### **Log Locations**
- **Django logs**: Terminal output or `backend/logs/`
- **PostgreSQL logs**: `/var/log/postgresql/`
- **Vite logs**: Terminal output
- **Browser logs**: F12 → Console

### **Useful Commands**
```bash
# Check system status
./start_local_dev.sh --check

# Reset everything
./reset_local_dev.sh

# View logs
tail -f backend/logs/django.log
```

---

## ✅ **Verification Checklist**

Before reporting issues, verify:
- [ ] PostgreSQL is running and accessible
- [ ] Database 'final' exists and is accessible
- [ ] Virtual environment is activated
- [ ] All migrations are applied
- [ ] Frontend dependencies are installed
- [ ] No port conflicts (8000, 5173)
- [ ] CORS settings are correct
- [ ] Environment variables are set

---

**🎯 Your system is now configured for local development with PostgreSQL!**

**Next Steps:**
1. Run `./start_local_dev.sh` to start both servers
2. Access http://localhost:5173 for the frontend
3. Login with your existing credentials
4. All WebSocket and API connections should work properly
