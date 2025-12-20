This is a project for a Pharmacy Management ERP, mainly focused on bulk distribution.

They handle 400+ active billings daily.

Current flow:
1. Create a new bill
2. A picker user selects the bill
3. The picker collects medicines from the racks
4. Medicines are handed over to packing
5. Packing users pack the medicines
6. Packed orders are sent for delivery

Delivery modes:
- Direct counter pickup
- Courier agency
- Direct delivery by staff

The goal is to define the business and software requirements, improve admin and user experience, maximize productivity, and enhance the complete workflow.

--------------------------------------------------

Suggested Flow:

When a new bill is created, it is pushed into the database with the following details:

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
  "items": {
    "name": "Paracetamol 650mg",
    "item_code": "PR650",
    "quantity": 20,
    "mrp": 3.50,
    "company_name": "Sun Pharma",
    "packing": "10x10 Tablets",
    "shelf_location": "R-12",
    "remarks": "",
    "expiry_date": "2025-12-23"
  }
}

After storing the invoice in the database, it appears in a common picking screen.

Any picker can select a bill from this screen by entering their email ID
(in the future, this will be replaced with QR code scanning).

Once selected:
- The invoice status changes to "Picking"
- A picking session is created and assigned to the picker
- The picker can see the invoice in their account

The picker goes through the racks (arranged rack-wise), picks each item, and marks it as completed.

If there are issues such as batch mismatch, expired items, or stock problems:
- The picker reports the issue
- The invoice is returned to the billing session

Billing users have their own accounts where they can:
- View invoices they created
- See returned or error invoices
- Identify at which stage the error occurred

After successful picking, the invoice moves to the packing session.

When the status becomes "Packed":
- The invoice appears on the common packing screen
- Packers select invoices using email ID or QR code
- Packers verify and pack the items

If packers find any issues or mismatches:
- The invoice can be returned to billing or picking with remarks

After packing, the invoice moves to delivery:
- Direct counter pickup
- Courier services (e.g., Ekart, Shiprocket)
- Delivery by company staff



SYSTEM VIEWS (ROLE-WISE)

==================================================
1. ADMIN LEVEL VIEWS
==================================================

Admin Dashboard
- Total invoices today
- Invoices by status (Created, Picking, Packing, Delivery, Closed)
- Live workload per stage
- Bottleneck alerts
- SLA breach alerts
- Error and return summary
- Stock alerts (low stock, near expiry)

Invoice Management
- View all invoices (global view)
- Search by invoice no, customer, date, status
- Filter by stage, error type, delivery mode
- Edit / cancel invoices
- Force status change (with reason)
- Reassign picker / packer / delivery staff

User Management
- Create / edit / deactivate users
- Assign roles and permissions
- Shift and availability management
- Productivity tracking per user

Inventory Management
- Stock summary (item-wise, batch-wise)
- Expired / blocked stock
- FIFO / FEFO configuration
- Rack and warehouse mapping

Reports & Analytics
- Daily / weekly / monthly reports
- User productivity reports
- Error frequency reports
- Delivery success reports
- Audit logs

System Settings
- Workflow configuration
- Status rules
- Integration settings (courier, SMS, ERP)
- Notification rules

==================================================
2. SUPERVISOR / DEPARTMENT HEAD VIEWS
==================================================

--------------------------------------------------
2.1 Billing Supervisor View
--------------------------------------------------
Billing Dashboard
- Invoices created today
- Returned invoices (from picking/packing)
- Error reasons (batch, expiry, stock)
- Pending corrections

Invoice Review
- View own team’s invoices
- Edit and resubmit returned invoices
- Communicate with picking/packing teams
- Hold / release invoices

Billing Performance
- Billing speed per user
- Error rate per biller
- Peak-hour load analysis

--------------------------------------------------
2.2 Picking Supervisor View
--------------------------------------------------
Picking Dashboard
- Invoices waiting for picking
- Invoices currently in picking
- Delayed picking alerts
- Picker availability

Picker Monitoring
- Live view of picker-wise workload
- Picking time per invoice
- Error reports raised by pickers

Control Actions
- Assign / reassign invoices to pickers
- Prioritize urgent invoices
- Approve partial picking
- Escalate issues to billing or admin

--------------------------------------------------
2.3 Packing Supervisor View
--------------------------------------------------
Packing Dashboard
- Invoices waiting for packing
- Packing in progress
- Packing delays
- Returned invoices

