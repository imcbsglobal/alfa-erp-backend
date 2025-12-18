# Sales API

Documentation for Sales module endpoints: invoice import and live updates (SSE).

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.example.com`

**Authentication Required:**
- DRF endpoints (APIView) in this module require JWT authentication (Default: `IsAuthenticated`).
- The SSE endpoint is an open Django view by default (no authentication). If you need to secure it, consult the `SSE and WebSocket` section below.

**Authorization Header:**
```
Authorization: Bearer <access_token>
```

---

## Overview

This module contains 3 main integration points:

- `GET /api/sales/invoices/` — List all invoices with pagination (includes customer, salesman, items)
- `POST /api/sales/import/invoice/` — Import an invoice (saves invoice, items, customer, salesman); authenticated
- `GET /api/sales/sse/invoices/` — Server-Sent Events endpoint that streams new invoices in real-time; open by default

### Notes about live updates
- The import view (`ImportInvoiceView`) pushes a message to an internal events queue that the SSE stream reads from.
- If your external system writes invoices directly to the database (bypassing this import endpoint), the SSE queue will not receive real-time events. Consider having your external system call this import endpoint or publish to a channel your Django app listens to (Postgres NOTIFY or Redis pub/sub).

---

## API Endpoints Summary

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/sales/invoices/` | Optional (IsAuthenticatedOrReadOnly) | List invoices (pagination + filters: `status`, `worker`, `user`, `created_by`) |
| GET | `/api/sales/invoices/{id}/` | Optional (IsAuthenticatedOrReadOnly) | Invoice detail with nested customer, items, salesman |
| POST | `/api/sales/import/invoice/` | API key or JWT (HasAPIKeyOrAuthenticated) | Import or update invoice (idempotent by `invoice_no`) |
| GET | `/api/sales/sse/invoices/` | Open by default (see notes) | Server-Sent Events stream of invoice events |
| GET | `/api/sales/picking/active/` | JWT (IsAuthenticated) | Get authenticated user's current picking task (admin may query others) |
| POST | `/api/sales/picking/start/` | JWT (IsAuthenticated) | Start a picking session (scan user email) |
| POST | `/api/sales/picking/complete/` | JWT (IsAuthenticated) | Complete picking (scan same user email) |
| GET | `/api/sales/packing/active/` | JWT (IsAuthenticated) | Get authenticated user's current packing task (admin may query others) |
| POST | `/api/sales/packing/start/` | JWT (IsAuthenticated) | Start a packing session (invoice must be PICKED) |
| POST | `/api/sales/packing/complete/` | JWT (IsAuthenticated) | Complete packing (scan same user email) |
| POST | `/api/sales/delivery/start/` | JWT (IsAuthenticated) | Start a delivery session (DIRECT/COURIER/INTERNAL) |
| POST | `/api/sales/delivery/complete/` | JWT (IsAuthenticated) | Complete delivery (confirm delivery status) |

---

## 1. List Invoices
`GET /api/sales/invoices/`

### Purpose
Retrieve a paginated list of all invoices with full details including customer, salesman, and line items.

### Authentication
Optional (IsAuthenticatedOrReadOnly) - public read access by default

### Query Parameters
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by invoice status. Can specify multiple times for OR filtering
  - Valid values: `PENDING`, `PICKING`, `PICKED`, `PACKING`, `PACKED`, `DISPATCHED`, `DELIVERED`
  - Examples: `?status=PENDING` or `?status=PICKING&status=PACKING`
- `user` (integer, optional): Filter by created_user ID (invoices created by specific authenticated user)
- `created_by` (string, optional): Filter by created_by field (username/identifier, case-insensitive contains match)
- `worker` (string, optional): Filter by worker email - shows invoices where this user was the picker, packer, or delivery person

