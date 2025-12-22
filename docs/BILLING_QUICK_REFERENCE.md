# Billing Section - Quick Reference Guide

## 🎯 Quick Start

### For Backend Developers

**New Model Fields Added to Invoice:**
```python
invoice.billing_status  # "BILLED", "REVIEW", "RE_INVOICED"
# Use the related `invoice_return` / serializer `return_info` for details
invoice.return_info.return_reason   # Text explaining why returned
invoice.return_info.returned_by     # User who returned it
invoice.return_info.returned_at     # Timestamp of return
```

**New API Endpoints:**
```
GET  /api/sales/billing/invoices/  - List user's invoices
POST /api/sales/billing/return/    - Return invoice to billing
```

---

## 📋 Common Use Cases

### 1. Display User's Invoices (Frontend)
```javascript
// Fetch invoices for current user
const response = await fetch('/api/sales/billing/invoices/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const data = await response.json();

// Display with pagination
data.results.forEach(invoice => {
  console.log(invoice.invoice_no, invoice.billing_status);
});
```

### 2. Show Only Invoices Under Review
```javascript
const response = await fetch(
  '/api/sales/billing/invoices/?billing_status=REVIEW',
  { headers: { 'Authorization': `Bearer ${token}` }}
);
```

### 3. Return an Invoice (from Picking/Packing)
```javascript
const response = await fetch('/api/sales/billing/return/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    invoice_no: 'INV-001',
    return_reason: 'Out of stock - Item MED001 not available'
  })
});

const result = await response.json();
if (result.success) {
  alert('Invoice returned successfully');
}
```

---

## 🔐 Permissions

| User Type | Can View | Can Return |
|-----------|----------|------------|
| Regular User | Only their own invoices | Any invoice in `PICKING`, `PICKED`, `PACKING`, `PACKED`, or `DISPATCHED` state |
| Admin | All invoices | Any invoice in `PICKING`, `PICKED`, `PACKING`, `PACKED`, or `DISPATCHED` state |

---

## ⚡ Real-time Events

Subscribe to invoice returns:
```javascript
const eventSource = new EventSource('/api/sales/sse/invoices/');
eventSource.addEventListener('message', (e) => {
  const data = JSON.parse(e.data);
  if (data.type === 'invoice_review') {
    showNotification(`Invoice ${data.invoice_no} returned by ${data.sent_by} from ${data.returned_from_section}: ${data.review_reason}`);
  }
});
```

---

## 🔄 Return Workflow

```
1. Picker/Packer discovers issue during picking/packing
   ↓
2. Clicks "Return to Billing" button
   ↓
3. Enters return reason (e.g., "Out of stock")
   ↓
4. POST to /api/sales/billing/return/
   ↓
5. Invoice status → REVIEW
   billing_status → REVIEW
   InvoiceReturn record created (accessible via `return_info`)
   Active sessions → CANCELLED
   ↓
6. Billing user sees returned invoice in dashboard
   ↓
7. Billing user corrects the issue
   ↓
8. Sets billing_status → RE_INVOICED
   ↓
9. Invoice ready for picking again
```

---

## 📝 Common Return Reasons (Templates)

Use these predefined reasons in your UI:

**Stock Issues:**
- "Out of stock - Item {item_code} not available"
- "Insufficient stock - Need {qty} but only {available} available"

**Batch Issues:**
- "Wrong batch number - Batch {batch_no} expired"
- "Batch {batch_no} not found in system"

**Item Issues:**
- "Missing items - {item_name} not on shelf {location}"
- "Item damaged - Cannot fulfill quantity"

**Quantity Issues:**
- "Quantity discrepancy - Requested {qty1} but only {qty2} available"

---

## 🧪 Testing Commands

```bash
# Check for syntax errors
python manage.py check

# Test invoice creation
curl -X POST "/api/sales/import/invoice/" \
  -H "Authorization: Bearer $TOKEN" \
  -d @invoice_data.json

# Test view user's invoices
curl -X GET "/api/sales/billing/invoices/" \
  -H "Authorization: Bearer $TOKEN"

# Test return invoice
curl -X POST "/api/sales/billing/return/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_no": "INV-001",
    "return_reason": "Out of stock"
  }'
```

---

## 🐛 Troubleshooting

**Issue:** "Invoice not found"
- Check invoice_no is correct
- Verify invoice exists in database

**Issue:** "Invoice in 'X' state cannot be returned"
- Only invoices in `PICKING`, `PICKED`, `PACKING`, `PACKED`, or `DISPATCHED` can be returned
- Check current invoice status

**Issue:** "Invoice has already been returned"
- Invoice already has billing_status=RETURNED
- Cannot return twice - must be processed first

**Issue:** User sees no invoices
- Verify user has created invoices
- Check created_by field matches user email
- Check created_user FK is set

---

## 📊 Database Queries

```python
# Get all invoices under review
Invoice.objects.filter(billing_status='REVIEW')

# Get user's invoices
Invoice.objects.filter(
    Q(created_user=user) | Q(created_by=user.email)
)

# Get invoices returned today
from django.utils import timezone
from apps.sales.models import InvoiceReturn

today = timezone.now().date()
InvoiceReturn.objects.filter(
    returned_at__date=today
)

# Most common return reasons
from django.db.models import Count
InvoiceReturn.objects.values('return_reason').annotate(
    count=Count('id')
).order_by('-count')
```

---

## 🎨 UI Components Needed

### 1. Billing Dashboard
- Table showing user's invoices
- Filter by status and billing_status
- Show return reason in tooltip/modal
- Highlight returned invoices

### 2. Return Modal (in Picking/Packing)
- Input: Invoice number (auto-filled)
- Textarea: Return reason
- Dropdown: Common reason templates
- Button: Confirm Return

### 3. Notification Toast
- Show when invoice returned (SSE event)
- Display: invoice_no, `sent_by`, `returned_from_section`, `review_reason`
- Action: View Invoice button

---

## 🔗 Related Endpoints

```
GET  /api/sales/invoices/           - All invoices (general list)
GET  /api/sales/billing/invoices/   - Billing-specific (user filtered)
POST /api/sales/billing/return/     - Return to billing
GET  /api/sales/invoices/{id}/      - Invoice detail
POST /api/sales/import/invoice/     - Create new invoice
```

---

## 💡 Tips

1. **Always validate invoice_no** before showing return button
2. **Use SSE for real-time updates** to keep dashboard fresh
3. **Pre-populate reason templates** to save time
4. **Show audit trail** - who returned, when, why
5. **Highlight returned invoices** with distinct color/badge
6. **Add confirmation dialog** before returning
7. **Log return reasons** for analytics

---

## 📚 Full Documentation

See [docs/api/billing.md](docs/api/billing.md) for complete API documentation.
See [BILLING_IMPLEMENTATION.md](BILLING_IMPLEMENTATION.md) for implementation details.
