# Delivery Workflow Complete Guide

## Overview
The delivery system supports **3 main delivery types** with different workflows:

---

## 🎯 Delivery Types

### 1. **Counter Pickup (DIRECT)**
Customer picks up directly from the counter - **completes immediately**.

#### Sub-Types:
- **Direct Patient**: Individual customer pickup
- **Direct Company**: Company representative pickup

#### Workflow:
```
PACKED Invoice → Dispatch Page → Select "Counter Pickup" 
  → Choose Sub-type (Patient/Company)
  → Fill popup form with customer details
  → Submit → ✅ DELIVERED (No further steps)
```

#### Required Fields:

**For Direct Patient:**
- Username/ID *
- Person Name *
- Phone Number * (10 digits)
- Notes (optional)

**For Direct Company:**
- Username/ID *
- Person Name *
- Phone Number * (10 digits)
- Company Name *
- Company ID *
- Notes (optional)

#### Backend Behavior:
- Creates DeliverySession with `delivery_type='DIRECT'`
- Sets `counter_sub_mode='patient'` or `'company'`
- Immediately sets:
  - `delivery_status='DELIVERED'`
  - `start_time=now()`
  - `end_time=now()`
  - Invoice `status='DELIVERED'`

---

### 2. **Courier Delivery**
Third-party courier service delivery - **goes to Consider List**.

#### Workflow:
```
PACKED Invoice → Dispatch Page → Select "Courier Delivery"
  → Select Courier from dropdown
  → Submit → Courier Consider List
  → Upload courier slip → ✅ DELIVERED
```

#### Required Fields:
- Courier selection from active couriers list

#### Backend Behavior:
- Creates DeliverySession with `delivery_type='COURIER'`
- Sets `delivery_status='TO_CONSIDER'`
- Invoice remains `status='PACKED'` (not dispatched yet)
- Appears in **Courier Delivery Consider List** (`/delivery/courier-deliveries`)

#### Consider List Actions:
1. View courier assignments
2. Upload courier slip/screenshot
3. On slip upload → Marked as DELIVERED

---

### 3. **Company Delivery (INTERNAL)**
Internal staff member delivery - **goes to Consider List**.

#### Workflow:
```
PACKED Invoice → Dispatch Page → Select "Company Delivery"
  → Enter staff email and name
  → Submit → Company Delivery Consider List
  → Staff completes delivery → ✅ DELIVERED
```

#### Required Fields:
- Staff Email *
- Staff Name *

#### Backend Behavior:
- Creates DeliverySession with `delivery_type='INTERNAL'`
- Sets `delivery_status='TO_CONSIDER'`
- Invoice remains `status='PACKED'`
- Appears in **Company Delivery Consider List** (`/delivery/company-deliveries`)

#### Consider List Actions:
1. View staff assignments
2. Staff member completes delivery from their dashboard
3. On completion → Marked as DELIVERED

---

## 📋 Status Flow

### Counter Pickup:
```
PACKED → DELIVERED (instant)
```

### Courier Delivery:
```
PACKED → TO_CONSIDER → IN_TRANSIT (on slip upload) → DELIVERED
```

### Company Delivery:
```
PACKED → TO_CONSIDER → IN_TRANSIT (when staff accepts) → DELIVERED
```

---

## 🗂️ Pages & Routes

### Frontend Pages:

1. **Dispatch Page** (`/delivery/dispatch`)
   - Shows all PACKED invoices
   - DeliveryModal opens on "Start Delivery" button
   - Filters out invoices already in delivery sessions

2. **Courier Delivery Page** (`/delivery/courier-deliveries`)
   - Shows `delivery_type=COURIER` && `status=TO_CONSIDER`
   - Upload courier slip functionality
   - View invoice details

3. **Company Delivery Page** (`/delivery/company-deliveries`)
   - Shows `delivery_type=INTERNAL` && `status=TO_CONSIDER`
   - View assigned staff member
   - Track delivery progress

4. **My Delivery List** (`/ops/delivery/my-deliveries`)
   - For DELIVERY role users
   - Shows their assigned deliveries
   - Complete delivery action

---

## 🔌 Backend API Endpoints

### Start Delivery
```http
POST /api/sales/delivery/start/
```

**Request Body (Counter Pickup - Patient):**
```json
{
  "invoice_no": "INV-001",
  "delivery_type": "DIRECT",
  "counter_sub_mode": "patient",
  "pickup_person_username": "john123",
  "pickup_person_name": "John Doe",
  "pickup_person_phone": "9876543210",
  "notes": "Optional notes"
}
```

**Request Body (Counter Pickup - Company):**
```json
{
  "invoice_no": "INV-001",
  "delivery_type": "DIRECT",
  "counter_sub_mode": "company",
  "pickup_person_username": "rep001",
  "pickup_person_name": "Jane Smith",
  "pickup_person_phone": "9876543210",
  "pickup_company_name": "ABC Corp",
  "pickup_company_id": "COMP123",
  "notes": "Optional notes"
}
```

**Request Body (Courier):**
```json
{
  "invoice_no": "INV-001",
  "delivery_type": "COURIER",
  "courier_id": "COU-001"
}
```

**Request Body (Company Delivery):**
```json
{
  "invoice_no": "INV-001",
  "delivery_type": "INTERNAL",
  "user_email": "staff@company.com",
  "user_name": "Staff Member"
}
```

### Get Consider List
```http
GET /api/sales/delivery/consider-list/?delivery_type=COURIER
GET /api/sales/delivery/consider-list/?delivery_type=INTERNAL
```

**Query Parameters:**
- `delivery_type`: COURIER or INTERNAL
- `search`: Search by invoice number or customer name
- `page`: Page number
- `page_size`: Items per page

