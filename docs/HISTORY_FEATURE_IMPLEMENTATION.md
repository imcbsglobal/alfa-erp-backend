# History Feature Implementation Guide

Complete implementation of picking, packing, and delivery history tracking with search, filtering, and pagination.

## Overview

The history feature provides three dedicated endpoints to track and review all picking, packing, and delivery activities:

- **Picking History** (`GET /api/sales/picking/history/`)
- **Packing History** (`GET /api/sales/packing/history/`)
- **Delivery History** (`GET /api/sales/delivery/history/`)

Each endpoint supports:
- ✅ Search by invoice number, customer details, or employee email
- ✅ Status-based filtering (PREPARING, PICKED, PACKED, etc.)
- ✅ Date range filtering (start_date, end_date)
- ✅ Pagination (default: 10 per page, max: 100)
- ✅ Permission-based access (admins see all, users see only their own)
- ✅ Duration calculation in minutes

---

## Architecture

### Models
History data is pulled from existing session models:
- `PickingSession` - tracks picking activities
- `PackingSession` - tracks packing activities
- `DeliverySession` - tracks delivery activities

No new models needed - history views query existing session records.

### Serializers
Three specialized history serializers:

**PickingHistorySerializer**
```python
Fields:
- id (int) - Session ID
- invoice_no (string) - Invoice number
- invoice_date (date) - Invoice date
- invoice_status (string) - Invoice status (PENDING, PICKING, PACKED, DELIVERED, etc.)
- invoice_remarks (string) - Invoice remarks/notes
- salesman_name (string) - Salesman who created the invoice
- customer_name (string) - Customer full name
- customer_email (string) - Customer email
- customer_phone (string) - Customer primary phone
- customer_address (string) - Customer address line 1
- items (list) - Invoice line items (id, name, item_code, quantity, mrp, company_name, packing, shelf_location, remarks, batch_no, expiry_date)
- total_amount (number) - Calculated total (sum of quantity * mrp)
- picker_email (string) - Employee who picked
- picker_name (string) - Employee full name
- picking_status (string) - PREPARING, PICKED, VERIFIED
- start_time (datetime) - When picking started
- end_time (datetime) - When picking completed
- duration (float) - Minutes between start and end
- notes (string) - Session notes
- created_at (datetime) - Session creation time
```

**PackingHistorySerializer**
```python
Fields:
- id, invoice_no, invoice_date, invoice_status, invoice_remarks
- salesman_name
- customer_name, customer_email, customer_phone, customer_address
- items (list) - Invoice items
- total_amount
- packer_email, packer_name
- packing_status (PENDING, IN_PROGRESS, PACKED)
- start_time, end_time, duration, notes, created_at
```

**DeliveryHistorySerializer**
```python
Fields:
- id, invoice_no, invoice_date, invoice_status, invoice_remarks
- salesman_name
- customer_name, customer_email, customer_phone, customer_address
- items (list) - Invoice items
- total_amount
- delivery_type (DIRECT, COURIER, INTERNAL)
- delivery_user_email, delivery_user_name
- courier_name, tracking_no
- delivery_status (PENDING, IN_TRANSIT, DELIVERED)
- start_time, end_time, duration, notes, created_at
```

### Views
Generic list views with custom querysets:

```python
class PickingHistoryView(generics.ListAPIView):
    serializer_class = PickingHistorySerializer
    pagination_class = HistoryPagination  # 10 per page
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Permission filtering
        # Search filtering
        # Status filtering
        # Date filtering
```

### Permissions
Implemented via `get_queryset()` filtering:

**Admin users** (`is_admin_or_superadmin()` = True):
- See ALL sessions across all employees
- No filtering applied

**Regular users** (pickers, packers, drivers):
- See ONLY their own sessions
- Filtered by: `picker=user`, `packer=user`, or `assigned_to=user`

---

## Query Parameters

### Common Parameters (All History Endpoints)

| Parameter | Type | Description | Example |
|---|---|---|---|
| `invoice` | integer | Filter by invoice primary key (id) | `?invoice=123` |
| `invoice_no` | string | Filter by invoice number (exact match) | `?invoice_no=INV-007` |
| `search` | string | Search across invoice, customer, employee | `?search=INV-007` |
| `status` | string | Filter by session status | `?status=PICKED` |
| `start_date` | string | Sessions on or after (YYYY-MM-DD) | `?start_date=2024-12-01` |
| `end_date` | string | Sessions on or before (YYYY-MM-DD) | `?end_date=2024-12-31` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Results per page (max 100) | `?page_size=20` |

### Delivery-Specific Parameters

