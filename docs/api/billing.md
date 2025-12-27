# Billing API Documentation

## Overview
The Billing API allows users to view their billed invoices and provides functionality to return invoices back to billing for corrections when issues are discovered during picking or packing.

## Key Features
- **User-specific invoice viewing**: Regular users see only their own created invoices
- **Admin view**: Admins/superadmins see all invoices
- **Return to billing**: Allows pickers/packers to return invoices when issues are found; return details are stored in a separate `InvoiceReturn` record and exposed under `return_info` in invoice responses.
- **Billing status tracking**: Tracks invoice states (BILLED, REVIEW, RE_INVOICED)
- **Invoice priority**: Invoices now include a `priority` field (LOW / MEDIUM / HIGH) to help order processing and task assignment

---

## Endpoints

### 1. List Billing Invoices

**GET** `/api/sales/billing/invoices/`

Retrieve a paginated list of invoices for the billing section.

**Authentication**: Required (Bearer token)

**Permissions**:
- Regular users see only invoices they created (matched by `created_user` or `created_by` field)
- Admin/superadmin see all invoices

**Query Parameters**:
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by invoice status | `?status=PENDING&status=PICKING` |
| `billing_status` | string | Filter by billing status | `?billing_status=RETURNED` |
| `priority` | string | Filter by invoice priority (LOW, MEDIUM, HIGH) | `?priority=HIGH` |
| `created_by` | string | Filter by creator (admin only) | `?created_by=john@example.com` |
| `page` | integer | Page number | `?page=2` |
| `page_size` | integer | Items per page (max 100) | `?page_size=50` |

**Response** (200 OK):
```json
{
  "count": 100,
  "next": "http://example.com/api/sales/billing/invoices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "invoice_no": "INV-001",
      "invoice_date": "2025-12-20",
      "status": "PENDING",
      "priority": "MEDIUM",
      "billing_status": "BILLED",
      "created_by": "john@example.com",
      "customer": {
        "code": "C001",
        "name": "ABC Pharmacy",
        "area": "Downtown",
        "address1": "123 Main St",
        "phone1": "555-1234",
        "email": "abc@pharmacy.com"
      },
      "salesman": {
        "id": 1,
        "name": "John Salesman",
        "phone": "555-5678"
      },
      "items": [
        {
          "id": 1,
          "name": "Paracetamol 500mg",
          "item_code": "MED001",
          "quantity": 100,
          "mrp": 5.50,
          "company_name": "PharmaCo",
          "packing": "Box of 10",
          "shelf_location": "A-12",
          "batch_no": "BATCH123",
          "expiry_date": "2026-12-31",
          "remarks": null
        }
      ],
      "total_amount": 550.00,
      "remarks": null,
      "return_info": null,
      "created_at": "2025-12-20T10:30:00Z"
    }
  ]
}
```

**Example Usage**:
```bash
# Get all your invoices
curl -X GET "http://localhost:8000/api/sales/billing/invoices/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get invoices under review only
curl -X GET "http://localhost:8000/api/sales/billing/invoices/?billing_status=REVIEW" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get pending invoices (admin)
curl -X GET "http://localhost:8000/api/sales/billing/invoices/?status=PENDING&created_by=john" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

### 2. Return Invoice to Billing

**POST** `/api/sales/billing/return/`

Return an invoice back to billing from the picking or packing section when issues are discovered.

**Authentication**: Required (Bearer token)

**Permissions**: Any authenticated user (typically pickers/packers)

**Conditions**:
- Invoice must be in `PICKING`, `PICKED`, or `PACKING` status
- Invoice must not already be in `RETURNED` billing status

**Request Body**:
```json
{
  "invoice_no": "INV-001",
  "return_reason": "Missing items in stock - Paracetamol unavailable",
  "user_email": "picker@example.com"  // optional, defaults to authenticated user
}
```

**Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `invoice_no` | string | Yes | Invoice number to return |
| `return_reason` | string | Yes | Detailed reason for return (missing items, wrong batch, out of stock, etc.) |
| `user_email` | string | No | Email of user returning the invoice (defaults to authenticated user) |

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Invoice INV-001 has been returned to billing for corrections",
  "data": {
    "invoice_no": "INV-001",
    "billing_status": "RETURNED",
    "return_reason": "Missing items in stock - Paracetamol unavailable",
    "returned_by": "picker@example.com",
    "returned_at": "2025-12-22T14:30:00Z"
  }
}
```

**Error Responses**:

**400 Bad Request** - Validation errors:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "invoice_no": ["Invoice not found."]
  }
}
```

**400 Bad Request** - Wrong status:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "invoice_no": ["Invoice in 'DELIVERED' state cannot be returned to billing. Only invoices in PICKING, PICKED, or PACKING state can be returned."]
  }
}
```

**400 Bad Request** - Already returned:
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "invoice_no": ["Invoice has already been returned to billing."]
  }
}
```

**Example Usage**:
```bash
# Return invoice with reason
curl -X POST "http://localhost:8000/api/sales/billing/return/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_no": "INV-001",
    "return_reason": "Out of stock - Item MED001 unavailable"
  }'

# Return invoice with specific user email
curl -X POST "http://localhost:8000/api/sales/billing/return/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_no": "INV-002",
    "return_reason": "Wrong batch number - Batch expired",
    "user_email": "packer@example.com"
  }'
```

---

## Billing Status Flow

```
BILLED (default)
   ↓
REVIEW (when returned from picking/packing/delivery)
   ↓