### Examples
```bash
# Get all pending invoices
GET /api/sales/invoices/?status=PENDING

# Get invoices that are either picking or packing
GET /api/sales/invoices/?status=PICKING&status=PACKING

# Get invoices created by user ID 5
GET /api/sales/invoices/?user=5

# Get invoices created by username containing "admin"
GET /api/sales/invoices/?created_by=admin

# Get invoices picked by zain@gmail.com
GET /api/sales/invoices/?worker=zain@gmail.com

# Get picked invoices worked on by zain@gmail.com
GET /api/sales/invoices/?status=PICKED&worker=zain@gmail.com

# Combine filters: pending invoices created by admin, page 2
GET /api/sales/invoices/?status=PENDING&created_by=admin&page=2
```

### Response
**Success (200 OK):**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/sales/invoices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 31,
      "invoice_no": "INV-77052",
      "invoice_date": "2025-01-18",
      "customer": {
        "code": "CUST-889",
        "name": "LifeCare Pharmacy",
        "area": "Kozhikode",
        "address1": "Near Railway Station",
        "address2": "",
        "phone1": "9876543210",
        "phone2": "",
        "email": "lifecare@shop.com"
      },
      "salesman": {
        "id": 1,
        "name": "Ajay",
        "phone": ""
      },
      "created_by": "admin",
      "items": [
        {
          "id": 45,
          "name": "Paracetamol 650mg",
          "item_code": "PR650",
          "quantity": 20,
          "mrp": 3.50,
          "company_name": "Sun Pharma",
          "packing": "10x10 Tablets",
          "shelf_location": "R-12",
          "remarks": ""
        },
        {
          "id": 46,
          "name": "Otrivin Nasal Spray",
          "item_code": "OTN10",
          "quantity": 10,
          "mrp": 85.00,
          "company_name": "Novartis",
          "packing": "10ml Bottle",
          "shelf_location": "G-04",
          "remarks": ""
        }
      ],
      "total_amount": 920.0,
      "remarks": null,
      "created_at": "2025-12-10T12:14:31.800134Z"
    }
  ]
}
```

### cURL example
```bash
curl -X GET "http://localhost:8000/api/sales/invoices/?page=1&page_size=20"
```

---

## 2. Get Invoice by ID
`GET /api/sales/invoices/{id}/`

### Purpose
Retrieve a single invoice by its primary key with nested details (customer, salesman, items).

### Authentication
Optional (IsAuthenticatedOrReadOnly) - public read access by default

### Response
**Success (200 OK)**
```json
{
  "id": 31,
  "invoice_no": "INV-77052",
  "invoice_date": "2025-01-18",
  "customer": { ... },
  "salesman": { ... },
  "created_by": "admin",
  "items": [...],
  "total_amount": 920.0,
  "remarks": null,
  "created_at": "2025-12-10T12:14:31.800134Z"
}
```

### cURL example
```bash
curl -X GET "http://localhost:8000/api/sales/invoices/31/"
```

---

## 3. My Active Picking Task
`GET /api/sales/picking/active/`

### Purpose
Get the current active picking task for the authenticated user. Since a user can only work on one task at a time (enforced by the system), this returns their current picking invoice if they have an active picking session.

**Use Case:** When a picker opens the app, call this endpoint to check if they have an unfinished picking task.

### Authentication
Required (Bearer token)

### Query Parameters
- `user` (string, optional): Look up by user ID (UUID) or email. If present and the requester is an admin/superadmin/staff, returns the specified user's active picking task.
- `user_email` (string, optional): Alias for `user` (email address preferred).

### Permissions
- If the request asks for another user's active task (via `user` or `user_email`), the caller must be an admin/superadmin/staff (checked via `User.is_admin_or_superadmin()`).

### Response

**Active Picking Task (200 OK)**
```json
{
  "success": true,
  "message": "Active picking task found for zain@gmail.com",
  "data": {
    "task_type": "PICKING",
    "session_id": 42,
    "start_time": "2025-12-17T10:30:00Z",
    "invoice": {
      "id": 31,
      "invoice_no": "INV-77052",
      "invoice_date": "2025-01-18",
      "status": "PICKING",
      "customer": {
        "code": "CUST-889",
        "name": "LifeCare Pharmacy",
        "area": "Kozhikode",
        "address1": "Near Railway Station",
        "phone1": "9876543210"
      },
      "items": [
        {
          "id": 45,
          "name": "Paracetamol 650mg",
          "item_code": "PR650",
          "quantity": 20,
          "shelf_location": "R-12"
        }
      ],
      "total_amount": 920.0
    }
  }
}
```

**No Active Picking Task (200 OK)**
```json
{
  "success": true,
  "message": "No active picking task",
  "data": null
}
```

### cURL example
```bash
curl -X GET "http://localhost:8000/api/sales/picking/active/" \
  -H "Authorization: Bearer <access_token>"

