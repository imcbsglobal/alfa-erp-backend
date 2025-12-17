# Import Invoice API (External Integration)

This document describes the Import Invoice API for external systems to submit invoices into ALFA ERP.

Endpoint

- POST /api/sales/import/invoice/

Description

- Accepts a single invoice payload containing customer and invoice items.
- Creates/updates the `Customer` and `Salesman` records automatically when necessary.
- Emits a Server-Sent Event (SSE) to the live invoice stream when the invoice is created (if running on the same process).

Authentication

- The endpoint supports either JWT authentication (normal users) OR a simple API key (recommended for external services).
- When using an API key, send the header:

```
X-API-KEY: WEDFBNPOIUFSDFTY
```

- The server setting name is `SALES_IMPORT_API_KEY`. Set it on the environment for production.

Sample Payload

```json
{
  "invoice_no": "LTPI-77282",
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

cURL Example (API key)

```bash
curl -X POST "http://localhost:8000/api/sales/import/invoice/" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-import-api-key" \
  -d @invoice.json
```

cURL Example (JWT)

```bash
curl -X POST "http://localhost:8000/api/sales/import/invoice/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d @invoice.json
```

Success Response (201 Created)

```json
{
  "success": true,
  "message": "Invoice imported successfully",
  "data": {
    "id": 123,
    "invoice_no": "LTPI-77282",
    "total_amount": 920.0
  }
}
```

Error Responses

- 401 Unauthorized (Missing/Invalid API key / missing JWT)

```json
{
  "success": false,
  "message": "Invalid API key"
}
```

- 400 Bad Request (Payload validation failed)

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "invoice_no": ["This field is required."]
  }
}
```

- 409 Conflict (Invoice already exists - duplicate invoice_no)

```json
{
  "success": false,
  "message": "Invoice with this invoice_no already exists.",
  "data": { "id": 12, "invoice_no": "LTPI-77282" }
}
```

Important Details / Integration Tips

- Idempotency: `invoice_no` is unique and acts as the idempotency key. If an invoice with same `invoice_no` already exists, the import will return 409.
- Created fields:
  - `created_by` (string): you can pass this in the payload for reference
  - `created_user` (nullable FK): if you authenticate using JWT, the `created_user` will be set to that user. If you use the API key, `created_user` will be left null.
- SSE: When an invoice is successfully created via this endpoint, the server will push the invoice payload to `/api/sales/sse/invoices/` (if SSE is enabled and this process handles SSE). If you run multiple worker processes, consider using a shared pub/sub (Redis) if you want the SSE events to be visible across workers.
- Rate limiting & Security: Consider IP whitelisting, HTTPS, rotating keys, or upgrading to `django-rest-framework-api-key` for production.
- Timestamps: `invoice_date` must follow a date format (`YYYY-MM-DD`). `created_at` is set by the server when created.

Troubleshooting

- If you receive `401: Authentication credentials were not provided.`:
  - Make sure you used `X-API-KEY` header, OR use a valid JWT token in `Authorization: Bearer <token>` header.
  - Verify `SALES_IMPORT_API_KEY` is set correctly on the server (environment variable). The import view accepts either API key or JWT auth.

- If you see `: keep-alive` in SSE but no invoice event after import:
  - Ensure the same process that receives the import handles SSE (in-memory queue), or use Redis pub/sub/Channels for multi-process broadcasting.

Contact/Ownership

- If you need a new API key created/rotated, contact the ALFA devops team or DB admin to provision a key and share securely (do not send keys over email unencrypted).

---

If you'd like, I can also add an example script for the external software in Node/Python that obtains the API key from environment and posts the JSON payload to this endpoint with proper error handling and retry behavior.