Packer Monitoring
- Packer-wise performance
- Packing accuracy
- Rework cases

Control Actions
- Assign / reassign packers
- Approve re-packing
- Escalate quality issues

--------------------------------------------------
2.4 Delivery Supervisor View
--------------------------------------------------
Delivery Dashboard
- Ready-for-dispatch invoices
- In-transit deliveries
- Failed / returned deliveries
- Courier-wise status

Delivery Control
- Assign delivery staff
- Select / change courier
- Track AWB and delivery status
- Handle delivery exceptions

Delivery Performance
- On-time delivery rate
- Courier comparison
- Staff delivery success rate

==================================================
3. USER LEVEL VIEWS
==================================================

--------------------------------------------------
3.1 Billing User View
--------------------------------------------------
- Create new invoice
- View created invoices
- Edit draft invoices
- View returned invoices with reasons
- Resubmit corrected invoices

--------------------------------------------------
3.2 Picker User View
--------------------------------------------------
My Picking Queue
- Assigned invoices
- Priority indicators
- Rack-wise item list

Picking Screen
- Mark item as picked
- Report issues (expiry, batch mismatch, shortage)
- Partial pick option

History
- Completed picks
- Error reports submitted

--------------------------------------------------
3.3 Packing User View
--------------------------------------------------
My Packing Queue
- Assigned invoices
- Packing checklist

Packing Screen
- Verify picked items
- Pack and confirm
- Report mismatch or damage

History
- Packed invoices
- Returned invoices

--------------------------------------------------
3.4 Delivery Staff View
--------------------------------------------------
My Delivery Queue
- Assigned deliveries
- Route-optimized list

Delivery Screen
- Update delivery status
- Capture proof of delivery
- Mark failed delivery with reason

History
- Completed deliveries
- Failed / returned deliveries

==================================================
4. COMMON FEATURES (ALL ROLES)
==================================================

- Role-based dashboards
- Notifications & alerts
- Search and filters
- Activity logs (own actions)
- Mobile-friendly UI
- Dark / light mode (optional)

==================================================

SYSTEM VIEWS (ROLE-WISE)

==================================================
1. ADMIN LEVEL VIEWS
==================================================

Admin Dashboard
- Total invoices today
- Invoices by status (Created, Picking, Packing, Delivery, Closed)
- Live workload per stage
- Bottleneck alerts
- SLA breach alerts
- Error and return summary
- Stock alerts (low stock, near expiry)

Invoice Management
- View all invoices (global view)
- Search by invoice no, customer, date, status
- Filter by stage, error type, delivery mode
- Edit / cancel invoices
- Force status change (with reason)
- Reassign picker / packer / delivery staff

User Management
- Create / edit / deactivate users
- Assign roles and permissions
- Shift and availability management
- Productivity tracking per user

Inventory Management
- Stock summary (item-wise, batch-wise)
- Expired / blocked stock
- FIFO / FEFO configuration
- Rack and warehouse mapping

Reports & Analytics
- Daily / weekly / monthly reports
- User productivity reports
- Error frequency reports
- Delivery success reports
- Audit logs

System Settings
- Workflow configuration
- Status rules
- Integration settings (courier, SMS, ERP)
- Notification rules

==================================================
2. SUPERVISOR / DEPARTMENT HEAD VIEWS
==================================================

--------------------------------------------------
2.1 Billing Supervisor View
--------------------------------------------------
Billing Dashboard
- Invoices created today
- Returned invoices (from picking/packing)
- Error reasons (batch, expiry, stock)
- Pending corrections

Invoice Review
- View own team’s invoices
- Edit and resubmit returned invoices
- Communicate with picking/packing teams
- Hold / release invoices

Billing Performance
- Billing speed per user
- Error rate per biller
- Peak-hour load analysis

--------------------------------------------------
2.2 Picking Supervisor View
--------------------------------------------------
Picking Dashboard
- Invoices waiting for picking
- Invoices currently in picking
- Delayed picking alerts
- Picker availability

Picker Monitoring
- Live view of picker-wise workload
- Picking time per invoice
- Error reports raised by pickers

Control Actions
- Assign / reassign invoices to pickers
- Prioritize urgent invoices
- Approve partial picking
- Escalate issues to billing or admin

