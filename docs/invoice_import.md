# Invoice Import Behavior

Endpoint: `POST /api/sales/import/invoice/` (handled by `ImportInvoiceView`)

## Authentication
- API Key (via `X-API-KEY` header) OR
- Bearer Token (authenticated user)

## Behavior

### Creating New Invoices
If an invoice with the provided `invoice_no` does not exist:
- Creates a new `Invoice` record with status `INVOICED` and billing_status `BILLED`
- Creates associated `InvoiceItem` rows
- Sets `created_user` to the authenticated user (if available)
- Sets `created_by` string field (if provided)
- Emits SSE event to the `invoices` channel for live updates

### Updating Existing Invoices
If an invoice with the provided `invoice_no` already exists:
- **Customer**: Upserted using `update_or_create` by `code` field
- **Salesman**: Created or retrieved using `get_or_create` by `name`
- **Invoice Fields Updated**:
  - `invoice_date`
  - `salesman` (ForeignKey)
  - `customer` (ForeignKey)
  - `created_by` (string identifier)
  - `priority` (LOW, MEDIUM, HIGH)
  - `Total` (optional manual total amount)
  - `temp_name` (optional temporary name)
  - `remarks` (optional)
  - `created_user` (ForeignKey to User, if authenticated)
- **Items**: All existing `InvoiceItem` rows are **deleted** and replaced with incoming items (full replace strategy)
- **Transaction**: Entire operation wrapped in database transaction for consistency
- **SSE Event**: Update event emitted to `invoices` channel

## Request Format

```json
{
  "invoice_no": "INV-TEST-2026-001",
  "invoice_date": "2026-01-23",
  "salesman": "Ahmed Khan",
  "created_by": "admin_user",
  "priority": "HIGH",
  "Total": 8725.00,
  "temp_name": "Downtown Location",
  "remarks": "Test invoice - Rush order for pharmacy chain",
  "customer": {
    "code": "CUST-PH-2026-001",
    "name": "MediPlus Pharmacy",
    "area": "Gulberg",
    "address1": "Plot 45, Main Boulevard",
    "address2": "Near City Hospital",
    "phone1": "+92-300-1234567",
    "phone2": "+92-42-35123456",
    "email": "orders@mediplus.pk"
  },
  "items": [
    {
      "name": "Panadol Extra Tablets",
      "item_code": "MED-PAN-001",
      "barcode": "8964000123456",
      "quantity": 100,
      "mrp": 45.50,
      "company_name": "GSK Pakistan",
      "packing": "Strip of 10 tablets",
      "shelf_location": "A-12-03",
      "batch_no": "BATCH-20260115",
      "expiry_date": "2027-12-31",
      "remarks": "Keep in cool dry place"
    },
    {
      "name": "Augmentin 625mg",
      "item_code": "MED-AUG-625",
      "barcode": "8964000789012",
      "quantity": 50,
      "mrp": 125.00,
      "company_name": "GSK Pakistan",
      "packing": "Strip of 6 tablets",
      "shelf_location": "B-08-15",
      "batch_no": "BATCH-20260110",
      "expiry_date": "2027-06-30",
      "remarks": "Prescription required"
    },
    {
      "name": "Brufen 400mg Tablets",
      "item_code": "MED-BRU-400",
      "barcode": "8964000345678",
      "quantity": 75,
      "mrp": 38.00,
      "company_name": "Abbott Laboratories",
      "packing": "Strip of 10 tablets",
      "shelf_location": "A-15-07",
      "batch_no": "BATCH-20260118",
      "expiry_date": "2028-01-31",
      "remarks": "Store below 25°C"
    }
  ]
}
```

**Postman Testing Tips:**
- Set method to `POST`
- URL: `http://localhost:8000/api/sales/import/invoice/`
- Headers: 
  - `Content-Type: application/json`
  - `X-API-KEY: your_api_key_here` (or use Bearer token)
- Body: Select `raw` and `JSON`, then paste the above JSON
- Change `invoice_no` each time you test to create new invoices

## Field Details

### Invoice Fields
- `invoice_no` (required): Unique invoice identifier
- `invoice_date` (required): Date of invoice
- `salesman` (required): Salesman name (string)
- `created_by` (optional): String identifier of person who created invoice
- `priority` (optional): LOW, MEDIUM (default), or HIGH
- `Total` (optional): Manual total amount (decimal) - Note: Field name is capitalized
- `temp_name` (optional): Temporary name to display when customer address/area is not available
- `remarks` (optional): Additional notes
- `created_at` (auto-generated): Timestamp when invoice was created in the system (ISO 8601 format)

### Customer Fields
- `code` (required): Unique customer code
- `name` (required): Customer name
- `area` (optional): Customer area/location
- `address1`, `address2` (optional): Address lines
- `phone1`, `phone2` (optional): Contact numbers
- `email` (optional): Email address

### Item Fields
- `name` (required): Product/item name
- `item_code` (required): Item code identifier
- `barcode` (optional): Item barcode
- `quantity` (required): Quantity ordered
- `mrp` (required): Maximum Retail Price
- `company_name` (optional): Manufacturer/company name
- `packing` (optional): Packing details (e.g., "Box of 10")
- `shelf_location` (optional): Warehouse shelf location
- `batch_no` (optional): Batch/lot number
- `expiry_date` (optional): Expiration date (YYYY-MM-DD)
- `remarks` (optional): Item-specific notes

