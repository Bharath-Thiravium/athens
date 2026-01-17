# PR12 - Offline Sync Conflict Resolution + Robust Sync Status

## Implementation Summary

Successfully implemented comprehensive offline sync conflict resolution system for PTW module with versioning, idempotency tracking, conflict detection, and resolution UI.

## Backend Changes

### 1. Database Schema (Migration 0009)
- **Added version fields** to `Permit`, `PermitIsolationPoint`, `PermitCloseout` (IntegerField, default=1, indexed)
- **Created AppliedOfflineChange model** for idempotency tracking with unique constraint on (device_id, offline_id, entity)

### 2. Conflict Resolution Utilities (`conflict_utils.py`)
**Functions:**
- `check_idempotency()` - Check if change already applied
- `record_applied_change()` - Record applied change for deduplication
- `detect_permit_conflicts()` - Detect conflicts in permit updates with field-level analysis
- `merge_permit_fields()` - Merge permit fields using strategies (set_merge, true_wins)
- `validate_status_transition()` - Validate status transitions with compliance checks
- `detect_isolation_conflicts()` - Detect isolation point conflicts with monotonic status validation
- `merge_isolation_lock_ids()` - Merge lock IDs using union
- `detect_closeout_conflicts()` - Detect closeout checklist conflicts
- `merge_closeout_checklist()` - Merge checklist with True wins strategy
- `get_server_state()` - Get minimal server state for conflict resolution

**Conflict Detection Logic:**
- **Scalar fields** (title, description, location): Conflict if versions mismatch
- **JSON set fields** (ppe_requirements): Set-merge hint (union)
- **Safety checklist**: True-wins hint (any True value wins)
- **Status transitions**: Validate using `can_transition_to()` and compliance checks
- **Isolation status**: Monotonic progression (assigned → isolated → verified → deisolated)

### 3. Enhanced Sync Endpoint (`views.py`)
**Updated `sync_offline_data()` endpoint:**
- Accepts new payload format with `changes` array
- Each change includes: entity, op, offline_id, server_id, client_version, data
- Returns structured response: `{applied, conflicts, rejected, summary}`

**Response Structure:**
```json
{
  "applied": [
    {"entity": "permit", "offline_id": "...", "server_id": 123, "new_version": 2}
  ],
  "conflicts": [
    {
      "entity": "permit",
      "offline_id": "...",
      "server_id": 123,
      "reason": "stale_version",
      "client_version": 1,
      "server_version": 2,
      "fields": {
        "title": {"client": "...", "server": "...", "merge_hint": "last_write_wins"}
      },
      "server_state": {...}
    }
  ],
  "rejected": [
    {"entity": "...", "offline_id": "...", "reason": "validation_error", "detail": {...}}
  ]
}
```

**Supported Entities:**
- `permit` (create, update, update_status)
- `permit_photo` (append, idempotent)
- `gas_reading` (append)
- `isolation_point` (update with version check)
- `closeout` (update with merge)

**Version Increment:**
- Uses `F('version') + 1` for atomic increment
- Calls `refresh_from_db()` to get new version

**Idempotency:**
- Checks `AppliedOfflineChange` before processing
- Returns `already_applied` status if duplicate

## Frontend Changes

### 1. TypeScript Types (`types/offlineSync.ts`)
**Interfaces:**
- `QueueItem` - Queue item with status tracking
- `ConflictDetail` - Conflict information with field-level details
- `FieldConflict` - Per-field conflict with merge hints
- `SyncPayload` - Sync request payload
- `SyncResponse` - Sync response structure
- `SyncStatusInfo` - Sync status information

**Enums:**
- `SyncStatus`: pending | syncing | synced | conflict | failed
- `SyncOperation`: create | update | update_status | append
- `SyncEntity`: permit | permit_photo | gas_reading | isolation_point | closeout | signature

### 2. Updated Offline Sync Hook (`hooks/useOfflineSync2.ts`)
**Features:**
- **Queue Management**: localStorage-based queue with per-item status
- **Device ID**: Persistent device identifier for idempotency
- **Sync Function**: Batched sync with conflict handling
- **Conflict Resolution**: `resolveConflict(offline_id, resolution, mergedData?)`
  - `keep_mine`: Retry with client version updated to server version
  - `use_server`: Mark as synced with server state
  - `merge`: Apply merged data and retry
- **Auto-sync**: Every 5 minutes when online
- **Status Tracking**: pendingCount, conflictCount, lastSync, syncProgress
- **Queue Cleanup**: Remove synced items older than 7 days

**API:**
```typescript
{
  syncStatus: SyncStatusInfo,
  queue: QueueItem[],
  addToQueue(entity, op, payload, server_id?, client_version?): string,
  syncNow(): Promise<void>,
  resolveConflict(offline_id, resolution, mergedData?): void,
  removeFromQueue(offline_id): void,
  clearSynced(): void,
  getConflicts(): QueueItem[]
}
```

### 3. Sync Status Indicator (`components/SyncStatusIndicator.tsx`)
**Features:**
- Badge with pending/conflict count
- Status icon (online/offline/syncing/conflict)
- Dropdown menu:
  - Sync Now (disabled if offline or no pending)
  - View Conflicts (shows count, links to conflicts page)
  - Clear Synced
- Progress indicator during sync

### 4. Conflict Resolution UI (`components/SyncConflictsPage.tsx`)
**Features:**
- List of all conflicts with details
- Per-conflict information:
  - Entity type and reason tag
  - Client/server versions
  - Created timestamp and attempt count
  - Field-level conflict details with merge hints