--------------------------------------------------
2.3 Packing Supervisor View
--------------------------------------------------
Packing Dashboard
- Invoices waiting for packing
- Packing in progress
- Packing delays
- Returned invoices

Packer Monitoring
- Packer-wise performance
- Packing accuracy
- Rework cases

Control Actions
- Assign / reassign packers
- Approve re-packing
- Escalate quality issues

--------------------------------------------------
2.4 Delivery Supervisor View
--------------------------------------------------
Delivery Dashboard
- Ready-for-dispatch invoices
- In-transit deliveries
- Failed / returned deliveries
- Courier-wise status

Delivery Control
- Assign delivery staff
- Select / change courier
- Track AWB and delivery status
- Handle delivery exceptions

Delivery Performance
- On-time delivery rate
- Courier comparison
- Staff delivery success rate

==================================================
3. USER LEVEL VIEWS
==================================================

--------------------------------------------------
3.1 Billing User View
--------------------------------------------------
- Create new invoice
- View created invoices
- Edit draft invoices
- View returned invoices with reasons
- Resubmit corrected invoices

--------------------------------------------------
3.2 Picker User View
--------------------------------------------------
My Picking Queue
- Assigned invoices
- Priority indicators
- Rack-wise item list

Picking Screen
- Mark item as picked
- Report issues (expiry, batch mismatch, shortage)
- Partial pick option

History
- Completed picks
- Error reports submitted

--------------------------------------------------
3.3 Packing User View
--------------------------------------------------
My Packing Queue
- Assigned invoices
- Packing checklist

Packing Screen
- Verify picked items
- Pack and confirm
- Report mismatch or damage

History
- Packed invoices
- Returned invoices

--------------------------------------------------
3.4 Delivery Staff View
--------------------------------------------------
My Delivery Queue
- Assigned deliveries
- Route-optimized list

Delivery Screen
- Update delivery status
- Capture proof of delivery
- Mark failed delivery with reason

History
- Completed deliveries
- Failed / returned deliveries

==================================================
4. COMMON FEATURES (ALL ROLES)
==================================================

- Role-based dashboards
- Notifications & alerts
- Search and filters
- Activity logs (own actions)
- Mobile-friendly UI
- Dark / light mode (optional)

==================================================



| Analytics API Endpoint                        | Method | Description                                                           |
| ----------------------------------- | ------ | --------------------------------------------------------------------- |
| `/api/analytics/invoices/summary/`  | GET    | Get total invoices by status, daily/weekly/monthly                    |
| `/api/analytics/invoices/errors/`   | GET    | List invoices with errors/returns                                     |
| `/api/analytics/picking/summary/`   | GET    | Picker performance metrics                                            |
| `/api/analytics/picking/history/`   | GET    | Detailed picking logs per invoice/user                                |
| `/api/analytics/packing/summary/`   | GET    | Packer performance metrics                                            |
| `/api/analytics/packing/history/`   | GET    | Detailed packing logs per invoice/user                                |
| `/api/analytics/delivery/summary/`  | GET    | Delivery performance metrics                                          |
| `/api/analytics/delivery/history/`  | GET    | Detailed delivery logs per invoice/user                               |
| `/api/analytics/inventory/summary/` | GET    | Stock levels, low stock, near-expiry items                            |
| `/api/analytics/inventory/history/` | GET    | Inventory usage history by batch/item                                 |
| `/api/analytics/user/productivity/` | GET    | User productivity metrics (billing, picking, packing, delivery)       |
| `/api/analytics/kpi/overview/`      | GET    | Aggregated KPIs: avg processing time, error rates, delivery success   |
| `/api/analytics/alerts/`            | GET    | Active alerts: SLA breach, low stock, delayed deliveries              |
| `/api/analytics/export/csv/`        | GET    | Export analytics data in CSV format                                   |
| `/api/analytics/export/pdf/`        | GET    | Export analytics data in PDF format                                   |
| `/api/analytics/filter/`            | POST   | Filter analytics data by date, user, invoice status, item, or courier |
| `/api/analytics/trends/`            | GET    | Historical trends (invoices, picking, packing, delivery, stock)       |
| `/api/analytics/reports/custom/`    | POST   | Generate custom reports with user-defined filters                     |
| `/api/analytics/dashboard/`         | GET    | Dashboard summary data for Admin/Supervisor                           |
| `/api/analytics/dashboard/user/`    | GET    | Dashboard summary data for individual users (picker/packer/delivery)  |
