# 🔧 ATHENS EHS SYSTEM - DEBUG PLAYBOOK

## 🚨 Emergency Response Guide

### If System is Down:
1. **Check Docker Status**: `./docker-status.sh`
2. **Check System Health**: `./diagnose_system.sh`
3. **Restart Services**: `./setup_https_config.sh`
4. **Check Logs**: `tail -f backend/backend.log frontend/frontend.log`

### If Users Can't Login:
1. **Start Here**: [Authentication Module Debug](#authentication-debug)
2. **Check JWT**: Verify token generation and validation
3. **Check Project Assignment**: User must have project assigned
4. **Check Database**: Verify user records exist

---

## 🔍 Module-Specific Debug Chains

### Authentication Debug
**Symptoms**: Login failures, permission errors, project access issues

**Debug Chain**:
1. **Check User Record**: `python manage.py shell` → `User.objects.get(username='...')`
2. **Verify Project Assignment**: User must have `project` field set
3. **Check JWT Generation**: `/api/auth/login/` endpoint response
4. **Validate Permissions**: Check `admin_type` and `user_type` fields
5. **Project Isolation**: Verify user's project matches data access

**Critical Files**:
- `backend/authentication/views.py` - Login logic
- `backend/authentication/models.py` - User model
- `backend/authentication/project_isolation.py` - Data filtering

**Common Fixes**:
```bash
# Reset user password
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='USER'); u.set_password('PASSWORD'); u.save()"

# Check project assignment
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='USER'); print(f'Project: {u.project}')"
```

### Induction Training Access Block
**Symptoms**: "Only EPC Safety Department users can access induction training"

**Exact Validation Chain**:
1. **Check User Type**: Must be `admin_type='epcuser'` OR `admin_type='master'`
2. **Check Project Assignment**: User must have `project` field set
3. **Check EPC Safety Function**: `is_epc_safety_user()` in views
4. **Verify Database**: User record has correct admin_type

**Debug Steps**:
```python
# Check user's admin_type
user = User.objects.get(username='USERNAME')
print(f"Admin Type: {user.admin_type}")
print(f"User Type: {user.user_type}")
print(f"Project: {user.project}")

# Fix admin_type
user.admin_type = 'epcuser'
user.save()
```

**Critical Validation**:
- File: `backend/inductiontraining/views.py`
- Function: `is_epc_safety_user()`
- Logic: `admin_type in ['master', 'epcuser']`

### Face Recognition Failures
**Symptoms**: Attendance marked as absent, low confidence scores

**Debug Chain**:
1. **Check Photo Existence**: Profile photos must exist in media folder
2. **Verify Confidence Threshold**: Default 65% (0.65)
3. **Check Photo Quality**: Clear, well-lit photos required
4. **Validate Face Detection**: Ensure faces are detected in both photos

**Debug Commands**:
```bash
# Check worker photos
ls -la media/worker_photos/

# Test face recognition endpoint
curl -X POST /api/induction-training/test-worker-photos/
```

### Project Isolation Failures
**Symptoms**: Users see data from other projects, empty querysets

**Debug Chain**:
1. **Verify User Project**: `user.project` must be set
2. **Check Model Fields**: Models must have `project` foreign key
3. **Validate Filtering**: `apply_project_isolation()` function
4. **Check ViewSet Mixins**: `ProjectIsolationMixin` usage

**Critical Validation**:
```python
# Check project isolation
user = User.objects.get(username='USERNAME')
print(f"User Project: {user.project}")

# Test isolation function
from authentication.project_isolation import apply_project_isolation
queryset = SomeModel.objects.all()
filtered = apply_project_isolation(queryset, user)
print(f"Total: {queryset.count()}, Filtered: {filtered.count()}")
```

### Permission Request Failures
**Symptoms**: Edit/delete buttons not working, permission denied errors

**Debug Chain**:
1. **Check Object Creator**: User can edit own objects
2. **Check Escalation Status**: Escalated objects restrict creator access
3. **Verify Permission Grant**: Active grant within 15-minute window
4. **Check Approval Chain**: ProjectAdmin → AdminUser relationship

**Debug Steps**:
```python
# Check object creator
obj = SomeModel.objects.get(id=OBJECT_ID)
print(f"Created by: {obj.created_by}")
print(f"Current user: {request.user}")

# Check active grants
from permissions.models import PermissionGrant
grants = PermissionGrant.objects.filter(
    permission_request__requester=user,
    used=False,
    expires_at__gt=timezone.now()
)
print(f"Active grants: {grants.count()}")
```

### Menu Access Issues
**Symptoms**: Menu items not showing, empty navigation

**Debug Chain**:
1. **Check Project Menu Access**: `ProjectMenuAccess` records
2. **Verify Module Enablement**: `is_enabled=True` for user's project
3. **Check Menu Configuration**: `MenuModule` records exist
4. **Validate API Response**: `/api/menu/user-menu-access/`

**Debug Commands**:
```python
# Check menu access
from authentication.menu_models import ProjectMenuAccess
access = ProjectMenuAccess.objects.filter(
    project=user.project,
    is_enabled=True
)
print(f"Enabled modules: {[a.menu_module.name for a in access]}")
```

---

## 🔧 Common System Issues

### Database Connection Issues
**Symptoms**: Database errors, connection timeouts

**Quick Fixes**:
```bash
# Restart database
docker-compose restart db

# Check database status
docker-compose ps

# Reset database (CAUTION)
docker-compose down
docker-compose up -d
```

### File Upload Failures
**Symptoms**: Photos not saving, file size errors

**Debug Chain**:
1. **Check File Size**: Must be under configured limits
2. **Verify File Type**: Only allowed extensions
3. **Check Media Directory**: Permissions and disk space
4. **Validate Base64 Encoding**: For face recognition photos

**Common Fixes**:
```bash
# Check media directory permissions
ls -la media/
chmod -R 755 media/

# Check disk space
df -h
```

### Docker Container Issues
**Symptoms**: Services not starting, port conflicts

**Debug Commands**:
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend

# Full system restart
docker-compose down && docker-compose up -d
```

---

## 📊 Performance Debug

### Slow API Responses
**Debug Chain**:
1. **Check Database Queries**: Use Django Debug Toolbar
2. **Verify Indexes**: Ensure proper database indexing
3. **Check Project Isolation**: Efficient filtering queries
4. **Monitor Memory Usage**: Container resource limits

### High Memory Usage
**Debug Steps**:
```bash
# Check container memory
docker stats

# Monitor Python memory
docker-compose exec backend python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

---

## 🚨 Emergency Contacts & Escalation

### Level 1: System Admin
- **Issue**: Service restarts, basic configuration
- **Tools**: Docker commands, log checking
- **Escalate If**: Database corruption, security breaches

### Level 2: Technical Lead  
- **Issue**: Code-level debugging, module failures
- **Tools**: Blueprint documentation, debug commands
- **Escalate If**: Architecture changes needed

### Level 3: Architecture Team
- **Issue**: System design changes, security updates
- **Tools**: Complete system blueprints
- **Authority**: Baseline change approval

---

## 📋 Debug Checklist Template

```markdown
## Issue Debug Checklist
- [ ] System health check completed
- [ ] Relevant module blueprint consulted
- [ ] User context verified (project, admin_type)
- [ ] Database records validated
- [ ] Log files examined
- [ ] Common fixes attempted
- [ ] Escalation criteria met
- [ ] Resolution documented
```

---

## 🔗 Quick Reference Links

### Critical Debug Files:
- **Authentication**: `backend/authentication/views.py`
- **Project Isolation**: `backend/authentication/project_isolation.py`
- **Permissions**: `backend/permissions/decorators.py`
- **Face Recognition**: `backend/shared/training_face_recognition.py`
- **Menu Access**: `backend/authentication/menu_views.py`

### System Commands:
- **Health Check**: `./diagnose_system.sh`
- **Docker Status**: `./docker-status.sh`
- **System Restart**: `./setup_https_config.sh`
- **Log Monitoring**: `tail -f backend/backend.log`

### Emergency Recovery:
```bash
# Complete system reset (LAST RESORT)
docker-compose down
docker system prune -f
docker-compose up -d
./setup_https_config.sh
```

---

**Debug Playbook Version**: 1.0  
**Last Updated**: January 2025  
**Next Review**: After major system changes  
**Escalation Authority**: Technical Architecture Team