# Admin checking another user's active picking task
curl -X GET "http://localhost:8000/api/sales/picking/active/?user_email=zain@gmail.com" \
  -H "Authorization: Bearer <admin_token>"
```

---

## 4. My Active Packing Task
`GET /api/sales/packing/active/`

### Purpose
Get the current active packing task for the authenticated user. Since a user can only work on one task at a time (enforced by the system), this returns their current packing invoice if they have an active packing session.

**Use Case:** When a packer opens the app, call this endpoint to check if they have an unfinished packing task.

### Authentication
Required (Bearer token)

### Query Parameters
- `user` (string, optional): Look up by user ID (UUID) or email. If present and the requester is an admin/superadmin/staff, returns the specified user's active packing task.
- `user_email` (string, optional): Alias for `user` (email address preferred).

### Permissions
- If the request asks for another user's active task (via `user` or `user_email`), the caller must be an admin/superadmin/staff (checked via `User.is_admin_or_superadmin()`).

### Response

**Active Packing Task (200 OK)**
```json
{
  "success": true,
  "message": "Active packing task found for sara@gmail.com",
  "data": {
    "task_type": "PACKING",
    "session_id": 58,
    "start_time": "2025-12-17T11:15:00Z",
    "invoice": {
      "id": 45,
      "invoice_no": "INV-77099",
      "invoice_date": "2025-01-18",
      "status": "PACKING",
      "customer": { ... },
      "items": [...],
      "total_amount": 1250.0
    }
  }
}
```



**No Active Packing Task (200 OK)**
```json
{
  "success": true,
  "message": "No active packing task",
  "data": null
}
```

### cURL example
```bash
curl -X GET "http://localhost:8000/api/sales/packing/active/" \
  -H "Authorization: Bearer <access_token>"

# Admin checking another user's active packing task
curl -X GET "http://localhost:8000/api/sales/packing/active/?user_email=sara@gmail.com" \
  -H "Authorization: Bearer <admin_token>"
```

### Frontend Integration Example
```javascript
// Picker app: Check for active picking task on app launch
async function checkActivePickingTask() {
  try {
    const response = await api.get('/sales/picking/active/');
    
    if (response.data.data) {
      const { invoice } = response.data.data;
      // User has unfinished picking work, navigate to it
      navigateTo(`/picking/${invoice.invoice_no}`);
    } else {
      // No active task, show available invoices to pick
      navigateTo('/picking/dashboard');
    }
  } catch (error) {
    console.error('Error checking active picking task:', error);
  }
}

// Packer app: Check for active packing task on app launch
async function checkActivePackingTask() {
  try {
    const response = await api.get('/sales/packing/active/');
    
    if (response.data.data) {
      const { invoice } = response.data.data;
      // User has unfinished packing work, navigate to it
      navigateTo(`/packing/${invoice.invoice_no}`);
    } else {
      // No active task, show picked invoices ready for packing
      navigateTo('/packing/dashboard');
    }
  } catch (error) {
    console.error('Error checking active packing task:', error);
  }
}

