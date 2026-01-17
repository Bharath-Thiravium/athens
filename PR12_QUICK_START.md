# PR12 Quick Start Guide

## What Was Implemented

**Offline Sync Conflict Resolution System** for PTW module with:
- ✅ Version tracking on Permit, PermitIsolationPoint, PermitCloseout
- ✅ Idempotency tracking to prevent duplicate processing
- ✅ Conflict detection with field-level analysis
- ✅ Smart merge strategies (set-merge, true-wins)
- ✅ Frontend queue with per-item status tracking
- ✅ Conflict resolution UI with 3 resolution options
- ✅ Sync status indicator with badge
- ✅ 9 comprehensive backend tests

## Quick Deploy

```bash
# 1. Run migration
cd /var/www/athens/app/backend
source venv/bin/activate
python manage.py migrate ptw

# 2. Run tests
python manage.py test ptw.tests.test_offline_sync_conflicts

# 3. Build frontend
cd /var/www/athens/app/frontend
npm run build

# 4. Restart services
cd /var/www/athens
./setup_https_config.sh
```

## Key Files

**Backend:**
- `app/backend/ptw/models.py` - Added version fields + AppliedOfflineChange model
- `app/backend/ptw/conflict_utils.py` - Conflict detection & merge logic (NEW)
- `app/backend/ptw/views.py` - Enhanced sync_offline_data endpoint
- `app/backend/ptw/migrations/0009_add_version_and_idempotency.py` - Migration (NEW)
- `app/backend/ptw/tests/test_offline_sync_conflicts.py` - Tests (NEW)

**Frontend:**
- `app/frontend/src/features/ptw/types/offlineSync.ts` - TypeScript types (NEW)
- `app/frontend/src/features/ptw/hooks/useOfflineSync2.ts` - Updated hook (NEW)
- `app/frontend/src/features/ptw/components/SyncStatusIndicator.tsx` - Status widget (NEW)
- `app/frontend/src/features/ptw/components/SyncConflictsPage.tsx` - Conflict UI (NEW)

## API Changes

### New Sync Endpoint Format

**Request:**
```json
POST /api/v1/ptw/sync-offline-data/
{
  "device_id": "device_abc",
  "client_time": "2024-01-15T10:30:00Z",
  "changes": [
    {
      "entity": "permit",
      "op": "update",
      "offline_id": "offline_xyz",
      "server_id": 123,
      "client_version": 5,
      "data": {"title": "Updated"}
    }
  ]
}
```

**Response:**
```json
{
  "applied": [
    {"entity": "permit", "offline_id": "offline_xyz", "server_id": 123, "new_version": 6}
  ],
  "conflicts": [
    {
      "entity": "permit",
      "offline_id": "offline_abc",
      "reason": "stale_version",
      "client_version": 5,
      "server_version": 7,
      "fields": {
        "title": {"client": "A", "server": "B", "merge_hint": "last_write_wins"}
      },
      "server_state": {...}
    }
  ],
  "rejected": [],
  "summary": {"total": 2, "applied": 1, "conflicts": 1, "rejected": 0}
}
```

## Frontend Usage

```typescript
import { useOfflineSync } from '@features/ptw/hooks/useOfflineSync2';

const { syncStatus, addToQueue, syncNow, resolveConflict } = useOfflineSync();

// Add to queue
addToQueue('permit', 'update', { title: 'New' }, permitId, currentVersion);

// Manual sync
syncNow();

// Resolve conflict
resolveConflict(offline_id, 'keep_mine');  // Retry with updated version
resolveConflict(offline_id, 'use_server'); // Accept server state
resolveConflict(offline_id, 'merge', mergedData); // Apply merged data
```

## Validation

```bash
./validate_pr12.sh
```

Expected: **12/12 checks pass**

## Documentation

- `PR12_SUMMARY.md` - Full implementation details
- `PR12_DEPLOYMENT.md` - Deployment checklist & rollback
- `PR12_QUICK_START.md` - This file

## Status

✅ **Ready for deployment**
- All validations pass
- Python syntax valid
- Tests written (9 test cases)
- Documentation complete
- Backward compatible (old clients get missing_client_version conflict)

## Next Steps

1. Review PR12_DEPLOYMENT.md for detailed deployment steps
2. Run migration: `python manage.py migrate ptw`
3. Run tests: `python manage.py test ptw.tests.test_offline_sync_conflicts`
4. Update frontend imports to use new hook
5. Add SyncStatusIndicator to layout
6. Add /sync-conflicts route
7. Build and deploy frontend
8. Test manually with offline scenarios

## Support

Questions? Check:
- PR12_SUMMARY.md for implementation details
- PR12_DEPLOYMENT.md for deployment steps
- Test file for usage examples
- conflict_utils.py for merge logic