- Resolution actions:
  - **Keep Mine**: Retry with updated version
  - **Use Server**: Accept server state
  - **Auto Merge**: Apply smart merge based on hints
  - **Discard**: Remove from queue
- Auto-merge modal with explanation

**Merge Strategies:**
- **set_merge**: Union of arrays/sets
- **true_wins**: For checklists, True from either version wins
- **last_write_wins**: Manual resolution required

## Tests

### Backend Tests (`tests/test_offline_sync_conflicts.py`)
**9 Test Cases:**
1. `test_apply_update_when_versions_match` - Successful update with matching versions
2. `test_conflict_when_stale_version_scalar_field` - Conflict detection for stale scalar fields
3. `test_set_merge_ppe_when_stale` - PPE requirements set-merge hint
4. `test_checklist_merge_true_wins` - Safety checklist true-wins hint
5. `test_append_photo_idempotent_by_offline_id` - Photo append idempotency
6. `test_status_transition_rejected_when_invalid` - Invalid status transition rejection
7. `test_isolation_status_monotonic` - Isolation status monotonic progression
8. `test_applied_change_deduplication_table` - AppliedOfflineChange deduplication
9. `test_missing_client_version_handling` - Missing client_version handling

## Key Design Decisions

1. **Version Field**: Integer field incremented on every update, indexed for performance
2. **Idempotency**: Separate `AppliedOfflineChange` table with unique constraint
3. **Conflict Reasons**: Structured reasons (stale_version, invalid_transition, validation_error, missing_client_version)
4. **Merge Hints**: Field-level hints guide frontend auto-merge (set_merge, true_wins, last_write_wins)
5. **Server State**: Minimal server state returned in conflicts for resolution
6. **Backward Compatibility**: Old clients without client_version get conflict with missing_client_version reason
7. **Append-Only Entities**: Photos and gas readings are idempotent by offline_id, no version check
8. **Status Validation**: Status transitions validated server-side with compliance checks
9. **Atomic Version Increment**: Uses F('version') + 1 to prevent race conditions
10. **Queue Persistence**: localStorage for queue, IndexedDB consideration for future

## Files Created (8)
1. `app/backend/ptw/migrations/0009_add_version_and_idempotency.py` - Migration
2. `app/backend/ptw/conflict_utils.py` - Conflict resolution utilities (~250 lines)
3. `app/frontend/src/features/ptw/types/offlineSync.ts` - TypeScript types (~80 lines)
4. `app/frontend/src/features/ptw/hooks/useOfflineSync2.ts` - Updated hook (~280 lines)
5. `app/frontend/src/features/ptw/components/SyncStatusIndicator.tsx` - Status indicator (~90 lines)
6. `app/frontend/src/features/ptw/components/SyncConflictsPage.tsx` - Conflict resolution UI (~220 lines)
7. `app/backend/ptw/tests/test_offline_sync_conflicts.py` - Tests (~280 lines)
8. `validate_pr12.sh` - Validation script

## Files Modified (2)
1. `app/backend/ptw/models.py` - Added version fields and AppliedOfflineChange model (+30 lines)
2. `app/backend/ptw/views.py` - Replaced sync_offline_data endpoint (+250 lines)

## Validation

Run validation:
```bash
chmod +x validate_pr12.sh
./validate_pr12.sh
```

Run tests:
```bash
cd app/backend
python manage.py test ptw.tests.test_offline_sync_conflicts
```

Run migration:
```bash
python manage.py migrate
```

## Usage

### Backend API
```python
POST /api/v1/ptw/sync-offline-data/
{
  "device_id": "device_abc123",
  "client_time": "2024-01-15T10:30:00Z",
  "changes": [
    {
      "entity": "permit",
      "op": "update",
      "offline_id": "offline_xyz",
      "server_id": 123,
      "client_version": 5,
      "data": {"title": "Updated Title"}
    }
  ]
}
```

### Frontend Hook
```typescript
const { syncStatus, addToQueue, syncNow, resolveConflict, getConflicts } = useOfflineSync();

// Add to queue
addToQueue('permit', 'update', { title: 'New Title' }, permitId, currentVersion);

// Manual sync
syncNow();

// Resolve conflict
resolveConflict(offline_id, 'keep_mine');
resolveConflict(offline_id, 'use_server');
resolveConflict(offline_id, 'merge', mergedData);
```

### UI Components
```typescript
// Add to layout
<SyncStatusIndicator />

// Conflicts page route
<Route path="/dashboard/ptw/sync-conflicts" element={<SyncConflictsPage />} />
```

## Security

- **Permission Filtering**: All sync operations filtered by user's project
- **Validation**: Server-side validation for all updates
- **Status Transitions**: Enforced using existing `can_transition_to()` logic
- **Compliance Gating**: Closeout completion, gas testing, isolation requirements enforced
- **Device ID**: Client-generated, used only for idempotency tracking

## Performance

- **Indexed Fields**: version field indexed on all versioned models
- **Batch Processing**: Sync endpoint processes multiple changes in single request
- **Atomic Operations**: F('version') + 1 prevents race conditions
- **Query Optimization**: select_related/prefetch_related in sync endpoint
- **Queue Cleanup**: Auto-remove synced items older than 7 days

## Future Enhancements

1. IndexedDB for queue storage (handle larger payloads)
2. Partial field updates (only send changed fields)
3. Conflict resolution history/audit
4. Server-side merge execution
5. Real-time conflict notifications via WebSocket
6. Bulk conflict resolution
7. Custom merge strategies per field type
8. Conflict analytics dashboard

## Status

✅ Backend implementation complete
✅ Frontend implementation complete
✅ Tests complete
✅ Documentation complete
✅ Validation script complete
⏳ Ready for migration and testing
