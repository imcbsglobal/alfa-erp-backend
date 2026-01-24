# Delivery Workflow Visual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INVOICE DELIVERY WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │   PACKED     │
                            │   INVOICE    │
                            └──────┬───────┘
                                   │
                                   │ Dispatch Page
                                   │ (Biller initiates)
                                   ▼
                      ┌────────────────────────┐
                      │  SELECT DELIVERY TYPE  │
                      └────────────────────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                │                  │                  │
                ▼                  ▼                  ▼
       ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
       │ COUNTER PICKUP │  │   COURIER    │  │   COMPANY    │
       │    (DIRECT)    │  │   DELIVERY   │  │   DELIVERY   │
       └────────┬───────┘  └──────┬───────┘  └──────┬───────┘
                │                  │                  │
                │                  │                  │
     ┌──────────┴─────────┐       │                  │
     │                    │       │                  │
     ▼                    ▼       │                  │
┌─────────┐       ┌──────────┐   │                  │
│ DIRECT  │       │  DIRECT  │   │                  │
│ PATIENT │       │ COMPANY  │   │                  │
└────┬────┘       └────┬─────┘   │                  │
     │                 │          │                  │
     ▼                 ▼          ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ POPUP FORM  │  │  POPUP FORM  │  │  SELECT COURIER  │  │  ENTER STAFF     │
│             │  │              │  │                  │  │  EMAIL & NAME    │
│ • Username  │  │ • Username   │  │  • Active        │  │                  │
│ • Name      │  │ • Name       │  │    Couriers      │  │  • user_email    │
│ • Phone     │  │ • Phone      │  │    Dropdown      │  │  • user_name     │
│             │  │ • Company    │  │                  │  │                  │
│             │  │   Name       │  │  • Search        │  │                  │
│             │  │ • Company ID │  │                  │  │                  │
└─────┬───────┘  └──────┬───────┘  └────────┬─────────┘  └────────┬─────────┘
      │                 │                   │                     │
      │                 │                   │                     │
      └────────┬────────┘                   │                     │
               │                            │                     │
               ▼                            ▼                     ▼
       ┌───────────────┐          ┌──────────────────┐   ┌──────────────────┐
       │   DELIVERED   │          │  COURIER CONSIDER │   │  COMPANY CONSIDER│
       │   (INSTANT)   │          │       LIST        │   │       LIST       │
       └───────────────┘          │                   │   │                  │
               │                  │ Status:           │   │ Status:          │
               │                  │ TO_CONSIDER       │   │ TO_CONSIDER      │
               │                  └────────┬──────────┘   └────────┬─────────┘
               │                           │                       │
               │                           │                       │
               │                           ▼                       ▼
               │                  ┌──────────────────┐   ┌──────────────────┐
               │                  │  UPLOAD COURIER  │   │ STAFF ACCEPTS &  │
               │                  │      SLIP        │   │ COMPLETES        │
               │                  └────────┬─────────┘   └────────┬─────────┘
               │                           │                       │
               │                           ▼                       ▼
               │                  ┌──────────────────┐   ┌──────────────────┐
               │                  │   IN_TRANSIT     │   │   IN_TRANSIT     │
               │                  └────────┬─────────┘   └────────┬─────────┘
               │                           │                       │
               │                           ▼                       ▼
               │                  ┌──────────────────┐   ┌──────────────────┐
               │                  │    DELIVERED     │   │    DELIVERED     │
               │                  └────────┬─────────┘   └────────┬─────────┘
               │                           │                       │
               └───────────────────────────┴───────────────────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │ DELIVERY HISTORY│
                                  └─────────────────┘
```

---

## Detailed Flow Explanations

### 🟢 **Counter Pickup Flow (Instant Completion)**

```
PACKED → Dispatch Page → Counter Pickup Button
   ↓
Select Sub-Type:
   ├─ Direct Patient → Enter: Username, Name, Phone
   └─ Direct Company → Enter: Username, Name, Phone, Company Name, Company ID
   ↓
Submit → Validate (10-digit phone, all required fields)
   ↓
Backend:
   ├─ Create DeliverySession (delivery_type='DIRECT')
   ├─ Set counter_sub_mode ('patient' or 'company')
   ├─ Set start_time = now()
   ├─ Set end_time = now()
   ├─ Set delivery_status = 'DELIVERED'
   └─ Update Invoice status = 'DELIVERED'
   ↓
✅ COMPLETED (No further steps)
```

---

### 🟠 **Courier Delivery Flow (Multi-Step)**

```
PACKED → Dispatch Page → Courier Delivery Button
   ↓
Select Courier:
   ├─ Load active couriers
   ├─ Search/filter by name or code
   └─ Select courier from dropdown
   ↓
Submit
   ↓
Backend:
   ├─ Create DeliverySession (delivery_type='COURIER')
   ├─ Set delivery_status = 'TO_CONSIDER'
   ├─ Set assigned_to = current_user
   ├─ Set courier_name from selected courier
   └─ Keep Invoice status = 'PACKED'
   ↓
Appears in: /delivery/courier-deliveries
   ↓
Courier Consider List Page:
   ├─ View all TO_CONSIDER courier deliveries
   ├─ Upload courier slip (image/PDF)
   └─ Submit slip upload
   ↓
