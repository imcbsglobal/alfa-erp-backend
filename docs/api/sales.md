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

## 1. List Invoices
`GET /api/sales/invoices/`

### Purpose
Retrieve a paginated list of all invoices with full details including customer, salesman, and line items.

### Authentication
Optional (IsAuthenticatedOrReadOnly) - public read access by default

### Query Parameters
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20, max: 100)

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
          "shelf_location": "R-12",
          "remarks": ""
        },
        {
          "id": 46,
          "name": "Otrivin Nasal Spray",
          "item_code": "OTN10",
          "quantity": 10,
          "mrp": 85.00,
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

## 2. Import Invoice
`POST /api/sales/import/invoice/`

### Purpose
Import a new invoice with nested customer and invoice items. The endpoint will create the salesman and customer if they don't exist and attach invoice items.

### Authentication
Required (Bearer token - JWT)

### Request Body
```json
{
  "invoice_no": "INV-10222",
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
      "shelf_location": "R-12",
      "remarks": ""
    },
    {
      "name": "Otrivin Nasal Spray",
      "item_code": "OTN10",
      "quantity": 10,
      "mrp": 85.00,
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

## 3. SSE: Invoice Stream
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
      "shelf_location": "R-12",
      "remarks": ""
    },
    {
      "id": 46,
      "name": "Otrivin Nasal Spray",
      "item_code": "OTN10",
      "quantity": 10,
      "mrp": 85.00,
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
- `item_code`, `quantity`, `mrp`, `shelf_location`, `remarks`

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

