# PR9 - Notifications + Escalations Implementation

## ✅ Implementation Status: BACKEND COMPLETE

### Overview
Implemented comprehensive notification and escalation system for the Athens PTW module. Users now receive in-app notifications for key PTW events, and overdue tasks automatically escalate to higher authorities.

---

## 🎯 What Was Implemented

### 1. **Notification Utility** (`ptw/notification_utils.py`)

**Core Functions:**
- `create_ptw_notification()` - Create notifications with idempotency
- `generate_dedupe_key()` - Generate unique keys to prevent duplicates
- Event-specific helpers:
  - `notify_permit_created()`
  - `notify_permit_submitted()`
  - `notify_verifier_assigned()`
  - `notify_approver_assigned()`
  - `notify_permit_approved()`
  - `notify_permit_rejected()`
  - `notify_permit_activated()`
  - `notify_closeout_required()`
  - `notify_isolation_pending()`

**Features:**
- **Idempotency**: Uses MD5 hash of (user_id, event_type, permit_id, date) to prevent duplicates
- **Deduplication**: Checks for existing notifications before creating new ones
- **Settings-aware**: Respects `NOTIFICATIONS_ENABLED` setting
- **Structured data**: Includes permit_id, permit_number, permit_type in notification data
- **Deep links**: All notifications link to `/dashboard/ptw/view/{id}`

**Notification Types:**
```python
'ptw_created'              # Permit created
'ptw_submitted'            # Submitted for workflow
'ptw_verification'         # Verification required
'ptw_approval'             # Approval required
'ptw_approved'             # Approved
'ptw_rejected'             # Rejected
'ptw_activated'            # Work started
'ptw_completed'            # Work completed
'ptw_expired'              # Permit expired
'ptw_expiring'             # Expiring soon
'ptw_closeout_required'    # Closeout needed
'ptw_isolation_pending'    # Isolation verification pending
'ptw_escalated'            # Task escalated
'ptw_overdue'              # Task overdue
```

---

### 2. **Enhanced Celery Tasks** (`ptw/tasks.py`)

#### **check_overdue_workflow_tasks()**
- Runs every hour
- Checks `WorkflowStep` with status='pending' beyond time limits
- Uses `EscalationRule` model for permit-type-specific thresholds
- Falls back to 4-hour default if no rule exists
- Sends `ptw_overdue` notification to assignee
- Escalates to Grade A/B admins if 2x time limit exceeded
- Respects `ESCALATIONS_ENABLED` setting
- Implements deduplication per day

#### **auto_expire_permits()**
- Runs every hour
- Auto-expires active permits past `planned_end_time`
- Sends `ptw_expired` notification to creator
- Uses notification utility for consistency

#### **check_pending_closeout_and_isolation()** (NEW)
- Runs every 4 hours
- Checks active permits ending within 2 hours for closeout requirements
- Checks permits with unverified isolation points
- Sends proactive notifications

#### **cleanup_old_notifications()**
- Runs weekly
- Deletes PTW notifications older than 30 days

---

### 3. **Workflow Integration** (`ptw/workflow_views.py`)

**Notification Triggers Added:**

**initiate_workflow()**
- Sends `ptw_submitted` notification to creator

**assign_verifier()**
- Sends `ptw_verification` notification to assigned verifier

**verify_permit()**
- On approve: Sends `ptw_approval` notification to approver
- On reject: Sends `ptw_rejected` notification to creator

**approve_permit()**
- On approve: Sends `ptw_approved` notification to creator and verifier
- On reject: Sends `ptw_rejected` notification to creator

---

### 4. **Tests** (`ptw/tests/test_notifications.py`)

**Test Coverage:**
- ✅ `test_create_ptw_notification` - Basic notification creation
- ✅ `test_notification_idempotency` - Duplicate prevention
- ✅ `test_notify_permit_submitted` - Submission notification
- ✅ `test_notify_verifier_assigned` - Verifier assignment
- ✅ `test_notify_permit_approved` - Approval notification
- ✅ `test_escalation_task_creates_notification` - Escalation logic
- ✅ `test_escalation_idempotency` - No duplicate escalations
- ✅ `test_auto_expire_permits_task` - Auto-expiry with notification

---

### 5. **Management Command** (`ptw/management/commands/ptw_check_escalations.py`)

**Usage:**
```bash
python manage.py ptw_check_escalations
```

**Purpose:**
- Manual escalation checking
- Can be scheduled via cron/systemd timer
- Alternative to Celery beat for simple deployments

**Cron Example:**
```cron
# Check escalations every hour
0 * * * * cd /var/www/athens/app/backend && python manage.py ptw_check_escalations
```

---

## 📊 Notification Flow Examples

### **Example 1: Contractor Creates Permit**
1. User creates permit → `ptw_created` notification to creator
2. User submits → `ptw_submitted` notification to creator
3. System auto-assigns verifier → `ptw_verification` notification to verifier
4. Verifier approves → `ptw_approval` notification to approver
5. Approver approves → `ptw_approved` notification to creator + verifier

### **Example 2: Overdue Task Escalation**
1. Permit submitted at 9:00 AM
2. Verifier assigned, no action taken
3. At 1:00 PM (4 hours later):
   - Escalation task runs
   - `ptw_overdue` notification sent to verifier
4. At 5:00 PM (8 hours later):
   - Escalation task runs again
   - `ptw_escalated` notification sent to Grade A/B admins

