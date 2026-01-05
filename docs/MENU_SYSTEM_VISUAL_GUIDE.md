# Menu Access Control System - Visual Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         LOGIN FLOW                               │
└─────────────────────────────────────────────────────────────────┘

User Login
   ↓
CustomTokenObtainPairSerializer.validate()
   ↓
Check User Role
   ↓
┌──────────────────┬──────────────────────────────────────────────┐
│  SUPERADMIN?     │  Other Roles                                 │
├──────────────────┼──────────────────────────────────────────────┤
│  menus = []      │  UserMenu.get_user_menu_structure(user)      │
│  (empty array)   │  → Returns assigned menus from database       │
└──────────────────┴──────────────────────────────────────────────┘
   ↓                                ↓
Frontend uses                  Frontend uses
menuConfig.js                  menus from login response
(all menus shown)              (only assigned menus shown)
```

## Role-Based Menu Assignment

```
┌────────────────────────────────────────────────────────────────┐
│                      ROLE → MENU MAPPING                        │
└────────────────────────────────────────────────────────────────┘

SUPERADMIN
  └─> [] (empty - frontend shows all via menuConfig.js)

ADMIN
  ├─> Dashboard
  ├─> Picking (List, My Assigned)
  ├─> Delivery (all submenus)
  ├─> History (History, Consolidate)
  ├─> User Management (List, Control)
  └─> Master (Job Title, Department, Courier)

USER / STORE
  ├─> Dashboard
  ├─> Picking (List, My Assigned)
  └─> History (History, Consolidate)

BILLING (⚠️ Frontend expects "BILLER")
  ├─> Dashboard
  └─> Billing (Invoice List, Reviewed Bills)

PACKER
  ├─> Dashboard
  └─> Packing (List, My Assigned)

DELIVERY
  ├─> Dashboard
  └─> Delivery (Dispatch, Courier, Company, My Assigned)

PICKER
  └─> Dashboard (❗only dashboard, no picking access)

DRIVER
  ├─> Dashboard
  └─> Delivery (Dispatch, My Assigned)
```

## Database Structure

```
┌──────────────────────────────────────────────────────────────┐
│                     DATABASE TABLES                           │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│     MenuItem        │
├─────────────────────┤
│ id (UUID)           │
│ code (unique)       │
│ name                │
│ icon                │
│ url                 │
│ parent_id (FK)      │ ← Self-referencing for hierarchy
│ order               │
│ is_active           │
└─────────────────────┘
         │
         │ (Many-to-Many through UserMenu)
         ↓
┌─────────────────────┐         ┌─────────────────────┐
│     UserMenu        │←────────│       User          │
├─────────────────────┤         ├─────────────────────┤
│ id (UUID)           │         │ id (UUID)           │
│ user_id (FK)        │         │ email               │
│ menu_id (FK)        │         │ role                │
│ assigned_by (FK)    │         │ name                │
│ is_active           │         │ department          │
│ assigned_at         │         │ job_title           │
└─────────────────────┘         └─────────────────────┘
```

## Menu Hierarchy Example

```
┌──────────────────────────────────────────────────────────────┐
│                    MENU TREE STRUCTURE                        │
└──────────────────────────────────────────────────────────────┘

1. Dashboard [dashboard] → /dashboard
   (no children)

2. Invoice [billing] → /billing/invoices
   ├─ Invoice List [billing_invoice_list] → /billing/invoices
   └─ Reviewed Bills [billing_reviewed] → /billing/reviewed

3. Picking [invoices] → /invoices
   ├─ Picking List [picking_list] → /invoices
   └─ My Assigned Picking [my_assigned_picking] → /invoices/my

4. Packing [packing] → /packing/invoices
   ├─ Packing List [packing_list] → /packing/invoices
   └─ My Assigned Packing [my_assigned_packing] → /packing/my

5. Delivery [delivery] → /delivery/dispatch
   ├─ Dispatch Orders [delivery_dispatch] → /delivery/dispatch
   ├─ Courier List [delivery_courier_list] → /delivery/courier-list
   ├─ Company Delivery List [delivery_company_list] → /delivery/company-list
   └─ My Assigned Delivery [my_assigned_delivery] → /delivery/my

6. History [history] → /history
   ├─ History [history_main] → /history
   └─ Consolidate [history_consolidate] → /history/consolidate

7. User Management [user-management] → /user-management
   ├─ User List [user_list] → /user-management
   └─ User Control [user_control] → /user-control

8. Master [master] → /master/job-title
   ├─ Job Title [job_title] → /master/job-title
   ├─ Department [department] → /master/department
   └─ Courier [courier] → /master/courier

Total: 8 parent menus, 22 child menus = 30 menu items
```

## API Response Structure

### Login Success Response

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "packer@example.com",
      "name": "John Packer",
      "avatar": null,
      "role": "PACKER",
      "department": "Warehouse",
      "department_id": "abc123...",
      "job_title": {
        "id": "def456...",
        "title": "Warehouse Packer"
      },
      "groups": [],
      "is_staff": false,
      "is_superuser": false
    },
    "menus": [
      {
        "id": "menu-uuid-1",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "LayoutDashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      },
      {
        "id": "menu-uuid-2",
        "name": "Packing",
        "code": "packing",
        "icon": "Box",
        "url": "/packing/invoices",
        "order": 4,
        "children": [
          {
            "id": "menu-uuid-3",
            "name": "Packing List",
            "code": "packing_list",
            "icon": "Box",
            "url": "/packing/invoices",
            "order": 1
          },
          {
            "id": "menu-uuid-4",
            "name": "My Assigned Packing",
            "code": "my_assigned_packing",
            "icon": "PlusCircle",
            "url": "/packing/my",
            "order": 2
          }
        ]
      }
    ]
  }
}
```

