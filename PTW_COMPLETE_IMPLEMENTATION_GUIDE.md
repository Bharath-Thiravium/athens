# PTW Module - Complete Implementation Guide

## Overview
The Permit to Work (PTW) module is a comprehensive safety management system with 17 completed PRs covering workflow, compliance, notifications, reporting, and integrations.

## Completed Features (PR1-PR17)

### Core Workflow (PR1-PR6)
- ✅ Status management (draft → submitted → verified → approved → active → completed)
- ✅ Multi-level approval workflow
- ✅ Gas testing requirements and validation
- ✅ PPE and safety checklist enforcement
- ✅ Extension management with limits

### Advanced Features (PR7-PR14)
- ✅ **PR7**: Closeout checklist with completion gating
- ✅ **PR8**: Structured isolation points (LOTO) with verification
- ✅ **PR9**: Notifications + escalations system
- ✅ **PR10**: KPI dashboard with overdue alerts
- ✅ **PR11**: Audit-ready PDF/Excel exports + bulk export
- ✅ **PR12**: Offline sync with conflict resolution
- ✅ **PR13**: Rate limiting + observability + health endpoint
- ✅ **PR14**: Multi-tenant filters + server pagination

### UX & Reporting (PR15-PR17)
- ✅ **PR15**: Readiness endpoint + frontend UX improvements
- ✅ **PR16**: Compliance reporting (summary + exceptions)
- ✅ **PR17**: Webhooks for external integrations

## Architecture

### Backend Stack
- Django 4.x + Django REST Framework
- PostgreSQL database
- Celery for background tasks
- Redis for caching

### Frontend Stack
- React 18 + TypeScript
- Vite build tool
- Ant Design UI components
- Zustand for state management

## Key Endpoints

### Permits
- `GET /api/v1/ptw/permits/` - List permits (paginated, filtered)
- `POST /api/v1/ptw/permits/` - Create permit
- `GET /api/v1/ptw/permits/{id}/` - Get permit details
- `GET /api/v1/ptw/permits/{id}/readiness/` - Check readiness for transitions
- `POST /api/v1/ptw/permits/{id}/update_status/` - Update status

### Workflow
- `POST /api/v1/ptw/permits/{id}/workflow/initiate/` - Start workflow
- `POST /api/v1/ptw/permits/{id}/workflow/verify/` - Verify permit
- `POST /api/v1/ptw/permits/{id}/workflow/approve/` - Approve permit

### Isolation Points
- `GET /api/v1/ptw/isolation-points/` - List isolation points
- `GET /api/v1/ptw/permits/{id}/isolation/` - Get permit isolation
- `POST /api/v1/ptw/permits/{id}/assign_isolation/` - Assign points
- `POST /api/v1/ptw/permits/{id}/update_isolation/` - Update isolation status

### Closeout
- `GET /api/v1/ptw/permits/{id}/closeout/` - Get closeout checklist
- `POST /api/v1/ptw/permits/{id}/update_closeout/` - Update checklist
- `POST /api/v1/ptw/permits/{id}/complete_closeout/` - Complete closeout

### Reporting & Analytics
- `GET /api/v1/ptw/permits/kpis/` - Get KPI dashboard data
- `GET /api/v1/ptw/permits/reports_summary/` - Compliance summary
- `GET /api/v1/ptw/permits/reports_exceptions/` - Exception report

### Exports
- `GET /api/v1/ptw/permits/{id}/export_pdf/` - Export single PDF
- `GET /api/v1/ptw/permits/export_excel/` - Export Excel
- `POST /api/v1/ptw/permits/bulk_export_pdf/` - Bulk PDF ZIP
- `POST /api/v1/ptw/permits/bulk_export_excel/` - Bulk Excel

### Webhooks
- `GET /api/v1/ptw/webhooks/` - List webhook endpoints
- `POST /api/v1/ptw/webhooks/` - Create webhook
- `POST /api/v1/ptw/webhooks/{id}/test/` - Test webhook

## Database Models

### Core Models
- `Permit` - Main permit record
- `PermitType` - Permit type configuration
- `WorkflowInstance` - Workflow state
- `WorkflowStep` - Individual workflow steps

### Safety & Compliance
- `GasReading` - Gas test results
- `PermitHazard` - Identified hazards
- `PermitWorker` - Assigned workers
- `DigitalSignature` - Electronic signatures

### Isolation Management
- `IsolationPointLibrary` - Master catalog
- `PermitIsolationPoint` - Permit-level assignments

### Closeout
- `CloseoutChecklistTemplate` - Checklist templates
- `PermitCloseout` - Closeout tracking