## Response Format

### Success (201 Created - New Invoice)
```json
{
  "success": true,
  "message": "Invoice imported successfully",
  "data": {
    "id": 1,
    "invoice_no": "INV-TEST-2026-001",
    "total_amount": 8725.0,
    "priority": "HIGH",
    "status": "INVOICED",
    "billing_status": "BILLED",
    "created_at": "2026-01-23T10:30:45.123456Z"
  }
}
```

### Success (200 OK - Updated Invoice)
```json
{
  "success": true,
  "message": "Invoice INV-001 updated successfully",
  "data": {
    "invoice_no": "INV-001",
    "status": "INVOICED",
    "billing_status": "BILLED",
    "created_at": "2026-01-20T08:15:30.987654Z"
  }
}
```
**Note:** When updating an existing invoice, the `created_at` timestamp is preserved from the original creation time and is not modified.

### Error (400 Bad Request)
```json
{
  "success": false,
  "errors": {
    "invoice_date": ["This field is required."],
    "items": ["At least one item is required."]
  }
}
```

### Error (500 Internal Server Error)
```json
{
  "success": false,
  "message": "An unexpected error occurred while processing the invoice."
}
```

## Important Notes

### Transaction Safety
- All database operations (invoice, customer, salesman, items) are wrapped in a single transaction
- If any operation fails, all changes are rolled back to maintain data integrity

### Item Replacement Strategy
- **Full Replace**: All existing items are deleted and replaced with the new item list
- This ensures the invoice always matches the imported data exactly
- No partial updates or merging of items occurs

### Status Preservation
- The invoice `status` and `billing_status` fields are **NOT** modified during import/update
- If an invoice is in `PICKING`, `PACKING`, or `DELIVERED` status, it remains in that status
- Only use the **Update Invoice API** (`PATCH /api/sales/update/invoice/`) to modify invoices under review

### SSE Events
- Both create and update operations emit real-time events to the `invoices` channel
- Frontend applications can subscribe to `/api/sales/sse/invoices/` for live updates

### Authentication

### Timestamps
- `created_at`: Automatically set when invoice is first created (uses `auto_now_add=True`)
- This timestamp is preserved during updates and represents the original creation time
- Returned in ISO 8601 format (e.g., `2026-01-23T10:30:45.123456Z`)
- Available in all invoice-related endpoints:
  - `GET /api/sales/invoices/` (Invoice List)
  - `GET /api/sales/invoices/{id}/` (Invoice Detail)
  - `POST /api/sales/import/invoice/` (Import/Create)
  - Picking, Packing, and Delivery session responses
  - History endpoints
- API key authentication allows external systems to import invoices
- Bearer token authentication allows web application users to import invoices
- The `created_user` field is automatically set when using Bearer token authentication

## Recommendations

### For Partial Item Updates
If you need to update specific items without replacing all items:
- Use the dedicated **Update Invoice API** at `PATCH /api/sales/update/invoice/`
- That endpoint supports item-level updates by matching on `barcode` or `item_code`

### For Status-Aware Updates
The import endpoint does NOT check invoice status before updating. If you need to:
- Prevent updates when invoice is being processed (PICKING/PACKING/DISPATCHED)
- Only allow updates for invoices in REVIEW status
- Use the dedicated **Update Invoice API** which has these validations built-in

### For Production Use
Consider implementing:
- Rate limiting on the import endpoint
- Logging of all import operations for audit trail
- Validation of invoice totals against item quantities × MRP
- Duplicate detection within time windows

## Request Format

```json

{
  "invoice_no": "INV-TEST-2026-0014",
  "invoice_date": "2026-01-29",
  "salesman": "Ahmed Khan",
  "created_by": "admin_user",
  "priority": "HIGH",
  "Total": 8725.00,
  "temp_name": "RAMANKUTTY",
  "remarks": "Test invoice with temp_name field",
  "customer": {
    "code": "CUST-PH-2026-003",
    "name": "HealthCare Pharmacy",
    "area": "",
    "address1": "",
    "address2": "",
    "phone1": "+92-300-9876543",
    "phone2": "",
    "email": "contact@healthcare.pk"
  },
  "items": [
    {
      "name": "Panadol Extra Tablets",
      "item_code": "MED-PAN-001",
      "barcode": "8964000123456",
      "quantity": 100,
      "mrp": 45.50,
      "company_name": "GSK Pakistan",
      "packing": "Strip of 10 tablets",
      "shelf_location": "A-12-03",
      "batch_no": "BATCH-20260129",
      "expiry_date": "2027-12-31",
      "remarks": "Keep in cool dry place"
    },
    {
      "name": "Augmentin 625mg",
      "item_code": "MED-AUG-625",
      "barcode": "8964000789012",
      "quantity": 50,
      "mrp": 125.00,
      "company_name": "GSK Pakistan",
      "packing": "Strip of 6 tablets",
      "shelf_location": "B-08-15",
      "batch_no": "BATCH-20260125",
      "expiry_date": "2027-06-30",
      "remarks": "Prescription required"
    }
  ]
}
```