### Upload Courier Slip
```http
POST /api/sales/delivery/upload-slip/
Content-Type: multipart/form-data
```

**Form Data:**
```
invoice_no: INV-001
courier_slip: <file>
delivery_type: COURIER
```

### Assign Staff (from Consider List)
```http
POST /api/sales/delivery/assign/
```

**Request Body:**
```json
{
  "invoice_no": "INV-001",
  "user_email": "staff@company.com",
  "delivery_type": "INTERNAL"
}
```

---

## 🎨 UI Components

### DeliveryModal Component
Located: `src/features/delivery/components/DeliveryModal.jsx`

**Props:**
- `isOpen`: Boolean - Modal visibility
- `onClose`: Function - Close handler
- `onConfirm`: Function - Submit handler
- `invoice`: Object - Invoice data
- `submitting`: Boolean - Loading state

**Steps:**
1. Select delivery type (3 options)
2. Counter Pickup → Select sub-type (2 options)
3. Show appropriate form based on selection
4. Validate and submit

---

## 📊 Database Schema

### DeliverySession Model Fields

**Common Fields:**
- `invoice` (OneToOne) - Related invoice
- `delivery_type` (CharField) - DIRECT, COURIER, INTERNAL
- `assigned_to` (FK) - User who initiated
- `delivered_by` (FK) - User who completed
- `start_time` (DateTime)
- `end_time` (DateTime)
- `delivery_status` (CharField) - PENDING, TO_CONSIDER, IN_TRANSIT, DELIVERED, CANCELLED
- `notes` (TextField)

**Counter Pickup Specific:**
- `counter_sub_mode` - 'patient' or 'company'
- `pickup_person_username`
- `pickup_person_name`
- `pickup_person_phone`
- `pickup_company_name` (for company pickup)
- `pickup_company_id` (for company pickup)

**Courier Specific:**
- `courier_name` (CharField)
- `tracking_no` (CharField)
- `courier_slip` (FileField)

**Location Tracking:**
- `delivery_latitude`
- `delivery_longitude`
- `delivery_location_address`
- `delivery_location_accuracy`

---

## ✅ Validation Rules

### Counter Pickup Validation:
1. Invoice must be in PACKED status
2. No existing delivery session
3. `counter_sub_mode` required ('patient' or 'company')
4. Username, name, phone required for both sub-types
5. Phone must be 10 digits
6. Company name and ID required for 'company' sub-type

### Courier Delivery Validation:
1. Invoice must be in PACKED status
2. No existing delivery session
3. Valid courier_id required
4. Courier must exist and be ACTIVE

### Company Delivery Validation:
1. Invoice must be in PACKED status
2. No existing delivery session
3. Valid user email required
4. User must exist in system

---

## 🔐 Permissions

### Who Can Start Delivery:
- ADMIN
- SUPERADMIN
- BILLER (from billing section)

### Who Can Complete Delivery:
- **Counter Pickup**: Same person who initiated (auto-completed)
- **Courier Delivery**: Staff who uploads courier slip
- **Company Delivery**: Assigned DELIVERY role staff member

---

## 📱 Real-Time Updates (SSE)

All delivery actions emit SSE events on the **INVOICE_CHANNEL** to update:
- Dispatch page
- Consider lists (Courier & Company)
- My Delivery page
- Invoice history

Event Channel: `/api/sales/events/invoices/`

---

## 🧪 Testing Checklist

### Counter Pickup - Direct Patient:
- [ ] Can select Counter Pickup from dispatch page
- [ ] Can select Direct Patient sub-type
- [ ] Form shows required fields: username, name, phone
- [ ] 10-digit phone validation works
- [ ] On submit, invoice marked as DELIVERED
- [ ] Does NOT appear in any consider list
- [ ] Appears in delivery history with counter pickup details

### Counter Pickup - Direct Company:
- [ ] Can select Counter Pickup from dispatch page
- [ ] Can select Direct Company sub-type
- [ ] Form shows all fields: username, name, phone, company name, company ID
- [ ] All validations work
- [ ] On submit, invoice marked as DELIVERED
- [ ] Company details saved correctly

### Courier Delivery:
- [ ] Can select Courier Delivery
- [ ] Courier dropdown loads active couriers
- [ ] Can search and select courier
- [ ] On submit, appears in Courier Consider List
- [ ] Invoice status remains PACKED
- [ ] Can upload courier slip from consider list
- [ ] On slip upload, marked as DELIVERED
- [ ] Appears in delivery history

### Company Delivery:
- [ ] Can select Company Delivery
- [ ] Can enter staff email and name
- [ ] On submit, appears in Company Consider List
- [ ] Invoice status remains PACKED
- [ ] Assigned staff can see in their dashboard
- [ ] Staff can complete delivery
- [ ] On completion, marked as DELIVERED

---

## 🚨 Common Issues & Solutions

### Issue: Counter pickup not completing
**Solution:** Check that `delivery_type='DIRECT'` and both `start_time` and `end_time` are set to `timezone.now()`

### Issue: Courier/Company deliveries not showing in consider list
**Solution:** Verify `delivery_status='TO_CONSIDER'` is set correctly

### Issue: Duplicate delivery session error
**Solution:** Check if invoice already has a delivery session before creating new one

### Issue: Courier slip upload fails
**Solution:** Ensure file is image (JPG, PNG, GIF) or PDF, and under 5MB

---

## 📞 Support

For issues or questions about the delivery workflow:
1. Check this documentation
2. Review backend logs: `alfa-erp-backend/logs/`
3. Check frontend console for errors
4. Verify database constraints and relationships

---

**Last Updated:** January 24, 2026
**Version:** 1.0
**Status:** ✅ Fully Implemented & Production Ready