// Admin dashboard: Check any user's active task
async function checkUserActiveTask(userEmail, taskType) {
  const endpoint = taskType === 'PICKING' 
    ? '/sales/picking/active/' 
    : '/sales/packing/active/';
  
  const response = await api.get(`${endpoint}?user_email=${userEmail}`);
  return response.data.data; // null if no active task
}
```

---

## 4. Import Invoice
`POST /api/sales/import/invoice/`

### Purpose
Import a new invoice with nested customer and invoice items. The endpoint will create the salesman and customer if they don't exist and attach invoice items.

### Authentication
Required (Bearer token - JWT)

### Request Body
```json
{
  "invoice_no": "INV-10222",

### Import Authentication (API key)

This import endpoint supports a simple API key for external systems. The client must include the header:

```
X-API-KEY: <your-import-api-key>
```

Set the key on the server using the `SALES_IMPORT_API_KEY` environment variable (recommended) or in `config.settings.base.SALES_IMPORT_API_KEY` for development. The server will return `401 Unauthorized` if the key is missing or invalid.
  "invoice_date": "2025-01-18",
  "salesman": "Ajay",
  "created_by": "admin",
  "customer": {
    "code": "CUST-889",
    "name": "LifeCare Pharmacy",
    "area": "Kozhikode",
    "address1": "Near Railway Station",
    "address2": "",
    "phone1": "9876543210",
    "phone2": "",
    "email": "lifecare@shop.com"
  },
  "items": [
    {
      "name": "Paracetamol 650mg",
      "item_code": "PR650",
      "quantity": 20,
      "mrp": 3.50,
      "company_name": "Sun Pharma",
      "packing": "10x10 Tablets",
      "shelf_location": "R-12",
      "remarks": ""
    },
    {
      "name": "Otrivin Nasal Spray",
      "item_code": "OTN10",
      "quantity": 10,
      "mrp": 85.00,
      "company_name": "Novartis",
      "packing": "10ml Bottle",
      "shelf_location": "G-04",
      "remarks": ""
    }
  ]
}
```

### Response
**Success (201 Created)**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Invoice imported successfully",
  "data": {
    "id": 1,
    "invoice_no": "INV-10222",
    "total_amount": 920.0
  }
}
```

**Validation Error (400 Bad Request)**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation failed",
  "errors": {...}
}
```

### cURL example
```bash
curl -X POST "http://localhost:8000/api/sales/import/invoice/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 5. SSE: Invoice Stream
`GET /api/sales/sse/invoices/`

### Purpose
Server-Sent Events (SSE) endpoint used for live invoice streaming. It reads from an in-memory queue maintained by the server and streams JSON events to connected clients.

### Authentication
By default, this endpoint is a regular Django view (`StreamingHttpResponse`) without DRF authentication. If you require authorization, either:
- Protect the URL using middleware, or
- Implement auth inside `invoice_stream` and return `401` for unauthenticated requests.

### Event Structure
Each event is sent in SSE `data: <json>` format (with newline+newline at the end). The payload matches the invoice list API format with full nested data.

Example payload (JSON):
```json
{
  "id": 31,
  "invoice_no": "INV-77052",
  "invoice_date": "2025-01-18",
  "customer": {
    "code": "CUST-889",
    "name": "LifeCare Pharmacy",
    "area": "Kozhikode",
    "address1": "Near Railway Station",
    "address2": "",
    "phone1": "9876543210",
    "phone2": "",
    "email": "lifecare@shop.com"
  },
  "salesman": {
    "id": 1,
    "name": "Ajay",
    "phone": ""
  },
  "created_by": "admin",
  "items": [
    {
      "id": 45,
      "name": "Paracetamol 650mg",
      "item_code": "PR650",
      "quantity": 20,
      "mrp": 3.50,
      "company_name": "Sun Pharma",
      "packing": "10x10 Tablets",
      "shelf_location": "R-12",
      "remarks": ""
    },
    {
      "id": 46,
      "name": "Otrivin Nasal Spray",
      "item_code": "OTN10",
      "quantity": 10,
      "mrp": 85.00,
      "company_name": "Novartis",
      "packing": "10ml Bottle",
      "shelf_location": "G-04",
      "remarks": ""
    }
  ],
  "total_amount": 920.0,
  "remarks": null,
  "created_at": "2025-12-10T12:14:31.800134Z"
}
```

