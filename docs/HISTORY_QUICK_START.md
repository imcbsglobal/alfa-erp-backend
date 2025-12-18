# History Feature - Quick Start Guide

## What's New?

Three new API endpoints to track picking, packing, and delivery history:

1. **Picking History**: `GET /api/sales/picking/history/`
2. **Packing History**: `GET /api/sales/packing/history/`
3. **Delivery History**: `GET /api/sales/delivery/history/`

---

## Quick Examples

### 1. Get All History (Admin View)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/sales/picking/history/
```

### 2. Search by Invoice
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/sales/picking/history/?search=INV-007"
```

### 3. Filter by Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/sales/packing/history/?status=PACKED"
```

### 4. Date Range Filter
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/sales/delivery/history/?start_date=2024-12-01&end_date=2024-12-31"
```

### 5. Combined Filters
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/sales/delivery/history/?delivery_type=COURIER&status=DELIVERED&start_date=2024-12-10"
```

---

## Response Format

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/sales/picking/history/?page=2",
  "previous": null,
  "results": [
    {
      "id": 15,
      "invoice_no": "INV-007",
      "customer_name": "John Doe",
      "customer_email": "customer1@gmail.com",
      "picker_email": "picker1@gmail.com",
      "picker_name": "Alice Picker",
      "picking_status": "PICKED",
      "start_time": "2024-12-10T14:15:00Z",
      "end_time": "2024-12-10T14:30:00Z",
      "duration": 15.0,
      "notes": "All items picked successfully",
      "created_at": "2024-12-10T14:15:00Z"
    }
  ]
}
```

---

## Key Features

✅ **Permission-Based Access**
- Admins see all sessions
- Users see only their own

✅ **Search Across Multiple Fields**
- Invoice number, customer name/email, employee email

✅ **Flexible Filtering**
- Status (PREPARING, PICKED, PACKED, etc.)
- Date range (start_date, end_date)
- Delivery type (DIRECT, COURIER, INTERNAL)

✅ **Pagination**
- Default: 10 per page
- Max: 100 per page
- Navigate with `?page=2`

✅ **Duration Calculation**
- Automatic calculation in minutes
- Null for ongoing sessions

---

## Frontend Integration

```javascript
// React/Next.js Example
const fetchHistory = async () => {
  const response = await fetch(
    `${BASE_URL}/api/sales/picking/history/?status=PICKED&page=1`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  const data = await response.json();
  console.log(`Found ${data.count} total sessions`);
  console.log(`Showing ${data.results.length} on this page`);
  
  data.results.forEach(session => {
    console.log(`${session.invoice_no} - ${session.picker_name} - ${session.duration} min`);
  });
};
```

---

## Available Query Parameters

| Parameter | Type | Example | Description |
|---|---|---|---|
| `search` | string | `?search=INV-007` | Search invoice/customer/employee |
| `status` | string | `?status=PICKED` | Filter by session status |
| `start_date` | string | `?start_date=2024-12-01` | Sessions on or after |
| `end_date` | string | `?end_date=2024-12-31` | Sessions on or before |
| `delivery_type` | string | `?delivery_type=COURIER` | Delivery only - filter by type |
| `page` | integer | `?page=2` | Page number |
| `page_size` | integer | `?page_size=20` | Results per page (max 100) |

---

## Status Values

### Picking
- `PREPARING` - In progress
- `PICKED` - Completed
- `VERIFIED` - Pharmacist verified

### Packing
- `PENDING` - Waiting
- `IN_PROGRESS` - In progress
- `PACKED` - Completed

### Delivery
- `PENDING` - Not started
- `IN_TRANSIT` - In progress
- `DELIVERED` - Completed

### Delivery Types
- `DIRECT` - Self pickup (customer collects)
- `COURIER` - External courier service
- `INTERNAL` - Company driver delivery

---

## Common Use Cases

### 1. Admin Dashboard - Monitor Team
```bash
# See all ongoing picking tasks
GET /api/sales/picking/history/?status=PREPARING

# See all completed deliveries today
GET /api/sales/delivery/history/?status=DELIVERED&start_date=2024-12-18
```

### 2. Employee Performance Review
```bash
# Get specific employee's work
GET /api/sales/picking/history/?search=picker1@gmail.com&start_date=2024-12-01

# Check courier deliveries
GET /api/sales/delivery/history/?delivery_type=COURIER&status=DELIVERED
```

### 3. Invoice Tracking
```bash
# Track invoice through all stages
GET /api/sales/picking/history/?search=INV-007
GET /api/sales/packing/history/?search=INV-007
GET /api/sales/delivery/history/?search=INV-007
```

### 4. User View - Personal History
```bash
# User automatically sees only their own sessions
GET /api/sales/picking/history/
# Returns only sessions where picker = authenticated user
```

---

## Files Modified

1. **apps/sales/serializers.py**
   - Added `PickingHistorySerializer`
   - Added `PackingHistorySerializer`
   - Added `DeliveryHistorySerializer`

2. **apps/sales/views.py**
   - Added `HistoryPagination` (10 per page)
   - Added `PickingHistoryView`
   - Added `PackingHistoryView`
   - Added `DeliveryHistoryView`

3. **apps/sales/urls.py**
   - Added `/picking/history/` route
   - Added `/packing/history/` route
   - Added `/delivery/history/` route

4. **docs/api/sales.md**
   - Added Section 7: Picking History API
   - Added Section 8: Packing History API
   - Added Section 9: Delivery History API
   - Updated API Endpoints Summary table

5. **docs/HISTORY_FEATURE_IMPLEMENTATION.md**
   - Complete implementation guide
   - Frontend integration examples
   - Testing documentation

---

## Testing

```bash
# Get Django shell
python manage.py shell

# Create test data
from apps.accounts.models import User
from apps.sales.models import *
from django.utils import timezone

# Test API endpoints
python manage.py runserver

# In another terminal, test with curl:
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/sales/picking/history/
```

---

## Next Steps

1. ✅ Backend implementation complete
2. ✅ API documentation complete
3. ⏳ Frontend implementation needed:
   - Create History page with tabs (Picking/Packing/Delivery)
   - Add search bar and filters
   - Implement pagination controls
   - Add date picker for date range
4. ⏳ Add export functionality (CSV/Excel)
5. ⏳ Add analytics dashboard (stats, charts)

---

## Support

For questions or issues:
- Check [docs/api/sales.md](./api/sales.md) for complete API reference
- Check [docs/HISTORY_FEATURE_IMPLEMENTATION.md](./HISTORY_FEATURE_IMPLEMENTATION.md) for detailed guide
- Review unit tests in `apps/sales/tests/`

---

**Implementation Date**: December 18, 2025  
**Status**: ✅ Backend Complete, ⏳ Frontend Pending