| Parameter | Type | Description | Example |
|---|---|---|---|
| `delivery_type` | string | DIRECT, COURIER, INTERNAL | `?delivery_type=COURIER` |

---

## Search Fields

### Picking History Search
- Invoice number (`invoice__invoice_no`)
- Customer name (`invoice__customer__name`)
- Customer email (`invoice__customer__email`)
- Picker email (`picker__email`)

### Packing History Search
- Invoice number (`invoice__invoice_no`)
- Customer name (`invoice__customer__name`)
- Customer email (`invoice__customer__email`)
- Packer email (`packer__email`)

### Delivery History Search
- Invoice number (`invoice__invoice_no`)
- Customer name (`invoice__customer__name`)
- Customer email (`invoice__customer__email`)
- Delivery user email (`assigned_to__email`)
- Courier name (`courier_name`)
- Tracking number (`tracking_no`)

---

## Status Values

### Picking Status
- `PREPARING` - Picking in progress (ongoing)
- `PICKED` - Picking completed
- `VERIFIED` - Pharmacist verification completed

### Packing Status
- `PENDING` - Waiting to pack
- `IN_PROGRESS` - Packing in progress (ongoing)
- `PACKED` - Packing completed

### Delivery Status
- `PENDING` - Not yet started
- `IN_TRANSIT` - Delivery in progress (ongoing)
- `DELIVERED` - Delivery completed

---

## Use Cases

### 1. Admin Dashboard - Monitor All Activity
**Requirement**: Admin wants to see all picking activities across the team

```bash
GET /api/sales/picking/history/?page_size=50
```

**Response**: All picking sessions from all employees, ordered by newest first

### 2. Employee Performance Review
**Requirement**: Admin wants to check specific employee's completed tasks

```bash
GET /api/sales/picking/history/?search=picker1@gmail.com&status=PICKED&start_date=2024-12-01&end_date=2024-12-31
```

**Response**: All completed picking tasks by picker1@gmail.com in December 2024

### 3. Worker Personal History
**Requirement**: Picker wants to see their own work history

```bash
# User authenticated as picker1@gmail.com
GET /api/sales/picking/history/
```

**Response**: Only sessions where `picker = picker1@gmail.com` (automatic filtering)

### 4. Ongoing Tasks Dashboard
**Requirement**: Admin wants to monitor currently active picking tasks

```bash
GET /api/sales/picking/history/?status=PREPARING
```

**Response**: All picking sessions with status=PREPARING (ongoing tasks where end_time is null)

### 5. Delivery Type Analysis
**Requirement**: Admin wants courier delivery statistics

```bash
GET /api/sales/delivery/history/?delivery_type=COURIER&status=DELIVERED&start_date=2024-12-01
```

**Response**: All completed courier deliveries from December 1st onwards

### 6. Invoice Tracking
**Requirement**: Admin searches for specific invoice workflow

```bash
GET /api/sales/picking/history/?search=INV-007
GET /api/sales/packing/history/?search=INV-007
GET /api/sales/delivery/history/?search=INV-007
```

**Response**: Complete workflow history for INV-007 across all stages

---

## Frontend Integration

### React Component - History Table with Filters

```jsx
import React, { useState, useEffect } from 'react';

const PickingHistoryPage = () => {
  const [history, setHistory] = useState({ results: [], count: 0 });
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    startDate: '',
    endDate: '',
    page: 1,
    pageSize: 10
  });

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.search) params.append('search', filters.search);
      if (filters.status) params.append('status', filters.status);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      params.append('page', filters.page);
      params.append('page_size', filters.pageSize);

      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/sales/picking/history/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch history');
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [filters]);

  const handleSearch = (e) => {
    e.preventDefault();
    setFilters({ ...filters, page: 1 });
  };

  return (
    <div className="history-container">
      <h1>Picking History</h1>

      {/* Filters */}
      <form onSubmit={handleSearch} className="filters">
        <input
          type="text"
          placeholder="Search invoice or details..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
        />

        <select
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
        >
          <option value="">All Status</option>
          <option value="PREPARING">Preparing</option>
          <option value="PICKED">Picked</option>
          <option value="VERIFIED">Verified</option>
        </select>

        <input
          type="date"
          value={filters.startDate}
          onChange={(e) => setFilters({ ...filters, startDate: e.target.value, page: 1 })}
          placeholder="Start Date"
        />

        <input
          type="date"
          value={filters.endDate}
          onChange={(e) => setFilters({ ...filters, endDate: e.target.value, page: 1 })}
          placeholder="End Date"
        />

        <button type="submit">Search</button>
      </form>

      {/* Table */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <table className="history-table">
            <thead>
              <tr>
                <th>Invoice</th>
                <th>Customer</th>
                <th>Picker</th>
                <th>Status</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Duration</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {history.results.map((session) => (
                <tr key={session.id}>
                  <td>{session.invoice_no}</td>
                  <td>
                    <div>{session.customer_name}</div>
                    <div className="text-muted">{session.customer_email}</div>
                  </td>
                  <td>
                    <div>{session.picker_name}</div>
                    <div className="text-muted">{session.picker_email}</div>
                  </td>
                  <td>
                    <span className={`badge badge-${session.picking_status.toLowerCase()}`}>
                      {session.picking_status}
                    </span>
                  </td>
                  <td>{new Date(session.start_time).toLocaleString()}</td>
                  <td>
                    {session.end_time 
                      ? new Date(session.end_time).toLocaleString() 
                      : 'Ongoing'}
                  </td>
                  <td>
                    {session.duration 
                      ? `${session.duration} min` 
                      : '-'}
                  </td>
                  <td>{session.notes || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="pagination">
            <button
              disabled={!history.previous}
              onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
            >
              Previous
            </button>
            <span>Page {filters.page}</span>
            <button
              disabled={!history.next}
              onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
            >
              Next
            </button>
            <div>
              Showing {history.results.length} of {history.count} total records
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default PickingHistoryPage;
```