Backend (on slip upload):
   ├─ Update delivery_status = 'IN_TRANSIT'
   ├─ Save courier_slip file
   ├─ Set end_time = now()
   ├─ Set delivery_status = 'DELIVERED'
   └─ Update Invoice status = 'DELIVERED'
   ↓
✅ COMPLETED
```

---

### 🔵 **Company Delivery Flow (Multi-Step)**

```
PACKED → Dispatch Page → Company Delivery Button
   ↓
Enter Staff Details:
   ├─ Staff Email (required)
   └─ Staff Name (required)
   ↓
Submit
   ↓
Backend:
   ├─ Validate user exists by email
   ├─ Create DeliverySession (delivery_type='INTERNAL')
   ├─ Set delivery_status = 'TO_CONSIDER'
   ├─ Set assigned_to = current_user
   └─ Keep Invoice status = 'PACKED'
   ↓
Appears in: /delivery/company-deliveries
   ↓
Company Consider List Page:
   ├─ View all TO_CONSIDER company deliveries
   ├─ See assigned staff member
   └─ Wait for staff to complete
   ↓
Staff Dashboard (/ops/delivery/my-deliveries):
   ├─ Staff member sees assigned deliveries
   ├─ Accept delivery
   └─ Mark as complete (with optional location data)
   ↓
Backend (on completion):
   ├─ Update delivery_status = 'IN_TRANSIT' (when accepted)
   ├─ Set start_time = now()
   ├─ Update Invoice status = 'DISPATCHED'
   ├─ On final completion:
   │   ├─ Set end_time = now()
   │   ├─ Set delivery_status = 'DELIVERED'
   │   ├─ Set delivered_by = staff_user
   │   └─ Update Invoice status = 'DELIVERED'
   └─ Save delivery location (optional)
   ↓
✅ COMPLETED
```

---

## Page Navigation Map

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND PAGES                          │
└─────────────────────────────────────────────────────────────┘

/delivery/dispatch (Dispatch Page)
   │
   ├─ Shows: All PACKED invoices without delivery sessions
   ├─ Action: "Start Delivery" button
   └─ Opens: DeliveryModal

DeliveryModal (Component)
   │
   ├─ Step 1: Select delivery type (3 options)
   ├─ Step 2: Counter Pickup → Select sub-type
   ├─ Step 3: Show form based on selection
   └─ Submit → Creates delivery session

/delivery/courier-deliveries (Courier Consider List)
   │
   ├─ Shows: delivery_type=COURIER, status=TO_CONSIDER
   ├─ Action: "Upload Slip" button
   └─ On upload → Marked as DELIVERED

/delivery/company-deliveries (Company Consider List)
   │
   ├─ Shows: delivery_type=INTERNAL, status=TO_CONSIDER
   ├─ Action: View assigned staff
   └─ Staff completes from their dashboard

/ops/delivery/my-deliveries (Staff Dashboard)
   │
   ├─ Shows: Deliveries assigned to logged-in DELIVERY role user
   ├─ Action: Accept & Complete delivery
   └─ On complete → Marked as DELIVERED

/history (Delivery History)
   │
   ├─ Shows: All completed deliveries
   ├─ Filter by: delivery_type, date range, status
   └─ View: Complete delivery details & timeline
```

---

## Status Transitions

```
┌──────────────────────────────────────────────────────────────┐
│                   STATUS TRANSITIONS                          │
└──────────────────────────────────────────────────────────────┘

Counter Pickup (DIRECT):
  PENDING → DELIVERED ✅

Courier Delivery:
  PENDING → TO_CONSIDER → IN_TRANSIT → DELIVERED ✅

Company Delivery:
  PENDING → TO_CONSIDER → IN_TRANSIT → DELIVERED ✅

Cancelled:
  Any status → CANCELLED ❌
```

---

## Database Relationships

```
Invoice (1) ←→ (1) DeliverySession
   ↑
   │ References
   ↓
Customer, Salesman, Items

DeliverySession
   ├─ assigned_to → User (who initiated)
   ├─ delivered_by → User (who completed)
   └─ invoice → Invoice

User
   ├─ assigned_deliveries (as assigned_to)
   ├─ delivered_invoices (as delivered_by)
   └─ created_invoices (as created_user)
```

---

## Key Differences Summary

| Feature | Counter Pickup | Courier Delivery | Company Delivery |
|---------|---------------|------------------|------------------|
| **Completion** | Instant | Multi-step | Multi-step |
| **Consider List** | No | Yes | Yes |
| **Staff Assignment** | No | No (courier assigned) | Yes |
| **File Upload** | No | Yes (slip) | No |
| **Final Status** | DELIVERED | DELIVERED | DELIVERED |
| **Invoice Status** | DELIVERED | PACKED → DISPATCHED → DELIVERED | PACKED → DISPATCHED → DELIVERED |
| **Dispatch Page** | ❌ Bypassed | ✅ Goes through | ✅ Goes through |

---

**Generated:** January 24, 2026
**Documentation:** DELIVERY_WORKFLOW_GUIDE.md
**Status:** ✅ Implementation Complete