Keepalive pings are sent every 1 second as `: keep-alive` to maintain connection.

### Client Example (JavaScript)
```javascript
const es = new EventSource('http://localhost:8000/api/sales/sse/invoices/');

es.onmessage = (evt) => {
  const event = JSON.parse(evt.data);
  console.log('New invoice event:', event);
  // update the UI here, e.g., prepend to list or show a toast
};

es.onerror = (err) => {
  console.error('SSE connection error', err);
};
```

### Notes
- Because Django's `StreamingHttpResponse` is synchronous, it is recommended to run this under a server that supports streaming well, such as `gunicorn` or `daphne` (if you're using ASGI/WebSocket alternatives).
- For production-scalability, prefer WebSockets (Django Channels) or a Redis-backed pub/sub for event delivery — SSE with an in-memory queue is not shared across multiple instances.

### Status-Based Filtering for SSE ⚠️
**Current Implementation Review:**
The SSE endpoint (`/api/sales/sse/invoices/`) uses `django-eventstream` which broadcasts all invoice events to a single channel. It does **not support per-connection query parameter filtering** (e.g., `?status=PENDING`).

**Recommended Approaches:**

1. **Client-Side Filtering (Simple & Recommended):**
   ```javascript
   const es = new EventSource('http://localhost:8000/api/sales/sse/invoices/');
   es.onmessage = (evt) => {
     const invoice = JSON.parse(evt.data);
     // Filter on client side based on your needs
     if (invoice.status === 'PENDING' || invoice.status === 'PICKING') {
       updateUI(invoice);
     }
   };
   ```

2. **Use REST API with Polling for Filtered Data:**
   For status-specific views, use the filtered list endpoint with periodic polling:
   ```javascript
   // Poll every 5 seconds for pending invoices
   setInterval(() => {
     fetch('/api/sales/invoices/?status=PENDING')
       .then(r => r.json())
       .then(data => updateDashboard(data.results));
   }, 5000);
   ```

3. **Hybrid Approach (SSE + REST):**
   - Use SSE for real-time notifications of any change
   - On receiving SSE event, fetch filtered data from REST API
   - Best balance of real-time updates and filtered data
   ```javascript
   const es = new EventSource('http://localhost:8000/api/sales/sse/invoices/');
   es.onmessage = () => {
     // Any invoice changed, refresh filtered view
     fetch('/api/sales/invoices/?status=PENDING')
       .then(r => r.json())
       .then(data => updatePendingInvoices(data.results));
   };
   ```

4. **Advanced: Multiple Channels (Requires Custom Implementation):**
   - Modify backend to send events to status-specific channels: `invoices-pending`, `invoices-picking`, etc.
   - Connect to specific channels: `/api/sales/sse/invoices-pending/`
   - Requires custom eventstream configuration and changes to event emission logic

---

## 6. Picking, Packing & Delivery Workflow ✅

These endpoints implement the warehouse workflow using employee email scanning at each stage. Authenticated users scan their email (from QR code or barcode) to start and/or complete jobs. Each endpoint validates invoice state and user identity and emits an SSE event to `/api/sales/sse/invoices/` when status changes.

### Status Transition Summary
- CREATED → PENDING (picking started)
- PENDING → PICKED (picking completed)
- PICKED → PACKING (packing started)
- PACKING → PACKED (packing completed)
- PACKED → DISPATCHED (delivery started)
- DISPATCHED → DELIVERED (delivery completed)

> Note: The server enforces sequential transitions and prevents duplicate sessions.

---

### 4.1 Start Picking
`POST /api/sales/picking/start/`

Purpose: Create a picking session and set invoice status to `PENDING` when a user scans their email to begin picking.

Authentication: Required (Bearer token)

Request body:
```json
{
  "invoice_no": "INV-001",
  "user_email": "john.doe@company.com",
  "notes": "Starting picking"
}
```

