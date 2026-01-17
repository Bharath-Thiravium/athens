# PR12 Deployment Checklist

## Pre-Deployment

- [x] Backend code complete
- [x] Frontend code complete
- [x] Tests written
- [x] Validation script passes (12/12)
- [x] Python syntax valid
- [x] Documentation complete

## Deployment Steps

### 1. Run Migration
```bash
cd /var/www/athens/app/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=backend.settings
python manage.py migrate ptw
```

Expected output:
- Creates `version` field on Permit, PermitIsolationPoint, PermitCloseout
- Creates `ptw_applied_offline_change` table with unique constraint

### 2. Run Tests
```bash
cd /var/www/athens/app/backend
python manage.py test ptw.tests.test_offline_sync_conflicts
```

Expected: 9 tests pass

### 3. Update Frontend Hook Import
Replace old `useOfflineSync.ts` import with new `useOfflineSync2.ts` in components that use it:

```typescript
// Old
import { useOfflineSync } from '../hooks/useOfflineSync';

// New
import { useOfflineSync } from '../hooks/useOfflineSync2';
```

Or rename `useOfflineSync2.ts` to `useOfflineSync.ts` (backup old one first).

### 4. Add Sync Status Indicator to Layout
In PTW layout or PermitList header:
```typescript
import { SyncStatusIndicator } from '@features/ptw/components/SyncStatusIndicator';

// Add to header
<SyncStatusIndicator />
```

### 5. Add Conflicts Route
In PTW routes:
```typescript
import { SyncConflictsPage } from '@features/ptw/components/SyncConflictsPage';

// Add route
<Route path="/dashboard/ptw/sync-conflicts" element={<SyncConflictsPage />} />
```

### 6. Export New Components
In `app/frontend/src/features/ptw/components/index.ts`:
```typescript
export { SyncStatusIndicator } from './SyncStatusIndicator';
export { SyncConflictsPage } from './SyncConflictsPage';
```

### 7. Build Frontend
```bash
cd /var/www/athens/app/frontend
npm run build
```

Expected: Build succeeds

### 8. Restart Services
```bash
# Backend
pkill -f "python.*manage.py"
cd /var/www/athens/app/backend
source venv/bin/activate
export ATHENS_BACKEND_PORT=8001
python manage.py runserver 0.0.0.0:${ATHENS_BACKEND_PORT} &

# Frontend (if needed)
cd /var/www/athens/app/frontend
npm run dev &
```

## Post-Deployment Testing

### Manual Test Scenarios

#### 1. Version Increment Test
1. Create a permit via API
2. Note the version (should be 1)
3. Update the permit
4. Check version incremented to 2

#### 2. Conflict Detection Test
1. Create permit with version 1
2. Update server-side to version 2
3. Try to sync offline change with client_version=1
4. Should receive conflict response

#### 3. Idempotency Test
1. Sync a change with offline_id="test_123"
2. Sync same change again
3. Should return "already_applied" status

#### 4. Frontend Queue Test
1. Go offline (disable network in DevTools)
2. Make permit update
3. Check queue has pending item
4. Go online
5. Should auto-sync and mark as synced

#### 5. Conflict Resolution UI Test
1. Create conflict (stale version)
2. Navigate to /dashboard/ptw/sync-conflicts
3. Should see conflict listed
4. Test "Keep Mine", "Use Server", "Auto Merge" buttons

## Rollback Plan

If issues occur:

### 1. Rollback Migration
```bash
cd /var/www/athens/app/backend
python manage.py migrate ptw 0008_isolation_points
```

### 2. Revert Code Changes
```bash
cd /var/www/athens
git checkout HEAD~1 app/backend/ptw/models.py
git checkout HEAD~1 app/backend/ptw/views.py
```

### 3. Use Old Frontend Hook
Revert to old `useOfflineSync.ts` implementation

## Monitoring

After deployment, monitor:
- AppliedOfflineChange table growth (should be reasonable)
- Conflict rate (check logs for conflicts)
- Sync success rate
- Version field values (should increment properly)

## Known Limitations

1. **Photo Upload**: Current implementation doesn't handle actual file upload in sync endpoint (simplified for MVP)
2. **Large Payloads**: localStorage has ~5-10MB limit; consider IndexedDB for production
3. **Merge Strategies**: Currently supports set_merge and true_wins; custom strategies may be needed
4. **Real-time**: No WebSocket notifications for conflicts; user must check manually

## Future Improvements

1. Implement photo file handling in sync endpoint
2. Migrate queue storage to IndexedDB
3. Add WebSocket notifications for conflicts
4. Add conflict analytics dashboard
5. Implement server-side auto-merge
6. Add bulk conflict resolution
7. Add conflict resolution history/audit

## Support

For issues:
1. Check validation script: `./validate_pr12.sh`
2. Check Django logs for sync errors
3. Check browser console for frontend errors
4. Review PR12_SUMMARY.md for implementation details
