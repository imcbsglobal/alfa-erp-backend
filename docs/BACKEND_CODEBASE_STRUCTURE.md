# Backend Codebase Structure - Items, Invoices, and API Endpoints

## 1. MODEL DEFINITIONS

### 1.1 Item Model
**File:** [apps/sales/models.py](apps/sales/models.py#L166-L185)

```python
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255, help_text="Item/product name")
    item_code = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, blank=True, null=True, help_text="Item barcode")
    quantity = models.IntegerField()
    mrp = models.FloatField()
    company_name = models.CharField(max_length=100, blank=True)
    packing = models.CharField(max_length=50, blank=True)
    shelf_location = models.CharField(max_length=50, blank=True)
    batch_no = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.invoice.invoice_no}"
```

**Key Fields:**
- `quantity` (IntegerField): Ordered quantity
- `mrp` (FloatField): Maximum Retail Price
- Single related_name in Invoice: `items`

---

### 1.2 Invoice Model
**File:** [apps/sales/models.py](apps/sales/models.py#L31-L106)

```python
class Invoice(models.Model):
    invoice_no = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateField()
    salesman = models.ForeignKey(Salesman, on_delete=models.SET_NULL, null=True)
    created_by = models.CharField(max_length=150, blank=True, null=True)
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    temp_name = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    Total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ("INVOICED", "Invoiced"),
            ("PICKING", "Picking"),
            ("PICKED", "Picked"),
            ("PACKING", "Packing"),
            ("BOXING", "Boxing"),
            ("PACKED", "Packed"),
            ("DISPATCHED", "Dispatched"),
            ("DELIVERED", "Delivered"),
            ("REVIEW", "Under Review"),
        ],
        default="INVOICED"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")],
        default="MEDIUM"
    )
    
    billing_status = models.CharField(
        max_length=20,
        choices=[
            ("BILLED", "Billed"),
            ("REVIEW", "Under Review"),
            ("RE_INVOICED", "Re-invoiced"),
        ],
        default="BILLED"
    )
    
    is_hold = models.BooleanField(default=True)
    self_boxing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Key Fields:**
- `Total` (DecimalField): Invoice total amount (max_digits=10, decimal_places=2)
- `status`: Workflow status (INVOICED → DELIVERED)
- `billing_status`: Separate billing tracking
- Related ForeignKeys: `customer` (Customer), `salesman` (Salesman), `created_user` (User)

**Related Models via ForeignKey:**
- `InvoiceItem` (reverse: `items`)
- `InvoiceReturn` (reverse: `invoice_returns`)
- `PickingSession` (OneToOne)
- `PackingSession` (OneToOne)
- `DeliverySession` (OneToOne)
- `Box` (reverse: `boxes`)
- `PackingTray` (reverse: `packing_trays`)

---

### 1.3 Invoice-Item Relationship

**Direct Relationship:**
```
Invoice (1) --< InvoiceItem (Many)
  via: InvoiceItem.invoice = ForeignKey(Invoice)
  reverse: Invoice.items = related_name
```

**Item Structure:**
- Items are stored as `InvoiceItem` instances linked to an Invoice
- Each item has: name, code, quantity, mrp, company, packing, location, batch, expiry
- Accessed via: `invoice.items.all()`

---

### 1.4 Additional Related Models

**Customer Model:**
```python
class Customer(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    area = models.CharField(max_length=150, blank=True)
    address1/2/3 = models.TextField(blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    phone1/2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
```

**Salesman Model:**
```python
class Salesman(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, null=True, blank=True)
```

---

## 2. SERIALIZER IMPLEMENTATIONS

### 2.1 Item Serializer
**File:** [apps/sales/serializers.py](apps/sales/serializers.py#L41-L48)

```python
class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items"""
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'name', 'item_code', 'barcode', 'quantity', 'mrp', 
            'company_name', 'packing', 'shelf_location', 'remarks', 
            'batch_no', 'expiry_date'
        ]
```

**Import Serializer (for CSV/Excel Import):**
```python
class ItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    item_code = serializers.CharField()
    quantity = serializers.IntegerField()
    mrp = serializers.FloatField()
    shelf_location = serializers.CharField(max_length=50, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    batch_no = serializers.CharField(required=False, allow_blank=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    company_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    packing = serializers.CharField(max_length=100, required=False, allow_blank=True)
    barcode = serializers.CharField(required=False, allow_blank=True)
```

---

### 2.2 Invoice Serializers
**File:** [apps/sales/serializers.py](apps/sales/serializers.py#L64-L160)

**InvoiceListSerializer** (Main Serializer):
```python
class InvoiceListSerializer(serializers.ModelSerializer):
    customer = CustomerReadSerializer(read_only=True)
    salesman = SalesmanReadSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    Total = serializers.DecimalField(max_digits=10, decimal_places=2)
    return_info = serializers.SerializerMethodField()
    picker_info = serializers.SerializerMethodField()
    packer_info = serializers.SerializerMethodField()
    delivery_info = serializers.SerializerMethodField()
    current_handler = serializers.SerializerMethodField()
    tray_codes = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_no', 'invoice_date', 'customer', 'status', 'priority', 
            'salesman', 'created_by', 'items', 'Total', 'temp_name', 'remarks', 
            'created_at', 'billing_status', 'return_info', 'picker_info', 
            'packer_info', 'delivery_info', 'current_handler', 'tray_codes'
        ]
```

**Sub-Serializers:**
- `CustomerReadSerializer`: Customer details (code, name, area, addresses, contacts)
- `SalesmanReadSerializer`: Salesman info (id, name, phone)
- `InvoiceReturnSerializer`: Return/review information
- `InvoiceItemSerializer`: Item details (nested in items array)

**Key SerializerMethodField Methods:**
- `get_picker_info()`: Picking session details
- `get_packer_info()`: Packing session details
- `get_delivery_info()`: Delivery session details
- `get_return_info()`: Invoice return/review info
- `get_current_handler()`: Current person handling based on status
- `get_tray_codes()`: Associated tray codes

---

### 2.3 Import Serializer
**File:** [apps/sales/serializers.py](apps/sales/serializers.py#L173-L213)

```python
class InvoiceImportSerializer(serializers.Serializer):
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    salesman = serializers.CharField()
    created_by = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(
        choices=[('LOW','Low'),('MEDIUM','Medium'),('HIGH','High')], 
        required=False, 
        default='MEDIUM'
    )
    Total = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    temp_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    customer = CustomerSerializer()
    items = ItemSerializer(many=True)

    def create(self, validated_data):
        # Creates Invoice + InvoiceItems from import data
```

---

## 3. API ENDPOINTS

### 3.1 Invoice Management
**File Paths:** [apps/sales/urls.py](apps/sales/urls.py) | [apps/sales/views.py](apps/sales/views.py)

| Endpoint | Method | View Class | Purpose |
|----------|--------|-----------|---------|
| `/api/sales/invoices/` | GET | `InvoiceListView` | List all invoices with filters |
| `/api/sales/invoices/<id>/` | GET | `InvoiceDetailView` | Get single invoice details |
| `/api/sales/import/invoice/` | POST | `ImportInvoiceView` | Import invoices from CSV/Excel |
| `/api/sales/update/invoice/` | PATCH/PUT | `UpdateInvoiceView` | Update invoice |

**Query Parameters for `/api/sales/invoices/`:**
- `status`: Filter by status (INVOICED, PICKING, PICKED, PACKING, PACKED, DISPATCHED, DELIVERED, REVIEW)
- `user`: Filter by created_user ID
- `created_by`: Filter by created_by string
- `worker`: Filter by worker email (picker/packer/delivery person)
- `priority`: Filter by priority (LOW, MEDIUM, HIGH)
- `delivery_status`: Filter by delivery status
- `page`: Page number (pagination)
- `page_size`: Items per page (default 20, max 100,000)

**Example Queries:**
```
GET /api/sales/invoices/?status=INVOICED
GET /api/sales/invoices/?status=PICKING&status=PACKING
GET /api/sales/invoices/?worker=zain@gmail.com
GET /api/sales/invoices/?status=DELIVERED&start_date=2026-02-01
```

---

### 3.2 Picking Workflow
| Endpoint | Method | View Class | Purpose |
|----------|--------|-----------|---------|
| `/api/sales/picking/start/` | POST | `StartPickingView` | Start picking session |
| `/api/sales/picking/active/` | GET | `MyActivePickingView` | Get user's active picking |
| `/api/sales/picking/complete/` | POST | `CompletePickingView` | Complete picking |
| `/api/sales/picking/history/` | GET | `PickingHistoryView` | Picking session history |
| `/api/sales/picking/bulk-start/` | POST | `BulkPickingStartView` | Start multiple pickings |
| `/api/sales/picking/bulk-complete/` | POST | `BulkPickingCompleteView` | Complete multiple pickings |

---

### 3.3 Packing Workflow
| Endpoint | Method | View Class | Purpose |
|----------|--------|-----------|---------|
| `/api/sales/packing/start/` | POST | `StartPackingView` | Start packing session |
| `/api/sales/packing/active/` | GET | `MyActivePackingView` | Get user's active packing |
| `/api/sales/packing/history/` | GET | `PackingHistoryView` | Packing history |
| `/api/sales/packing/my-checking/` | GET | `GetMyCheckingBillsView` | Bills for checking |
| `/api/sales/packing/bill/<invoice_no>/` | GET | `GetBillDetailsView` | Bill details |
| `/api/sales/packing/start-checking/` | POST | `StartCheckingView` | Start checking |
| `/api/sales/packing/search-trays/` | GET | `SearchTrayView` | Search trays |
| `/api/sales/packing/tray-bill/<invoice_no>/` | GET | `GetTrayBillDetailsView` | Tray bill details |
| `/api/sales/packing/save-tray-draft/` | POST | `SaveTrayDraftView` | Save tray draft |
| `/api/sales/packing/complete-tray-packing/` | POST | `CompletePackingWithTraysView` | Complete tray packing |
| `/api/sales/packing/boxing-invoices/` | GET | `GetBoxingInvoicesView` | Invoices for boxing |
| `/api/sales/packing/boxing-data/<invoice_no>/` | GET | `GetBoxingDataView` | Boxing data |
| `/api/sales/packing/complete-boxing/` | POST | `CompleteBoxingView` | Complete boxing |

---

### 3.4 Delivery Workflow
| Endpoint | Method | View Class | Purpose |
|----------|--------|-----------|---------|
| `/api/sales/delivery/start/` | POST | `StartDeliveryView` | Start delivery |
| `/api/sales/delivery/complete/` | POST | `CompleteDeliveryView` | Complete delivery |
| `/api/sales/delivery/history/` | GET | `DeliveryHistoryView` | Delivery history |
| `/api/sales/delivery/consider-list/` | GET | `DeliveryConsiderListView` | Deliveries to consider |
| `/api/sales/delivery/eligible-staff/` | GET | `EligibleDeliveryStaffView` | Available delivery staff |
| `/api/sales/delivery/assign/` | POST | `AssignDeliveryStaffView` | Assign delivery staff |
| `/api/sales/delivery/upload-slip/` | POST | `UploadCourierSlipView` | Upload courier slip |
| `/api/sales/delivery/update-courier/` | PATCH | `UpdateDeliveryCourierView` | Update courier service |
| `/api/sales/delivery/audit-logs/` | GET | `GetCourierAuditLogsView` | Courier change logs |

---

### 3.5 Billing Endpoints
| Endpoint | Method | View Class | Purpose |
|----------|--------|-----------|---------|
| `/api/sales/billing/history/` | GET | `BillingHistoryView` | Billing history |
| `/api/sales/billing/invoices/` | GET | `BillingInvoicesView` | Invoices for billing |
| `/api/sales/billing/return/` | POST | `ReturnToBillingView` | Return for review |
| `/api/sales/billing/user-summary/` | GET | `BillingUserSummaryView` | Summary by salesman |

---

### 3.6 Report Endpoints
**File:** [apps/sales/views.py](apps/sales/views.py#L3266-L3500)

#### Invoice Report
**Endpoint:** `GET /api/sales/invoice-report/`  
**View Class:** `InvoiceReportView`

```python
class InvoiceReportView(generics.ListAPIView):
    """List invoices for reporting with filters and pagination"""
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InvoiceListPagination
```

**Query Parameters:**
- `search`: Search by invoice_no or customer name
- `status`: Filter by status
- `start_date`: Filter by created date (YYYY-MM-DD)
- `end_date`: Filter by created date (YYYY-MM-DD)
- `customer_name`: Filter by customer name
- `created_by`: Filter by salesman name
- `page_size`: Items per page

**Example:**
```
GET /api/sales/invoice-report/?start_date=2026-02-09&status=INVOICED&page_size=50
```

---

#### Invoice Report Export
**Endpoint:** `GET /api/sales/invoice-report/export/`  
**View Class:** `InvoiceReportExportView`

Returns lightweight export data (optimized for Excel):
```json
{
  "success": true,
  "count": 25,
  "data": [
    {
      "invoice_no": "INV-001",
      "created_by": "Salesman1",
      "created_at": "2026-02-09T10:30:00",
      "customer_name": "John Doe",
      "area": "North District",
      "amount": 1500.00,
      "status": "INVOICED"
    }
  ]
}
```

---

#### Billing User Summary
**Endpoint:** `GET /api/sales/billing/user-summary/`  
**View Class:** `BillingUserSummaryView`

```python
def get(self, request):
    # Aggregates data per salesman
    # Returns: salesman_id, salesman_name, bill_count, total_amount, 
    #          first_invoice_date, last_invoice_date
```

**Query Parameters:**
- `start_date`: Filter from date
- `end_date`: Filter to date
- `billing_status`: Default 'BILLED'

**Response:**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "salesman_id": 1,
      "salesman_name": "Salesman1",
      "bill_count": 45,
      "total_amount": 67500.00,
      "first_invoice_date": "2026-02-01T08:15:00",
      "last_invoice_date": "2026-02-16T16:45:00"
    }
  ]
}
```

---

### 3.7 Admin Endpoints
| Endpoint | Method | View Class | Purpose |
|----------|--------|-----------|---------|
| `/api/sales/admin/complete-workflow/` | POST | `AdminCompleteWorkflowView` | Complete entire workflow |
| `/api/sales/admin/bulk-status-update/` | POST | `AdminBulkStatusUpdateView` | Bulk status update |
| `/api/sales/admin/bulk-status-history/` | GET | `AdminBulkStatusHistoryView` | Bulk update history |

---

## 4. PAGINATION

**Default Pagination Class:** `InvoiceListPagination`
```python
class InvoiceListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100000
```

---

## 5. FILE STRUCTURE SUMMARY

```
alfa-erp-backend/
├── apps/
│   ├── sales/
│   │   ├── models.py              ← Invoice, InvoiceItem, Salesman, Customer, etc.
│   │   ├── serializers.py         ← InvoiceListSerializer, InvoiceItemSerializer, etc.
│   │   ├── views.py               ← API views and report endpoints
│   │   ├── urls.py                ← URL routing
│   │   ├── update_serializers.py  ← Update serializers
│   │   └── admin_views.py         ← Admin endpoints
│   ├── analytics/
│   │   ├── models.py              ← DailyHoldSnapshot
│   │   └── views.py               ← Dashboard and reporting views
│   ├── accounts/
│   │   └── models.py              ← User, Courier, Tray models
│   └── common/
│       └── serializers.py         ← Common serializers (TraySerializer)
└── config/
    └── urls.py                    ← Main URL configuration
```

---

## 6. KEY DATA FLOW EXAMPLES

### Creating an Invoice with Items

**Input (InvoiceImportSerializer):**
```json
{
  "invoice_no": "INV-001",
  "invoice_date": "2026-02-09",
  "salesman": "John Salesman",
  "customer": {
    "code": "CUST001",
    "name": "Customer Name",
    "area": "Area1",
    "phone1": "9876543210"
  },
  "items": [
    {
      "name": "Product A",
      "item_code": "PROD-A",
      "quantity": 10,
      "mrp": 150.00,
      "shelf_location": "A1-B2"
    },
    {
      "name": "Product B",
      "item_code": "PROD-B",
      "quantity": 5,
      "mrp": 200.00,
      "shelf_location": "C3-D4"
    }
  ],
  "Total": 2500.00
}
```

**Database Result:**
- Creates 1 Invoice record
- Creates 2 InvoiceItem records linked via ForeignKey
- Automatically creates/updates Customer and Salesman

**Retrieval (InvoiceListSerializer):**
```json
{
  "id": 1,
  "invoice_no": "INV-001",
  "customer": {
    "code": "CUST001",
    "name": "Customer Name"
  },
  "items": [
    {
      "id": 1,
      "name": "Product A",
      "quantity": 10,
      "mrp": 150.00
    },
    {
      "id": 2,
      "name": "Product B",
      "quantity": 5,
      "mrp": 200.00
    }
  ],
  "Total": "2500.00",
  "status": "INVOICED"
}
```

---

## 7. IMPORTANT NOTES

1. **Item Storage**: Items are stored as a separate `InvoiceItem` model with ForeignKey to Invoice
2. **Quantity Fields**: `quantity` is IntegerField (not decimal)
3. **Price Fields**: `mrp` is FloatField, `Total` is DecimalField
4. **Total Field**: Decimal(max_digits=10, decimal_places=2) - stores up to 99,999,999.99
5. **Item Serialization**: Always includes nested `items` array in InvoiceListSerializer
6. **Pagination**: Supports up to 100,000 items per page
7. **Filtering**: Supports status, worker, priority, delivery_status filters
8. **Report Exports**: Optimized export endpoint with limited fields for Excel
9. **Workflow Tracking**: Separate sessions for picking, packing, delivery with status tracking