### Vue Component - Delivery History with Tabs

```vue
<template>
  <div class="delivery-history">
    <h1>Delivery History</h1>

    <!-- Tabs for delivery type -->
    <div class="tabs">
      <button 
        :class="{ active: deliveryType === '' }"
        @click="setDeliveryType('')"
      >
        All Modes
      </button>
      <button 
        :class="{ active: deliveryType === 'DIRECT' }"
        @click="setDeliveryType('DIRECT')"
      >
        Self Pickup
      </button>
      <button 
        :class="{ active: deliveryType === 'COURIER' }"
        @click="setDeliveryType('COURIER')"
      >
        Courier
      </button>
      <button 
        :class="{ active: deliveryType === 'INTERNAL' }"
        @click="setDeliveryType('INTERNAL')"
      >
        Company Delivery
      </button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <input 
        v-model="search" 
        placeholder="Search invoice or details..."
        @input="debouncedSearch"
      />
      <input 
        type="date" 
        v-model="startDate"
        @change="fetchHistory"
      />
      <input 
        type="date" 
        v-model="endDate"
        @change="fetchHistory"
      />
    </div>

    <!-- Table -->
    <table v-if="history.results.length">
      <thead>
        <tr>
          <th>Invoice</th>
          <th>Mode</th>
          <th>Details</th>
          <th>Date</th>
          <th>Completed At</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="session in history.results" :key="session.id">
          <td>{{ session.invoice_no }}</td>
          <td>
            <span v-if="session.delivery_type === 'DIRECT'">Self Pickup</span>
            <span v-else-if="session.delivery_type === 'COURIER'">Courier</span>
            <span v-else>Company Delivery</span>
          </td>
          <td>
            <div v-if="session.delivery_type === 'DIRECT'">
              <div>{{ session.customer_email }}</div>
              <div class="text-muted">Customer collected the order</div>
            </div>
            <div v-else-if="session.delivery_type === 'COURIER'">
              <div>{{ session.courier_name }}</div>
              <div class="text-muted">Tracking: {{ session.tracking_no }}</div>
            </div>
            <div v-else>
              <div>{{ session.delivery_user_email }}</div>
              <div class="text-muted">Delivered by company driver</div>
            </div>
          </td>
          <td>{{ formatDate(session.created_at) }}</td>
          <td>{{ formatTime(session.end_time) }}</td>
        </tr>
      </tbody>
    </table>

    <div v-else class="empty-state">
      No delivery history found
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <button :disabled="!history.previous" @click="prevPage">Previous</button>
      <span>Page {{ page }}</span>
      <button :disabled="!history.next" @click="nextPage">Next</button>
      <div>Showing {{ history.results.length }} of {{ history.count }} records</div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { debounce } from 'lodash';

export default {
  name: 'DeliveryHistory',
  setup() {
    const history = ref({ results: [], count: 0 });
    const deliveryType = ref('');
    const search = ref('');
    const startDate = ref('');
    const endDate = ref('');
    const page = ref(1);

    const fetchHistory = async () => {
      const params = new URLSearchParams();
      if (deliveryType.value) params.append('delivery_type', deliveryType.value);
      if (search.value) params.append('search', search.value);
      if (startDate.value) params.append('start_date', startDate.value);
      if (endDate.value) params.append('end_date', endDate.value);
      params.append('page', page.value);

      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/api/sales/delivery/history/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (response.ok) {
        history.value = await response.json();
      }
    };

    const setDeliveryType = (type) => {
      deliveryType.value = type;
      page.value = 1;
      fetchHistory();
    };

    const debouncedSearch = debounce(() => {
      page.value = 1;
      fetchHistory();
    }, 500);

    const prevPage = () => {
      if (history.value.previous) {
        page.value--;
        fetchHistory();
      }
    };

    const nextPage = () => {
      if (history.value.next) {
        page.value++;
        fetchHistory();
      }
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-GB');
    };

    const formatTime = (dateString) => {
      if (!dateString) return '-';
      return new Date(dateString).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit'
      });
    };

    onMounted(() => {
      fetchHistory();
    });

    return {
      history,
      deliveryType,
      search,
      startDate,
      endDate,
      page,
      setDeliveryType,
      debouncedSearch,
      prevPage,
      nextPage,
      fetchHistory,
      formatDate,
      formatTime
    };
  }
};
</script>
```

