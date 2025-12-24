# ALFA ERP - Development Notes

This document contains development notes, role design decisions, and implementation guidance for the ALFA ERP system.

---

## User Roles

### Recommended Role Structure

| Role | Purpose / Access |
| ---- | ---------------- |
| **ADMIN** | Full access, create users, dashboard, reports, configuration |
| **SUPERADMIN** | Full system access including super-admin configurations |
| **BILLING** | Create and manage sales orders (bills) |
| **PICKER** | Handle picking stage only |
| **PACKER** | Handle packing stage only |
| **DRIVER** | Update dispatch, delivery status |
| **USER** | Basic user role with limited access |

### Simplified Role Set (Alternative)
```
ADMIN
STORE (Picker + Packer combined)
DELIVERY
BILLING
VIEWER
```

---

## Sidebar & Menu Access Control

### Permission-Based Approach (Recommended)

Backend returns list of permissions:

```json
{
  "permissions": [
    "sales.view",
    "sales.update_status",
    "picking.view",
    "packing.view",
    "delivery.view"
  ]
}
```

Frontend menu filtering:

```javascript
const menuItems = [
  { label: "Dashboard", key: "dashboard" },
  { label: "Delivery", key: "delivery", permission: "sales.update_status" },
  { label: "Purchase Orders", key: "purchase", permission: "purchase.view" }
];

const allowedMenu = menuItems.filter(item =>
  !item.permission || user.permissions.includes(item.permission)
);
```

### Backend-Generated Sidebar

For centralized control, the backend returns the sidebar structure:

```json
{
  "sidebar": [
    { "name": "Dashboard", "url": "/dashboard" },
    { "name": "Invoices", "url": "/invoices" }
  ]
}
```

**Pros**: No frontend redeployment for menu changes  
**Cons**: More backend work

---

## Django App Structure

```
apps/
├── accounts/          # Users, Roles, Permissions, JWT Auth
├── accesscontrol/     # Menu items, User-Menu assignments
├── sales/             # Invoices, Picking, Packing, Delivery workflows
├── analytics/         # Dashboard stats, KPIs, reports
└── common/            # Shared utilities, response handlers
```

### Module Responsibilities

**accounts/**
- User model with role field
- JWT authentication
- Department and JobTitle models
- User management views

**accesscontrol/**
- MenuItem model (hierarchical menus)
- UserMenu model (user-to-menu assignments)
- Menu assignment views

**sales/**
- Invoice, InvoiceItem, InvoiceReturn models
- Customer, Salesman models
- PickingSession, PackingSession, DeliverySession models
- SSE real-time events
- Workflow views (start/complete picking/packing/delivery)

**analytics/**
- Dashboard summary endpoints (planned)
- KPI calculations (planned)

**common/**
- Standardized API response handlers
- Custom viewsets and mixins

---

## Key Implementation Decisions

1. **Single Role per User**: Currently each user has one role (not multi-role)
2. **Email-based User Identification**: Users scan email (via QR) to start/complete tasks
3. **SSE for Real-time Updates**: Using django-eventstream for live invoice updates
4. **Session Tracking**: Each workflow step (picking/packing/delivery) creates a session record
5. **Menu Access at Login**: User menus are returned during login response

---

*For detailed API documentation, see [docs/api/](docs/api/README.md)*
