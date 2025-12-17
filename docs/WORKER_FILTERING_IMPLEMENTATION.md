# Worker-Based Filtering Implementation

## Problem
User wanted to filter invoices by the **worker** (picker/packer) who performed the task, not by who created the invoice.

**Requirements:**
- Filter invoices by worker email (e.g., `zain@gmail.com`)
- If status=PICKED, show invoices picked by this user
- If status=PACKED, show invoices packed by this user
- User can only have one active task at a time, so need endpoint to return current task

## ✅ Solution Implemented

### 1. **New Endpoint: My Active Task** (RECOMMENDED)
**Endpoint:** `GET /api/sales/my-active-task/`

Returns the user's current active picking or packing task (if any).

**Response Examples:**

**Active Picking Task:**
```json
{
  "success": true,
  "message": "Active picking task found",
  "data": {
    "task_type": "PICKING",
    "session_id": 42,
    "start_time": "2025-12-17T10:30:00Z",
    "invoice": { /* full invoice details */ }
  }
}
```

**No Active Task:**
```json
{
  "success": true,
  "message": "No active task",
  "data": null
}
```

**Use Case:**
```javascript
// On app launch, check if user has unfinished work
const response = await api.get('/sales/my-active-task/');
if (response.data.data) {
  const { task_type, invoice } = response.data.data;
  navigateTo(`/${task_type.toLowerCase()}/${invoice.invoice_no}`);
} else {
  navigateTo('/dashboard');
}
```

---

### 2. **Enhanced List API: Worker Filter**
**Endpoint:** `GET /api/sales/invoices/?worker=email@domain.com`

Added `worker` query parameter to existing invoice list endpoint.

**How it works:**
- Filters invoices where the user was picker, packer, OR delivery person
- Checks across PickingSession, PackingSession, and DeliverySession
- Can be combined with status filter

**Examples:**

```bash
# All invoices worked on by zain@gmail.com
GET /api/sales/invoices/?worker=zain@gmail.com

# Picked invoices by zain@gmail.com
GET /api/sales/invoices/?status=PICKED&worker=zain@gmail.com

# Packed invoices by zain@gmail.com
GET /api/sales/invoices/?status=PACKED&worker=zain@gmail.com

# Currently picking/packing by zain@gmail.com
GET /api/sales/invoices/?status=PICKING&status=PACKING&worker=zain@gmail.com
```

---

## 🎯 Which Endpoint to Use?

### Use **My Active Task** endpoint when:
- ✅ User opens the app (check if they have unfinished work)
- ✅ Showing "Continue Your Task" button
- ✅ Navigation to current work
- ✅ Simple: returns only ONE invoice (or null)

### Use **Worker Filter** on List endpoint when:
- ✅ Showing history of all invoices user has worked on
- ✅ Filtered views (e.g., "All Picked by Me", "All Packed by Me")
- ✅ Dashboard statistics (count of invoices worked on)
- ✅ Complex filtering needs

---

## 📝 Code Changes

### Files Modified:

1. **apps/sales/views.py**
   - Updated `InvoiceListView.get_queryset()` to add `worker` filter
   - Created new `MyActiveTaskView` class

2. **apps/sales/urls.py**
   - Added `path("my-active-task/", MyActiveTaskView.as_view())`

3. **docs/api/sales.md**
   - Added `worker` parameter documentation
   - Added "My Active Task" endpoint documentation with examples

---

## 🧪 Testing Examples

### Test My Active Task:
```bash
# Start a picking session first
curl -X POST "http://localhost:8000/api/sales/picking/start/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invoice_no":"INV-001","user_email":"zain@gmail.com"}'

# Then check active task
curl -X GET "http://localhost:8000/api/sales/my-active-task/" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Worker Filter:
```bash
# Get all invoices picked by zain@gmail.com
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/sales/invoices/?status=PICKED&worker=zain@gmail.com"

# Get current tasks (picking or packing) by zain@gmail.com
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/sales/invoices/?status=PICKING&status=PACKING&worker=zain@gmail.com"
```

---

## 🚀 Frontend Implementation Examples

### Example 1: Check Active Task on App Launch
```javascript
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './services/api';

function App() {
  const navigate = useNavigate();
  
  useEffect(() => {
    checkActiveTask();
  }, []);
  
  async function checkActiveTask() {
    try {
      const response = await api.get('/sales/my-active-task/');
      const activeTask = response.data.data;
      
      if (activeTask) {
        const { task_type, invoice } = activeTask;
        // User has unfinished work, navigate to it
        if (task_type === 'PICKING') {
          navigate(`/picking/${invoice.invoice_no}`);
        } else if (task_type === 'PACKING') {
          navigate(`/packing/${invoice.invoice_no}`);
        }
      }
    } catch (error) {
      console.error('Error checking active task:', error);
    }
  }
  
  return <div>Loading...</div>;
}
```

### Example 2: Show "My Picked Invoices" List
```javascript
function MyPickedInvoices() {
  const [invoices, setInvoices] = useState([]);
  const userEmail = getCurrentUserEmail(); // from auth context
  
  useEffect(() => {
    // Get all invoices this user picked
    api.get(`/sales/invoices/?status=PICKED&worker=${userEmail}`)
      .then(response => setInvoices(response.data.results))
      .catch(error => console.error(error));
  }, [userEmail]);
  
  return (
    <div>
      <h2>Invoices I Picked ({invoices.length})</h2>
      {invoices.map(invoice => (
        <InvoiceCard key={invoice.id} invoice={invoice} />
      ))}
    </div>
  );
}
```

### Example 3: Dashboard with Active Task Banner
```javascript
function Dashboard() {
  const [activeTask, setActiveTask] = useState(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    api.get('/sales/my-active-task/')
      .then(response => setActiveTask(response.data.data));
  }, []);
  
  return (
    <div>
      {activeTask && (
        <div className="alert alert-warning">
          <p>You have an unfinished {activeTask.task_type} task</p>
          <button onClick={() => navigate(`/${activeTask.task_type.toLowerCase()}/${activeTask.invoice.invoice_no}`)}>
            Continue Task: {activeTask.invoice.invoice_no}
          </button>
        </div>
      )}
      
      <DashboardContent />
    </div>
  );
}
```

---

## 📊 Comparison: Before vs After

### Before:
```bash
# ❌ This didn't work correctly
GET /api/sales/invoices/?status=PICKED&user=zain@gmail.com
# Would filter by created_user, not picker
```

### After:
```bash
# ✅ Worker filter - shows invoices picked by this user
GET /api/sales/invoices/?status=PICKED&worker=zain@gmail.com

# ✅ My active task - simple endpoint for current work
GET /api/sales/my-active-task/
```

---

## 🎯 Summary

✅ **My Active Task Endpoint:** Simple, purpose-built for checking user's current work
✅ **Worker Filter:** Flexible filtering for invoice lists by picker/packer/delivery person
✅ **Proper Separation:** Created_user vs worker vs assigned user - now all handled correctly
✅ **Documentation:** Complete API docs with examples
✅ **Frontend Ready:** Example code for common use cases

**Ready to use!** Both solutions are implemented and documented.