### Audit & Integration
- `PermitAudit` - Audit trail
- `WebhookEndpoint` - Webhook configurations
- `WebhookDeliveryLog` - Delivery tracking

## Configuration

### Settings (backend/settings.py)
```python
# Throttling
PTW_SYNC_RATE = "60/min"
PTW_BULK_EXPORT_RATE = "5/hour"
PTW_KPI_RATE = "120/min"

# SLA Thresholds
PTW_VERIFICATION_SLA_HOURS = 4
PTW_APPROVAL_SLA_HOURS = 4
PTW_EXPIRING_SOON_HOURS = 4

# Limits
PTW_BULK_EXPORT_LIMIT = 200

# Features
NOTIFICATIONS_ENABLED = True
ESCALATIONS_ENABLED = False  # Enable after testing
```

### Celery Tasks
```python
# Escalation checks (hourly)
'check-overdue-ptw-tasks': {
    'task': 'ptw.tasks.check_overdue_workflow_tasks',
    'schedule': crontab(minute=0),
}

# Auto-expire permits (every 10 minutes)
'auto-expire-permits': {
    'task': 'ptw.tasks.auto_expire_permits',
    'schedule': crontab(minute='*/10'),
}
```

## Testing

### Backend Tests
```bash
cd app/backend
python manage.py test ptw.tests.test_readiness_endpoint
python manage.py test ptw.tests.test_reports
python manage.py test ptw.tests.test_webhooks
python manage.py test ptw.tests.test_filters_and_pagination
python manage.py test ptw.tests.test_throttling
python manage.py test ptw.tests.test_permissions_regression
```

### Frontend Build
```bash
cd app/frontend
npm run build
```

## Deployment Checklist

1. **Database Migration**
   ```bash
   python manage.py migrate ptw
   ```

2. **Create Superuser** (if needed)
   ```bash
   python manage.py createsuperuser
   ```

3. **Load Initial Data**
   ```bash
   python manage.py create_permit_types
   ```

4. **Configure Celery Beat**
   - Ensure Redis is running
   - Start Celery worker and beat

5. **Build Frontend**
   ```bash
   cd app/frontend && npm run build
   ```

6. **Configure Nginx**
   - Serve frontend from dist/
   - Proxy /api/ to Django

7. **Enable Features**
   - Set ESCALATIONS_ENABLED = True after testing
   - Configure webhook endpoints via admin

## Troubleshooting

### Common Issues

**PostgreSQL Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection settings
grep -A 5 "DATABASES" backend/settings.py
```

**Celery Not Running**
```bash
# Check Celery status
ps aux | grep celery

# Restart Celery
pkill -f celery
celery -A backend worker -l info &
celery -A backend beat -l info &
```

**Frontend Build Errors**
```bash
# Clear cache and rebuild
cd app/frontend
rm -rf node_modules dist
npm install
npm run build
```

## Security Considerations

1. **Project Scoping**: All endpoints enforce project-level access control
2. **Rate Limiting**: Throttling prevents abuse of high-load endpoints
3. **Webhook Signing**: HMAC SHA256 signatures for webhook payloads
4. **Audit Trail**: All actions logged in PermitAudit table
5. **Permission Checks**: Role-based access control throughout

## Performance Optimization

1. **Pagination**: All list endpoints use server-side pagination (20 items/page)
2. **Filtering**: Efficient database queries with proper indexes
3. **Caching**: Redis caching for frequently accessed data
4. **Prefetching**: select_related/prefetch_related to avoid N+1 queries
5. **Bulk Operations**: Optimized bulk export with streaming

## Monitoring

### Health Endpoint
```bash
curl -H "Authorization: Bearer <token>" \
  https://your-domain.com/api/v1/ptw/health/
```

Returns:
- Sync statistics (last 24h)
- Workflow overdue counts
- Job run status

### Logs
- Application logs: `/var/log/athens/ptw.log`
- Celery logs: `/var/log/athens/celery.log`
- Nginx logs: `/var/log/nginx/access.log`

## Support

For issues or questions:
1. Check validation scripts: `./validate_pr*.sh`
2. Review PR summaries: `PR*_SUMMARY.md`
3. Check Django admin: `/admin/ptw/`
4. Review audit logs in database

## Version History

- **v1.0** (PR1-PR6): Core workflow and compliance
- **v1.5** (PR7-PR10): Advanced features and reporting
- **v2.0** (PR11-PR14): Production hardening
- **v2.5** (PR15-PR17): UX improvements and integrations
