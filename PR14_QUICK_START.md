# PR14 Quick Start Guide

## What Changed?
PTW permits now use **server-side pagination** and **consistent filters** across list/KPI/export endpoints.

## Key Features

### 1. Server-Side Pagination
- **Before**: Frontend loaded all permits, paginated client-side
- **After**: Backend returns 20 permits per page, frontend requests more as needed
- **Benefit**: Faster load times, scales to thousands of permits

### 2. Deep-Linkable Filters
- **URL Example**: `/dashboard/ptw?status=active&page=2&search=PTW-001`
- **Benefit**: Share filtered views via URL, bookmark searches

### 3. Unified Filter Model
- **List, KPI, Export** all use same filters
- **Benefit**: "Export current view" exports exactly what you see

## Quick Examples

### Backend API

#### List Permits (Paginated)
```bash
GET /api/v1/ptw/permits/?page=1&page_size=20&status=active
```

Response:
```json
{
  "count": 150,
  "next": "http://.../permits/?page=2",
  "previous": null,
  "results": [...]
}
```

#### Filter by Multiple Statuses
```bash
GET /api/v1/ptw/permits/?status=active,pending_approval
```

#### Filter by Date Range
```bash
GET /api/v1/ptw/permits/?date_from=2024-01-01&date_to=2024-12-31
```

#### Search + Filter + Sort
```bash
GET /api/v1/ptw/permits/?search=PTW-001&status=active&ordering=-created_at
```

#### KPIs with Filters
```bash
GET /api/v1/ptw/permits/kpis/?status=active&project=1
```

#### Export with Filters
```bash
GET /api/v1/ptw/permits/export_excel/?status=active&risk_level=high
```

#### Bulk Export with Filters (No IDs Needed)
```bash
POST /api/v1/ptw/permits/bulk_export_pdf/?status=active
Body: { "use_filters": true }
```

### Frontend Usage

#### Import Updated API
```typescript
import { getPermitsPaginated, PaginatedResponse } from '../api';

const response = await getPermitsPaginated({
  page: 1,
  page_size: 20,
  status: 'active',
  search: 'PTW-001'
});

console.log(response.data.count); // Total count
console.log(response.data.results); // Current page results
```

#### Export Current View
```typescript
// User sees filtered list, clicks "Export Current View"
const params = {
  search: searchText,
  status: statusFilter,
  date_from: dateRange?.[0]?.format('YYYY-MM-DD'),
  date_to: dateRange?.[1]?.format('YYYY-MM-DD')
};

const response = await exportPermitsExcel(params);
// Downloads Excel with filtered permits
```

## Available Filters

| Filter | Type | Example | Description |
|--------|------|---------|-------------|
| `page` | number | `page=2` | Page number (default: 1) |
| `page_size` | number | `page_size=50` | Results per page (10/20/50/100) |
| `search` | string | `search=PTW-001` | Search permit_number, title, location |
| `status` | string | `status=active,pending_approval` | Single or comma-separated |
| `project` | number | `project=1` | Filter by project ID |
| `permit_type` | number | `permit_type=5` | Filter by permit type ID |
| `permit_category` | string | `permit_category=hot_work` | Filter by category |
| `risk_level` | string | `risk_level=high` | Filter by risk level |
| `priority` | string | `priority=urgent` | Filter by priority |
| `created_by` | number | `created_by=10` | Filter by creator user ID |
| `date_from` | date | `date_from=2024-01-01` | Start date (YYYY-MM-DD) |
| `date_to` | date | `date_to=2024-12-31` | End date (YYYY-MM-DD) |
| `ordering` | string | `ordering=-created_at` | Sort field (prefix `-` for desc) |

## Testing

### Run Backend Tests
```bash
cd /var/www/athens/app/backend
python manage.py test ptw.tests.test_filters_and_pagination
```

Expected: 15 tests passed

### Run Validation
```bash
cd /var/www/athens
./validate_pr14.sh
```

Expected: 24/24 checks passed

### Manual Testing

1. **Pagination**:
   - Open `/dashboard/ptw`
   - Verify "X-Y of Z permits" shows correct total
   - Click page 2, verify URL updates to `?page=2`
   - Refresh page, verify stays on page 2

2. **Filters**:
   - Select status "Active"
   - Verify URL updates to `?status=active`
   - Copy URL, open in new tab, verify filter applied

3. **Search**:
   - Type "PTW-001" in search
   - Verify URL updates to `?search=PTW-001`
   - Verify results match search

4. **Export Current View**:
   - Apply filters (status=active, date range)
   - Click "Export Current View"
   - Verify Excel contains only filtered permits

5. **Project Scoping**:
   - Login as user from Project A
   - Verify only Project A permits visible
   - Try accessing Project B permit by ID (should fail)

## Troubleshooting

### Issue: "No permits found"
- **Check**: User assigned to a project?
- **Fix**: Assign user to project in admin panel

### Issue: Pagination not working
- **Check**: Backend returns `count`, `next`, `previous`, `results`?
- **Fix**: Verify DRF pagination settings in `settings.py`

### Issue: Filters not applied
- **Check**: URL has query params?
- **Fix**: Verify `updateURL()` called in `fetchPermits()`

### Issue: Export includes wrong permits
- **Check**: Export API called with filter params?
- **Fix**: Verify `exportPermitsExcel(params)` receives current filters

### Issue: Cross-project data leak
- **Check**: `get_queryset()` filters by user project?
- **Fix**: Verify project scoping in `PermitViewSet.get_queryset()`

## Configuration

### Change Default Page Size
Edit `app/backend/backend/settings.py`:
```python
REST_FRAMEWORK = {
    'PAGE_SIZE': 50,  # Change from 20 to 50
}
```

### Disable Pagination (Not Recommended)
In `PermitViewSet`:
```python
pagination_class = None  # Disables pagination
```

### Add Custom Filter
Edit `app/backend/ptw/filters.py`:
```python
class PermitFilter(filters.FilterSet):
    # Add new filter
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
```

## Performance Tips

1. **Use Pagination**: Don't set `page_size` too high (max 100)
2. **Limit Date Ranges**: Narrow date filters for faster queries
3. **Use Specific Filters**: More filters = fewer results = faster
4. **Monitor Queries**: Check Django debug toolbar for N+1 queries

## Migration from Old Code

### Old Code (Client-Side Pagination)
```typescript
const response = await getPermits(params);
const allPermits = response.data; // All permits loaded
const page1 = allPermits.slice(0, 20); // Client-side slice
```

### New Code (Server-Side Pagination)
```typescript
const response = await getPermitsPaginated({ page: 1, page_size: 20, ...params });
const page1 = response.data.results; // Only page 1 from server
const total = response.data.count; // Total count
```

## Rollback Plan

If issues arise:

1. **Backend**: Revert `views.py` changes, set `pagination_class = None`
2. **Frontend**: Revert `PermitList.tsx` to use old `getPermits()`
3. **Database**: No migrations, no rollback needed

## Next Steps

- [ ] Test in staging environment
- [ ] Monitor query performance
- [ ] Add saved filter presets (future PR)
- [ ] Add FilterBar to KPI dashboard (future PR)
- [ ] Consider adding indexes if queries slow

## Support

Questions? Check:
1. `PR14_SUMMARY.md` for detailed documentation
2. `validate_pr14.sh` for validation checks
3. Test cases in `test_filters_and_pagination.py` for examples