Success (201 Created):
```json
{
  "success": true,
  "message": "Picking started by John Doe",
  "data": {
    "id": 12,
    "invoice": 31,
    "invoice_no": "INV-001",
    "picker": "uuid-of-picker",
    "picker_name": "John Doe",
    "picker_email": "john.doe@company.com",
    "start_time": "2025-12-10T12:30:00Z",
    "picking_status": "PREPARING",
    "notes": "Starting picking",
    "duration_minutes": null
  }
}
```

Errors:
- 400 Bad Request — validation errors (invoice not found, invalid status, user email not found, or picking already exists)
- 401 Unauthorized — missing/invalid token

cURL example:
```bash
curl -X POST "http://localhost:8000/api/sales/picking/start/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"invoice_no":"INV-001","user_email":"john.doe@company.com","notes":"Starting picking"}'
```

---

### 4.2 Complete Picking
`POST /api/sales/picking/complete/`

Purpose: User scans their email to confirm picking completion. The system verifies the scanned email matches the user who started the picking session. Records `end_time`, sets `picking_status` to `PICKED`, and updates invoice status to `PICKED`.

Request body:
```json
{
  "invoice_no": "INV-001",
  "user_email": "john.doe@company.com",
  "notes": "Picked all items"
}
```

Success (200 OK):
```json
{
  "success": true,
  "message": "Picking completed for INV-001",
  "data": {
    "id": 12,
    "invoice_no": "INV-001",
    "picker": "uuid-of-picker",
    "picker_name": "John Doe",
    "picker_email": "john.doe@company.com",
    "start_time": "2025-12-10T12:30:00Z",
    "end_time": "2025-12-10T12:45:00Z",
    "picking_status": "PICKED",
    "duration_minutes": 15.0
  }
}
```

Errors include:
- 400 — invoice not found, no picking session, email mismatch, or picking already completed

---

### 4.3 Start Packing
`POST /api/sales/packing/start/`

Purpose: Start a packing session. The invoice must be in `PICKED` status before packing begins.

Request body:
```json
{
  "invoice_no": "INV-001",
  "user_email": "jane.smith@company.com",
  "notes": "Starting packing"
}
```

Success (201 Created): returns `PackingSessionReadSerializer` with `packing_status` `IN_PROGRESS` and sets invoice status to `PACKING`.

Errors:
- 400 — invoice must be in PICKED state, duplicate packing session, invalid user email

---

### 4.4 Complete Packing
`POST /api/sales/packing/complete/`

Purpose: User scans email to complete packing; verifies same user started packing. Sets `packing_status` to `PACKED` and invoice status to `PACKED`.

Request body:
```json
{
  "invoice_no": "INV-001",
  "user_email": "jane.smith@company.com",
  "notes": "Packed and ready"
}
```

Success (200 OK): returns updated packing session with `end_time` and `duration_minutes`.

---

### 4.5 Start Delivery
`POST /api/sales/delivery/start/`

Purpose: Create a delivery session and set invoice status to `DISPATCHED`. Delivery has three types:
- `DIRECT` — requires user email scan (assigned delivery person)
- `COURIER` — requires `courier_name` and optional user_email
- `INTERNAL` — requires user email scan

Request body examples:

DIRECT / INTERNAL
```json
{
  "invoice_no": "INV-001",
  "user_email": "driver@company.com",
  "delivery_type": "DIRECT",
  "notes": "Delivering to ABC shop"
}
```

COURIER
```json
{
  "invoice_no": "INV-001",
  "delivery_type": "COURIER",
  "courier_name": "DHL Express",
  "tracking_no": "TRK-12345",
  "notes": "Handed to courier"
}
```

Success (201 Created): returns created `DeliverySession` and sets invoice status to `DISPATCHED`.

Validation errors (400): invoice not in `PACKED` status, missing courier_name for COURIER, or missing user_email for DIRECT/INTERNAL.

---

### 4.6 Complete Delivery
`POST /api/sales/delivery/complete/`

Purpose: Confirm delivery. For DIRECT/INTERNAL deliveries, the scanned `user_email` must match assigned delivery user. For COURIER deliveries, `user_email` is optional. Sets `delivery_status` (`DELIVERED` or `IN_TRANSIT`) and updates invoice status (`DELIVERED` when delivered).

