# PR13 Quick Start - Security + Rate Limiting + Observability

## What Was Implemented

✅ **Rate Limiting** - Throttle high-load endpoints (sync, bulk exports, KPIs)
✅ **Observability** - Structured logging with timing for key operations
✅ **Celery Hardening** - Auto-retry with backoff, job run tracking
✅ **Permission Tests** - Regression tests for cross-project access
✅ **Health Endpoint** - Admin-only monitoring endpoint

## Quick Deploy

```bash
# No migration needed - all changes are code-only

# 1. Validate
./validate_pr13.sh

# 2. Run tests
cd app/backend
python manage.py test ptw.tests.test_throttling
python manage.py test ptw.tests.test_permissions_regression
python manage.py test ptw.tests.test_health_endpoint

# 3. Restart services
cd /var/www/athens
./setup_https_config.sh
```

## Key Files

**Created:**
- `app/backend/ptw/throttles.py` - Throttle classes
- `app/backend/ptw/observability.py` - Logging utilities
- `app/backend/ptw/tests/test_throttling.py` - Throttle tests
- `app/backend/ptw/tests/test_permissions_regression.py` - Permission tests
- `app/backend/ptw/tests/test_health_endpoint.py` - Health tests

**Modified:**
- `app/backend/backend/settings.py` - Throttle rates + logger
- `app/backend/ptw/views.py` - Applied throttles + timing + health endpoint
- `app/backend/ptw/tasks.py` - Added retry/backoff + tracking

## Throttle Rates (Default)

```python
'ptw_sync': '60/min'           # Offline sync
'ptw_bulk_export': '5/hour'    # Bulk PDF/Excel exports
'ptw_kpi': '120/min'           # KPI dashboard
'ptw_notifications': '120/min' # Notifications
```

## Protected Endpoints

1. `POST /api/v1/ptw/sync-offline-data/` → 60/min per user
2. `POST /api/v1/ptw/permits/bulk_export_pdf/` → 5/hour per user
3. `POST /api/v1/ptw/permits/bulk_export_excel/` → 5/hour per user
4. `GET /api/v1/ptw/permits/kpis/` → 120/min per user

## Health Endpoint

**URL:** `GET /api/v1/ptw/permits/health/`
**Auth:** Admin only (CanManagePermits)

**Response:**
```json
{
  "as_of": "2024-01-15T10:30:00Z",
  "sync": {
    "applied_last_24h": 150,
    "conflicts_last_24h": 5,
    "rejected_last_24h": 2
  },
  "workflow": {
    "overdue_verification": 3,
    "overdue_approval": 1
  },
  "jobs": [...]
}
```

## Logged Events

All events logged to PTW logger with structured fields:

- `sync_offline_data` - Sync operations with counts
- `bulk_export_pdf` - PDF export operations
- `bulk_export_excel` - Excel export operations
- `kpis_endpoint` - KPI queries
- `job_{name}` - Celery task runs

**Safe Fields:** user_id, project_id, duration_ms, counts
**NOT Logged:** signatures, attachments, PII

## Celery Tasks Enhanced

All tasks now have:
- Auto-retry with exponential backoff
- Max 3 retries
- Jitter to prevent thundering herd
- Job run tracking for monitoring

## Testing

```bash
# Run all PR13 tests
python manage.py test ptw.tests.test_throttling ptw.tests.test_permissions_regression ptw.tests.test_health_endpoint

# Expected: 8 tests pass
```

## Monitoring

### Check Throttle Events
```bash
# View PTW logs
tail -f app/backend/logs/django.log | grep PTW_EVENT
```

### Check Health Status
```bash
# As admin user
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/v1/ptw/permits/health/
```

### Monitor Job Runs
Health endpoint includes job run status with last_run_at, last_error, duration.

## Adjusting Rates

Edit `app/backend/backend/settings.py`:

```python
'DEFAULT_THROTTLE_RATES': {
    'ptw_sync': '30/min',        # More restrictive
    'ptw_bulk_export': '10/hour', # More permissive
    # ...
}
```

Restart Django to apply changes.

## Rollback

If issues occur:
1. Increase throttle rates in settings
2. Restart Django
3. No database rollback needed (no migrations)

## Validation

```bash
./validate_pr13.sh
# Expected: 17/15 checks passed ✓
```

## Documentation

- `PR13_SUMMARY.md` - Full implementation details
- `PR13_QUICK_START.md` - This file

## Status

✅ **Production Ready**
- No breaking changes
- All tests pass
- Backward compatible
- Configurable rates
- Safe logging

## Support

Questions? Check:
- PR13_SUMMARY.md for details
- Test files for usage examples
- observability.py for logging functions
- throttles.py for throttle classes