---

## Performance Optimization

### Database Queries
History views use `select_related()` to optimize queries:

```python
queryset = PickingSession.objects.select_related(
    'invoice',           # Join Invoice table
    'invoice__customer', # Join Customer table
    'picker'             # Join User table
).order_by('-created_at')
```

**Without optimization**: N+1 query problem (1 session query + N queries for related objects)
**With optimization**: 1 query with JOINs

### Indexing Recommendations
Add database indexes for commonly filtered fields:

```python
# In models.py
class PickingSession(models.Model):
    # ... existing fields
    
    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),        # Order by created_at DESC
            models.Index(fields=['picking_status']),     # Status filter
            models.Index(fields=['picker', 'created_at']), # User filter + sort
        ]
```

### Caching Strategy
For frequently accessed data:

```python
from django.core.cache import cache

def get_user_history_summary(user_id):
    cache_key = f'history_summary_{user_id}'
    summary = cache.get(cache_key)
    
    if not summary:
        # Calculate summary
        summary = {
            'total_picks': PickingSession.objects.filter(picker_id=user_id).count(),
            'completed_picks': PickingSession.objects.filter(
                picker_id=user_id, 
                picking_status='PICKED'
            ).count(),
            # ... more stats
        }
        cache.set(cache_key, summary, timeout=300)  # 5 minutes
    
    return summary
```

---

## Testing

### Unit Tests

```python
# apps/sales/tests/test_history.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.sales.models import Invoice, Customer, Salesman, PickingSession
from datetime import datetime, timedelta

User = get_user_model()

class PickingHistoryTestCase(TestCase):
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='test123',
            name='Admin User',
            is_staff=True
        )
        
        # Create regular picker
        self.picker = User.objects.create_user(
            email='picker@test.com',
            password='test123',
            name='Picker User',
            role='PICKER'
        )
        
        # Create test data
        self.customer = Customer.objects.create(
            code='C001',
            name='Test Customer',
            email='customer@test.com'
        )
        self.salesman = Salesman.objects.create(name='Test Salesman')
        
        self.invoice = Invoice.objects.create(
            invoice_no='INV-001',
            invoice_date=datetime.now().date(),
            customer=self.customer,
            salesman=self.salesman,
            status='PICKING'
        )
        
        self.picking_session = PickingSession.objects.create(
            invoice=self.invoice,
            picker=self.picker,
            start_time=datetime.now() - timedelta(minutes=15),
            end_time=datetime.now(),
            picking_status='PICKED'
        )
        
        self.client = APIClient()
    
    def test_admin_sees_all_sessions(self):
        """Admin can see all picking sessions"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/sales/picking/history/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['invoice_no'], 'INV-001')
    
    def test_user_sees_only_own_sessions(self):
        """Regular user only sees their own sessions"""
        self.client.force_authenticate(user=self.picker)
        response = self.client.get('/api/sales/picking/history/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['picker_email'], 'picker@test.com')
    
    def test_search_filter(self):
        """Search filter works correctly"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/sales/picking/history/?search=INV-001')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
    
    def test_status_filter(self):
        """Status filter works correctly"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/sales/picking/history/?status=PICKED')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['picking_status'], 'PICKED')
    
    def test_duration_calculation(self):
        """Duration is calculated correctly"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/sales/picking/history/')
        
        self.assertEqual(response.status_code, 200)
        # Duration should be approximately 15 minutes
        self.assertGreater(response.data['results'][0]['duration'], 14)
        self.assertLess(response.data['results'][0]['duration'], 16)
    
    def test_pagination(self):
        """Pagination works correctly"""
        # Create 15 more sessions (total 16)
        for i in range(15):
            invoice = Invoice.objects.create(
                invoice_no=f'INV-{i+2:03d}',
                invoice_date=datetime.now().date(),
                customer=self.customer,
                salesman=self.salesman,
                status='PICKING'
            )
            PickingSession.objects.create(
                invoice=invoice,
                picker=self.picker,
                start_time=datetime.now(),
                picking_status='PREPARING'
            )
        
        self.client.force_authenticate(user=self.admin)
        
        # First page
        response = self.client.get('/api/sales/picking/history/?page_size=10')
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
        
        # Second page
        response = self.client.get('/api/sales/picking/history/?page=2&page_size=10')
        self.assertEqual(len(response.data['results']), 6)
        self.assertIsNone(response.data['next'])
```