RE_INVOICED (after corrections and re-submission)
```

**Billing Status Values**:
- `BILLED`: Invoice has been initially billed
- `REVIEW`: Invoice has been sent to billing for review/corrections (an `InvoiceReturn` record is created)
- `RE_INVOICED`: Invoice has been corrected and re-submitted

---

## Invoice Status Flow with Returns

```
PENDING → PICKING → PICKED → PACKING → PACKED → DISPATCHED → DELIVERED
```

When an invoice is returned to billing:
1. Invoice `status` is set to `REVIEW` and `billing_status` is set to `REVIEW`
2. An `InvoiceReturn` record is created (accessible via `return_info` in responses) containing `return_reason`, `returned_by`, `returned_from_section`, and timestamps
3. Any active picking/packing sessions are marked as `CANCELLED`
4. The invoice can be corrected and re-processed

---

## Common Return Reasons

Here are common reasons for returning invoices to billing:

1. **Stock Issues**:
   - "Out of stock - Item [item_code] unavailable"
   - "Insufficient stock - Need [quantity] but only [available] in stock"

2. **Batch Issues**:
   - "Wrong batch number - Batch [batch_no] expired on [date]"
   - "Batch [batch_no] not found in system"
   - "Batch mismatch - Expected [batch1] but found [batch2]"

3. **Item Issues**:
   - "Missing items - [item_name] not found on shelf [location]"
   - "Item damaged - Cannot fulfill quantity for [item_name]"
   - "Item code mismatch - [item_code] does not match physical item"

4. **Quantity Issues**:
   - "Quantity discrepancy - Requested [qty1] but only [qty2] available"
   - "Partial fulfillment required - Cannot complete full order"

5. **Other Issues**:
   - "Customer information incorrect - Cannot process delivery"
   - "Duplicate invoice - Already processed as [invoice_no]"

---

## Real-time Updates

When an invoice is returned to billing, a real-time event is sent via Server-Sent Events (SSE):

**Event Channel**: `invoices`

**Event Data**:
```json
{
  "type": "invoice_review",
  "invoice_no": "INV-001",
  "sent_by": "picker@example.com",
  "review_reason": "Out of stock - Item MED001 unavailable",
  "returned_from_section": "PICKING",
  "timestamp": "2025-12-22T14:30:00Z"
}
```

**Subscribe to events**:
```javascript
const eventSource = new EventSource('http://localhost:8000/api/sales/sse/invoices/');
eventSource.addEventListener('message', (e) => {
  const data = JSON.parse(e.data);
  if (data.type === 'invoice_returned') {
    console.log('Invoice returned:', data.invoice_no);
    // Update UI to show returned invoice
  }
});
```

---

## Integration Examples

### Frontend: Display User's Invoices

```javascript
async function fetchMyInvoices() {
  const response = await fetch('/api/sales/billing/invoices/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const data = await response.json();
  displayInvoices(data.results);
}
```

### Frontend: Return Invoice Button

```javascript
async function returnInvoiceToBilling(invoiceNo, reason) {
  const response = await fetch('/api/sales/billing/return/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      invoice_no: invoiceNo,
      return_reason: reason
    })
  });
  
  const result = await response.json();
  if (result.success) {
    alert('Invoice returned to billing successfully');
    // Refresh invoice list
    fetchMyInvoices();
  } else {
    alert('Error: ' + result.message);
  }
}
```

### Admin Dashboard: View All Returned Invoices

```javascript
async function fetchReturnedInvoices() {
  const response = await fetch('/api/sales/billing/invoices/?billing_status=RETURNED', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  const data = await response.json();
  displayReturnedInvoices(data.results);
}
```

---

## Notes

1. **User Privacy**: Regular users can only see invoices they created. This is enforced by checking both `created_user` (FK) and `created_by` (string field).

2. **Admin Access**: Admins can see all invoices and filter by `created_by` to find specific user's invoices.

3. **Session Cancellation**: When an invoice is returned, any active picking or packing sessions are automatically cancelled with a note explaining the reason.

4. **Re-invoicing**: After corrections, the billing user should:
   - Update the invoice details
   - Change `billing_status` to `RE_INVOICED`
   - The invoice will then be available for picking again

5. **Audit Trail**: The system maintains complete audit information:
   - Who returned the invoice (`returned_by`)
   - When it was returned (`returned_at`)
   - Why it was returned (`return_reason`)

---

## Testing

### Test Case 1: Regular User Views Their Invoices
```bash
# Login as regular user
TOKEN=$(curl -X POST "/api/auth/login/" -d '{"email":"user@example.com","password":"password"}' | jq -r '.token')

# Get their invoices
curl -X GET "/api/sales/billing/invoices/" -H "Authorization: Bearer $TOKEN"
# Should only see invoices created by this user
```

### Test Case 2: Return Invoice from Picking
```bash
# Start picking an invoice
curl -X POST "/api/sales/picking/start/" -H "Authorization: Bearer $TOKEN" \
  -d '{"invoice_no":"INV-001","user_email":"picker@example.com"}'

# Discover issue and return to billing
curl -X POST "/api/sales/billing/return/" -H "Authorization: Bearer $TOKEN" \
  -d '{"invoice_no":"INV-001","return_reason":"Item out of stock"}'

# Verify invoice status is PENDING and billing_status is RETURNED
curl -X GET "/api/sales/invoices/1/" -H "Authorization: Bearer $TOKEN"
```

### Test Case 3: Admin Views All Returned Invoices
```bash
# Login as admin
ADMIN_TOKEN=$(curl -X POST "/api/auth/login/" -d '{"email":"admin@example.com","password":"adminpass"}' | jq -r '.token')

# Get all returned invoices
curl -X GET "/api/sales/billing/invoices/?billing_status=RETURNED" -H "Authorization: Bearer $ADMIN_TOKEN"
# Should see all returned invoices from all users
```
