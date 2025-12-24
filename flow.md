# ALFA ERP - Business Flow & Workflow Design

This document describes the business flow and workflow design for the ALFA ERP system, a Pharmacy Management ERP focused on bulk distribution handling 400+ active billings daily.

---

## Current Workflow Overview

1. Create a new bill
2. A picker user selects the bill
3. The picker collects medicines from the racks
4. Medicines are handed over to packing
5. Packing users pack the medicines
6. Packed orders are sent for delivery

### Delivery Modes
- Direct counter pickup
- Courier agency
- Direct delivery by staff

---

## Invoice Flow

When a new bill is created, it is pushed into the database with the following structure:

```json
{
  "invoice_no": "LTPI-77282",
  "invoice_date": "2025-01-18",
  "salesman": "Ajay",
  "created_by": "admin",
  "priority": "HIGH",
  "customer": {
    "code": "CUST-889",
    "name": "LifeCare Pharmacy",
    "area": "Kozhikode",
    "address1": "Near Railway Station",
    "phone1": "9876543210",
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
      "batch_no": "B123",
      "expiry_date": "2025-12-23"
    }
  ]
}
```

### Picking Process
After storing the invoice, it appears in a common picking screen. Pickers:
- Select a bill by scanning their email/QR code
- Invoice status changes to "PICKING"
- A picking session is created and assigned
- Go through racks, pick items, mark as completed
- Can report issues (batch mismatch, expired items, stock problems)

### Packing Process
After successful picking:
- Invoice appears on the packing screen
- Packers select invoices using email/QR code
- Verify and pack items
- Can return invoices with remarks if issues found

### Delivery Process
After packing, invoice moves to delivery:
- **DIRECT**: Customer counter pickup
- **COURIER**: External courier service (with tracking)
- **INTERNAL**: Delivery by company staff

---

## Status Transitions

```
INVOICED → PICKING → PICKED → PACKING → PACKED → DISPATCHED → DELIVERED
                ↓           ↓           ↓
              REVIEW (returned to billing for corrections)
```

---

## Role-Based System Views

### 1. Admin Level
- **Dashboard**: Total invoices, status breakdown, bottleneck alerts, SLA breach alerts
- **Invoice Management**: Search, filter, edit, force status changes, reassign staff
- **User Management**: Create/edit/deactivate users, assign roles, track productivity
- **Reports & Analytics**: Daily/weekly/monthly reports, productivity, error frequency

### 2. Supervisor Views
- **Billing Supervisor**: Returned invoices, error reasons, pending corrections
- **Picking Supervisor**: Queue monitoring, picker workload, urgent invoice prioritization
- **Packing Supervisor**: Packing progress, packer performance, quality issues
- **Delivery Supervisor**: Dispatch status, courier tracking, delivery performance

### 3. User Level Views
- **Billing User**: Create invoices, view returns, resubmit corrections
- **Picker User**: Picking queue, rack-wise items, report issues, history
- **Packer User**: Packing queue, verify items, pack/confirm, history
- **Delivery Staff**: Delivery queue, update status, proof of delivery

### 4. Common Features
- Role-based dashboards
- Real-time notifications & alerts
- Search and filters
- Activity logs
- Mobile-friendly UI

---

## Planned Analytics Endpoints

| Endpoint | Method | Description |
| -------- | ------ | ----------- |
| `/api/analytics/invoices/summary/` | GET | Invoice totals by status |
| `/api/analytics/picking/summary/` | GET | Picker performance metrics |
| `/api/analytics/packing/summary/` | GET | Packer performance metrics |
| `/api/analytics/delivery/summary/` | GET | Delivery performance metrics |
| `/api/analytics/user/productivity/` | GET | User productivity metrics |
| `/api/analytics/kpi/overview/` | GET | Aggregated KPIs |
| `/api/analytics/dashboard/` | GET | Admin/Supervisor dashboard data |

---

*For API implementation details, see [docs/api/sales.md](docs/api/sales.md)*