### **Example 3: Permit Expiry**
1. Permit active, `planned_end_time` = 5:00 PM
2. At 5:00 PM:
   - Auto-expire task runs
   - Permit status → 'expired'
   - `ptw_expired` notification sent to creator

---

## 🔧 Configuration

### **Settings** (`backend/settings.py`)

Add these settings:

```python
# Notifications
NOTIFICATIONS_ENABLED = True  # Enable/disable all PTW notifications

# Escalations
ESCALATIONS_ENABLED = False  # Enable/disable escalation engine (default: False)
```

### **Celery Beat Schedule** (`backend/celery_app.py`)

Add to `beat_schedule`:

```python
'check-overdue-ptw-tasks': {
    'task': 'ptw.tasks.check_overdue_workflow_tasks',
    'schedule': crontab(minute=0),  # Every hour
},
'auto-expire-permits': {
    'task': 'ptw.tasks.auto_expire_permits',
    'schedule': crontab(minute=0),  # Every hour
},
'check-pending-closeout-isolation': {
    'task': 'ptw.tasks.check_pending_closeout_and_isolation',
    'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
},
'cleanup-old-ptw-notifications': {
    'task': 'ptw.tasks.cleanup_old_notifications',
    'schedule': crontab(minute=0, hour=0, day_of_week=0),  # Weekly on Sunday
},
```

### **Escalation Rules** (Django Admin)

Configure via Admin → PTW → Escalation Rules:

```
Permit Type: Electrical Work
Step Name: Verification
Time Limit: 4 hours
Escalate To Role: manager
Is Active: True
```

---

## 📁 Files Modified

1. **`app/backend/ptw/tasks.py`**
   - Updated imports to use notification utils
   - Enhanced `check_overdue_workflow_tasks()` with EscalationRule support
   - Updated `auto_expire_permits()` to use notification utility
   - Added `check_pending_closeout_and_isolation()` task
   - Lines modified: ~100

2. **`app/backend/ptw/workflow_views.py`**
   - Added notification triggers to `initiate_workflow()`
   - Added notification triggers to `assign_verifier()`
   - Added notification triggers to `verify_permit()`
   - Added notification triggers to `approve_permit()`
   - Lines modified: ~20

---

## 📁 Files Created

1. **`app/backend/ptw/notification_utils.py`** (~250 lines)
   - Core notification utility functions
   - Event-specific notification helpers
   - Idempotency and deduplication logic

2. **`app/backend/ptw/tests/test_notifications.py`** (~200 lines)
   - Comprehensive test suite
   - 8 test cases covering notifications and escalations

3. **`app/backend/ptw/management/commands/ptw_check_escalations.py`** (~20 lines)
   - Management command for manual escalation checking

4. **`PR9_BACKEND_SUMMARY.md`** (this file)
   - Complete implementation documentation

---

## ✅ Validation Commands

```bash
# Run tests
cd app/backend
python manage.py test ptw.tests.test_notifications

# Check for issues
python manage.py check

# Test management command
python manage.py ptw_check_escalations

# Test Celery tasks (if Celery running)
python manage.py shell
>>> from ptw.tasks import check_overdue_workflow_tasks
>>> check_overdue_workflow_tasks()
```

---

## 🚀 Deployment Steps

### **1. Enable Notifications**
```python
# backend/settings.py
NOTIFICATIONS_ENABLED = True
```

### **2. Configure Celery Beat** (if using Celery)
Add tasks to beat schedule as shown above, then restart:
```bash
systemctl restart celery-beat
```

### **3. OR Configure Cron** (if not using Celery)
```bash
# Add to crontab
crontab -e

# Add these lines:
0 * * * * cd /var/www/athens/app/backend && python manage.py ptw_check_escalations
0 */4 * * * cd /var/www/athens/app/backend && python manage.py shell -c "from ptw.tasks import check_pending_closeout_and_isolation; check_pending_closeout_and_isolation()"
```

### **4. Enable Escalations** (optional, after testing)
```python
# backend/settings.py
ESCALATIONS_ENABLED = True
```

### **5. Configure Escalation Rules**
- Login to Django Admin
- Navigate to PTW → Escalation Rules
- Create rules for each permit type
- Set appropriate time limits

---

## 🎯 Key Features

### **Idempotency**
- Notifications use dedupe keys based on (user, event, permit, date)
- Same notification won't be created twice in one day
- Escalation tasks check for existing notifications before creating new ones

### **Configurable**
- `NOTIFICATIONS_ENABLED` - Master switch for all notifications
- `ESCALATIONS_ENABLED` - Enable/disable escalation engine
- `EscalationRule` model - Per permit-type time limits
- `is_active` flag on rules - Easy enable/disable

### **Flexible Deployment**
- Works with Celery beat (recommended)
- Works with cron + management command (simple deployments)
- No breaking changes to existing code

### **Comprehensive Coverage**
- Workflow events (submit, verify, approve, reject)
- Status changes (activate, complete, expire)
- Compliance events (closeout required, isolation pending)
- Escalations (overdue, severely overdue)

---

## 📊 Statistics

**Lines Added:** ~470  
**Files Modified:** 2  
**Files Created:** 3  
**Test Cases:** 8  
**Notification Types:** 14  
**Celery Tasks:** 4 (1 new, 3 enhanced)  

---

## 🎉 PR9 Backend: COMPLETE

All backend components for notifications and escalations have been implemented and tested. The system provides comprehensive event tracking with intelligent deduplication and configurable escalation rules.

**Status:** ✅ Ready for frontend integration  
**Next:** Frontend notification bell + inbox page (optional, can use existing notification UI)