## Frontend Menu Rendering Logic

```javascript
// Pseudocode from menuConfig.js

// 1. Check if user is SUPERADMIN
if (user.role === 'SUPERADMIN') {
  // Use MENU_CONFIG from menuConfig.js (all menus)
  renderMenus(MENU_CONFIG)
} else {
  // Use menus array from login response
  renderMenus(user.menus)
}

// 2. For each menu, check hasAccess function
MENU_CONFIG.forEach(menu => {
  if (menu.hasAccess) {
    if (menu.hasAccess(user, permissions)) {
      renderMenu(menu)
    }
  } else {
    renderMenu(menu) // No access check = show to all
  }
})

// 3. Handle dynamic paths
const path = typeof menu.path === 'function' 
  ? menu.path(user)  // e.g., PACKER gets /ops/packing/invoices
  : menu.path;       // e.g., ADMIN gets /packing/invoices
```

## Path Resolution Flow

```
User clicks "Packing List" menu
   ↓
Frontend checks user role
   ↓
┌──────────────────┬──────────────────────────┐
│  PACKER role?    │  Other roles             │
├──────────────────┼──────────────────────────┤
│  /ops/packing/   │  /packing/invoices       │
│  invoices        │                          │
└──────────────────┴──────────────────────────┘
   ↓                        ↓
Backend receives request
   ↓
URL routing resolves to same view
   ↓
┌────────────────────────────────────────┐
│  Both paths → PackingInvoicesView      │
└────────────────────────────────────────┘
   ↓
Response rendered
```

## Command Workflow

```
python manage.py seed_menus --clear --assign
   ↓
┌─────────────────────────────────────────┐
│  1. Delete all UserMenu records         │
│  2. Delete all MenuItem records         │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  3. Create 8 parent menus               │
│  4. Create 22 child menus               │
└─────────────────────────────────────────┘
   ↓
┌─────────────────────────────────────────┐
│  5. Get all active users                │
│  6. For each user:                      │
│     - Get role-specific menus           │
│     - Create UserMenu records           │
│     - Link user ↔ menus                 │
└─────────────────────────────────────────┘
   ↓
✓ Complete: Users have menus assigned
```

## Security Flow

```
┌──────────────────────────────────────────────────────────┐
│              MENU ACCESS VALIDATION                       │
└──────────────────────────────────────────────────────────┘

User requests /packing/invoices
   ↓
Backend checks:
   ↓
1. Is user authenticated? (JWT valid)
   ↓
2. Does user have PACKER role OR menu assigned?
   ↓
3. Is menu active (is_active=True)?
   ↓
┌──────────────────┬────────────────────────────┐
│  All checks ✓    │  Any check fails           │
├──────────────────┼────────────────────────────┤
│  Allow access    │  401 Unauthorized          │
│  Return data     │  Redirect to login         │
└──────────────────┴────────────────────────────┘
```

## Migration Path for Existing Users

```
┌─────────────────────────────────────────────────────────┐
│           BEFORE RUNNING seed_menus                      │
└─────────────────────────────────────────────────────────┘

Existing Users:
  - user1@example.com (role: ADMIN)      → 0 menus
  - user2@example.com (role: PACKER)     → 0 menus
  - user3@example.com (role: BILLING)    → 0 menus

┌─────────────────────────────────────────────────────────┐
│     RUN: python manage.py seed_menus --clear --assign   │
└─────────────────────────────────────────────────────────┘

Result:
  - 30 MenuItem records created
  - UserMenu records auto-assigned based on roles

┌─────────────────────────────────────────────────────────┐
│           AFTER RUNNING seed_menus                       │
└─────────────────────────────────────────────────────────┘

Updated Users:
  - user1@example.com (role: ADMIN)      → 20+ menus
  - user2@example.com (role: PACKER)     → 3 menus
  - user3@example.com (role: BILLING)    → 3 menus

Next Login:
  → Each user gets correct menus[] in response
  → Frontend renders only assigned menus
```

## Troubleshooting Decision Tree

```
User doesn't see expected menus?
   ↓
Is user SUPERADMIN?
   ├─ YES → Check frontend menuConfig.js (should show all)
   └─ NO  → Continue
   ↓
Check login response (menus array)
   ↓
Is menus array empty?
   ├─ YES → User has no menus assigned
   │         → Run: python manage.py seed_menus --assign
   └─ NO  → Continue
   ↓
Do menus match expected role?
   ├─ NO  → Check UserMenu records in database
   │         → Reassign menus for user
   └─ YES → Continue
   ↓
Frontend not showing menus?
   ├─ Check console errors
   ├─ Verify menuConfig.js hasAccess functions
   └─ Check role name match (BILLER vs BILLING)
```

---

**Visual Legend:**
- `→` Flow direction
- `├─` Branch
- `└─` End branch
- `↓` Continue down
- `[code]` Database code field
- `/path` URL path
- `✓` Success
- `❌` Error
- `⚠️` Warning