### Manual Testing Checklist

- [ ] Admin can view all sessions across all users
- [ ] Regular user only sees their own sessions
- [ ] Search finds invoices by invoice number
- [ ] Search finds sessions by customer name/email
- [ ] Search finds sessions by employee email
- [ ] Status filter correctly filters by session status
- [ ] Date filters work with start_date
- [ ] Date filters work with end_date
- [ ] Date range filter works with both start_date and end_date
- [ ] Pagination shows correct page size
- [ ] Pagination next/previous links work
- [ ] Duration is calculated correctly for completed sessions
- [ ] Duration is null for ongoing sessions
- [ ] Response includes all required fields
- [ ] Timestamps are in correct format
- [ ] Empty results return proper structure
- [ ] Invalid date format is handled gracefully
- [ ] Invalid status value is ignored

---

## Troubleshooting

### Issue: User sees no history
**Cause**: User is not assigned to any sessions
**Solution**: Ensure user is the picker/packer/assigned_to in sessions

### Issue: Search returns no results
**Cause**: Search is case-sensitive or exact match
**Solution**: Search uses icontains (case-insensitive, partial match). Check spelling.

### Issue: Duration is always null
**Cause**: Sessions don't have end_time set
**Solution**: Ensure sessions are properly completed with end_time

### Issue: Admin sees same results as regular user
**Cause**: `is_admin_or_superadmin()` not returning True
**Solution**: Check User model permissions: is_staff, is_superuser, or role in [ADMIN, SUPERADMIN]

### Issue: Pagination not working
**Cause**: Page size exceeds maximum (100)
**Solution**: Use page_size <= 100

### Issue: Date filter not working
**Cause**: Incorrect date format
**Solution**: Use YYYY-MM-DD format (e.g., 2024-12-10)

---

## Future Enhancements

### 1. Export to CSV/Excel
Add export functionality for reporting:

```python
from django.http import HttpResponse
import csv

class PickingHistoryExportView(APIView):
    def get(self, request):
        sessions = PickingSession.objects.select_related('invoice', 'picker').all()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="picking_history.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Invoice', 'Customer', 'Picker', 'Status', 'Start', 'End', 'Duration'])
        
        for session in sessions:
            writer.writerow([
                session.invoice.invoice_no,
                session.invoice.customer.name,
                session.picker.email,
                session.picking_status,
                session.start_time,
                session.end_time,
                session.duration
            ])
        
        return response
```

### 2. Analytics Dashboard
Add aggregated statistics:

```python
class PickingAnalyticsView(APIView):
    def get(self, request):
        stats = {
            'total_sessions': PickingSession.objects.count(),
            'completed': PickingSession.objects.filter(picking_status='PICKED').count(),
            'avg_duration': PickingSession.objects.aggregate(
                avg=Avg('duration')
            )['avg'],
            'top_pickers': PickingSession.objects.values('picker__email').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        }
        return Response(stats)
```

### 3. Real-time Updates
Add SSE for live history updates:

```python
# When session is completed
from .events import send_history_event

def complete_picking(session):
    session.end_time = timezone.now()
    session.picking_status = 'PICKED'
    session.save()
    
    # Broadcast to history listeners
    send_history_event('picking', session)
```

### 4. Advanced Filtering
Add more filter options:
- Duration range (min/max minutes)
- Employee team/department
- Customer region/area
- Performance score (fast/slow completion)

---

## Related Documentation

- [Sales API Documentation](./api/sales.md) - Complete API reference
- [Query Filtering Implementation](./QUERY_FILTERING_IMPLEMENTATION.md) - Worker-based filtering
- [Worker Filtering Implementation](./WORKER_FILTERING_IMPLEMENTATION.md) - User vs worker filtering

---

**Last Updated**: December 18, 2025  
**Version**: 1.0.0