Request body:
```json
{
  "invoice_no": "INV-001",
  "user_email": "driver@company.com",
  "delivery_status": "DELIVERED",
  "notes": "Delivered to counter"
}
```

Success (200 OK): returns updated delivery session and invoice status.

Errors:
- 400 — invoice/delivery session not found, user email mismatch for DIRECT/INTERNAL, or delivery already completed

---

### JavaScript / Client integration tips 💡
- Use your barcode/QR scanner to read employee emails and send them as `user_email` in requests above.
- After each successful state transition the server emits an SSE event to `/api/sales/sse/invoices/` — listen with `EventSource` to update UI in real-time.

Client example (axios + EventSource):
```javascript
// Start picking (scanner supplies user_email)
await axios.post(`${API_BASE_URL}/sales/picking/start/`, { 
  invoice_no: 'INV-001', 
  user_email: 'john.doe@company.com' 
}, { 
  headers: { Authorization: `Bearer ${token}`}
});

// Complete picking
await axios.post(`${API_BASE_URL}/sales/picking/complete/`, { 
  invoice_no: 'INV-001', 
  user_email: 'john.doe@company.com' 
}, { 
  headers: { Authorization: `Bearer ${token}`}
});

// Listen for invoice updates
const es = new EventSource(`${API_BASE_URL}/sales/sse/invoices/`);
es.onmessage = (evt) => {
  const invoice = JSON.parse(evt.data);
  // refresh UI for invoice.invoice_no
}
```

---

## Data Model Overview
**Salesman**
- `name` (string)
- `phone` (string)

**Customer**
- `code` (string, unique)
- `name`, `area`, `address1`, `address2`, `phone1`, `phone2`, `email`

**Invoice**
- `invoice_no` (string, unique)
- `invoice_date` (date)
- `salesman` (FK to Salesman)
- `created_by` (string, optional) - Username/identifier from import payload
- `created_user` (FK to User) - Authenticated user who imported (set automatically)
- `customer` (FK to Customer)
- `remarks` (text)
- `created_at` (datetime, auto)

**InvoiceItem**
- `invoice` (FK)
- `name` - Item/product name
- `item_code`, `quantity`, `mrp`, `company_name`, `packing`, `shelf_location`, `remarks`

---

## Best Practices & Integration Tips
- Use the `import/invoice/` endpoint for all invoice entries when you want the SSE notifications to be emitted.
- If the source cannot call HTTP, use Postgres triggers + `NOTIFY` or Redis pub/sub to inform Django about external inserts — then broadcast via WebSockets or SSE.
- For secure, production-ready streaming and multi-instance support, implement a channel layer (Redis) + Django Channels and broadcast events to the appropriate groups.

---

## Future Endpoints (Suggestions)
You can extend the Sales module with helpful endpoints:
- `GET /api/sales/invoices/{id}/` — Invoice detail by ID
- `POST /api/sales/invoices/{id}/items/` — Add items to existing invoice
- `PUT/PATCH /api/sales/invoices/{id}/` — Update invoice details
- `DELETE /api/sales/invoices/{id}/` — Soft-delete invoice (set `is_active`)
- `GET /api/sales/invoices/?search=` — Add search/filter by invoice_no, customer name, date range

Add them when you have full CRUD implemented and update this doc accordingly.

---

## Troubleshooting
- If SSE clients do not receive messages, confirm:
  - Your import endpoint pushes events to `invoice_events` deque.
  - Long-running connections are allowed by your server/proxy (Nginx, Cloudflare, etc.).
  - You are using a single process (in-memory queue doesn't work across multiple server instances).

- If you see duplicate invoices or missing items, validate importer idempotency: the `invoice_no` is the unique identifier.

---

If you want, I can also add:
- Example code for a Postgres LISTEN/NOTIFY bridge
- Django Channels-based WebSocket consumer for scalable real-time updates

---

