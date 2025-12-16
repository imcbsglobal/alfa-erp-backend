# Menu Access Control API Documentation

Complete menu-based access control system for ALFA ERP. Menus are returned during login and managed by admins.

**Base URL**: `http://localhost:8000/api/`  
**Authentication**: JWT Bearer Token (except login)

---

## Overview

### Role-Based Menu Access

- **ADMIN / SUPERADMIN**: Automatically receive ALL menus in the system
- **Other Roles** (PICKER, PACKER, DRIVER, BILLING, USER): Receive only menus assigned by admin

### Menu Structure

Menus are hierarchical (parent-child) and returned as a tree structure with:
- `id`: Unique menu identifier
- `name`: Display name
- `code`: Unique code identifier
- `icon`: Icon identifier (Material Icons)
- `url`: Frontend route path
- `order`: Display order
- `children`: Array of child menus (nested items)

---

## Authentication & Login

### 1. Login (Returns Menus)
`POST /api/auth/login/`

Login endpoint that returns JWT tokens, user information, and accessible menus.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK) - ADMIN/SUPERADMIN:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login successful",
  "data": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "7a2750ff-dee3-4697-8b38-67e20d15df79",
      "email": "admin@gmail.com",
      "name": "Admin User",
      "avatar": "https://example.com/avatar.jpg",
      "role": "ADMIN",
      "department": "Operations",
      "department_id": "uuid",
      "job_title": {
        "id": "uuid",
        "title": "Manager"
      },
      "is_staff": false,
      "is_superuser": false,
      "groups": []
    },
    "menus": [
      {
        "id": "3ba6bb7a-162e-4e07-a8b5-ea4acbd84f8a",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      },
      {
        "id": "a3e2f800-1df2-4d7d-9fba-7378fcb9f2f0",
        "name": "User Management",
        "code": "user_management",
        "icon": "people",
        "url": "/user-management",
        "order": 2,
        "children": [
          {
            "id": "3fe93123-98e2-465d-86c4-ab8452e9f168",
            "name": "User List",
            "code": "user_list",
            "icon": "people",
            "url": "/user-management",
            "order": 1
          },
          {
            "id": "c3f8d255-0961-41ec-8970-052abb02a232",
            "name": "User Control",
            "code": "user_control",
            "icon": "settings",
            "url": "/user-control",
            "order": 2
          },
          {
            "id": "4302cd10-bc58-4e74-8d96-3727a8ae680c",
            "name": "Add User",
            "code": "add_user",
            "icon": "person_add",
            "url": "/add-user",
            "order": 3
          }
        ]
      },
      {
        "id": "c9bed12e-3b20-4dc3-9554-67ef922ee1dc",
        "name": "Master",
        "code": "master",
        "icon": "tune",
        "url": "/master/job-title",
        "order": 3,
        "children": [
          {
            "id": "9fcec07f-9823-43fc-9b03-3195f6a70988",
            "name": "Job Title",
            "code": "job_title",
            "icon": "work",
            "url": "/master/job-title",
            "order": 1
          }
        ]
      },
      {
        "id": "a90d8fda-f0dd-4237-9daa-721124614293",
        "name": "Delivery Management",
        "code": "delivery_management",
        "icon": "local_shipping",
        "url": "/delivery",
        "order": 4,
        "children": [
          {
            "id": "6d22d3e2-0daf-451c-9b94-d4edf7e5c8a4",
            "name": "Bills",
            "code": "delivery_bills",
            "icon": "receipt",
            "url": "/delivery/bills",
            "order": 1
          },
          {
            "id": "5d05bb3c-41ca-4a05-81dc-db1eb9f8a47f",
            "name": "Picking",
            "code": "delivery_picking",
            "icon": "inventory",
            "url": "/delivery/picking",
            "order": 2
          },
          {
            "id": "8d356a03-be4b-470d-99ba-5f1c56bb155b",
            "name": "Packing",
            "code": "delivery_packing",
            "icon": "inventory_2",
            "url": "/delivery/packing",
            "order": 3
          },
          {
            "id": "88de3c8c-a35c-42ec-8060-5aeb033d7afd",
            "name": "Delivery Tasks",
            "code": "delivery_tasks",
            "icon": "local_shipping",
            "url": "/delivery/tasks",
            "order": 4
          }
        ]
      },
      {
        "id": "36257e80-6969-4be6-9c5f-c4db755903f7",
        "name": "Purchase Management",
        "code": "purchase_management",
        "icon": "shopping_cart",
        "url": "/purchase",
        "order": 5,
        "children": [
          {
            "id": "9ed6ffed-7311-4e3a-af24-562315a618fc",
            "name": "Orders",
            "code": "purchase_orders",
            "icon": "list_alt",
            "url": "/purchase/orders",
            "order": 1
          },
          {
            "id": "36208166-446c-42c2-a9c8-19c02bca66ee",
            "name": "Vendors",
            "code": "purchase_vendors",
            "icon": "business",
            "url": "/purchase/vendors",
            "order": 2
          },
          {
            "id": "05aff752-5de4-422f-b0fe-67946c6d62ca",
            "name": "Invoices",
            "code": "purchase_invoices",
            "icon": "description",
            "url": "/purchase/invoices",
            "order": 3
          }
        ]
      },
      {
        "id": "feb8cb09-53b3-46a3-8cf7-0a3607280c1b",
        "name": "Payment Follow-up",
        "code": "payment_followup",
        "icon": "payment",
        "url": "/payment",
        "order": 6,
        "children": [
          {
            "id": "84afeb3d-b0c4-4887-a2e4-c91a26688655",
            "name": "Outstanding",
            "code": "payment_outstanding",
            "icon": "account_balance",
            "url": "/payment/outstanding",
            "order": 1
          },
          {
            "id": "2334a784-5aaf-4be5-9e5a-06303abcbe35",
            "name": "Follow-ups",
            "code": "payment_followups",
            "icon": "event_note",
            "url": "/payment/followups",
            "order": 2
          }
        ]
      },
      {
        "id": "cf7f1889-02ff-43ff-ba3e-17f4fa2cfa01",
        "name": "Reports",
        "code": "reports",
        "icon": "assessment",
        "url": "/reports",
        "order": 7,
        "children": []
      },
      {
        "id": "68c27648-0344-4d9f-aa80-3d95fa8f89ce",
        "name": "Settings",
        "code": "settings",
        "icon": "settings",
        "url": "/settings",
        "order": 8,
        "children": []
      }
    ]
  }
}
```

**Response (200 OK) - PICKER (Assigned Menus Only):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login successful",
  "data": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "email": "picker@example.com",
      "name": "John Picker",
      "role": "PICKER",
      "is_staff": false,
      "is_superuser": false
    },
    "menus": [
      {
        "id": "a90d8fda-f0dd-4237-9daa-721124614293",
        "name": "Delivery Management",
        "code": "delivery_management",
        "icon": "local_shipping",
        "url": "/delivery",
        "order": 4,
        "children": [
          {
            "id": "5d05bb3c-41ca-4a05-81dc-db1eb9f8a47f",
            "name": "Picking",
            "code": "delivery_picking",
            "icon": "inventory",
            "url": "/delivery/picking",
            "order": 2
          }
        ]
      }
    ]
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

**Notes:**
- Menus are loaded at login time and included in the response
- Users must re-login to see updated menu assignments
- ADMIN/SUPERADMIN roles automatically receive all active menus
- Other roles receive only menus assigned via UserMenu table

---

## User Endpoints

---

## User Endpoints

### 2. Get User Menus (Alternative)
`GET /api/access-control/menus/`

Alternative endpoint to fetch current user's menus after login (if needed for refresh).

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "User menus retrieved successfully",
  "data": {
    "menus": [
      {
        "id": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      }
    ],
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "User Name"
    }
  }
}
```

---

## Admin Endpoints (Menu Management)

All admin endpoints require `IsAdminUser` permission (user must have `is_staff=True` or role `ADMIN`/`SUPERADMIN`).

### 3. Get All Available Menus
`GET /api/access-control/admin/menus/`

Get all menus assigned to the authenticated user.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "User menus retrieved successfully",
  "data": {
    "menus": [
      {
        "id": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/",
        "order": 1,
        "children": []
      },
      {
        "id": "8f9e1234-b567-89ab-cdef-0123456789ab",
        "name": "Delivery Management",
        "code": "delivery",
        "icon": "local_shipping",
        "url": "/delivery",
        "order": 2,
        "children": [
          {
            "id": "1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
            "name": "Bills",
            "code": "delivery_bills",
            "icon": "receipt",
            "url": "/delivery/bills",
            "order": 1
          }
        ]
      }
    ],
    "user": {
      "id": 1,
      "email": "admin@gmail.com",
      "full_name": "Admin User"
    }
  }
}
```

---

### 3. Get All Available Menus
`GET /api/access-control/admin/menus/`

Get all menu items in the system (for admin to see what can be assigned).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "All menus retrieved successfully",
  "data": {
    "menus": [
      {
        "id": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      },
      {
        "id": "8f9e1234-b567-89ab-cdef-0123456789ab",
        "name": "Delivery Management",
        "code": "delivery_management",
        "icon": "local_shipping",
        "url": "/delivery",
        "order": 2,
        "children": [
          {
            "id": "1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
            "name": "Bills",
            "code": "delivery_bills",
            "icon": "receipt",
            "url": "/delivery/bills",
            "order": 1
          }
        ]
      }
    ]
  }
}
```

---

### 4. Assign Menus to User
`POST /api/access-control/admin/assign-menus/`

Assign menus to a specific user.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "menu_ids": [
    "cc17dc82-a37d-423a-bd21-ff659780ed93",
    "8f9e1234-b567-89ab-cdef-0123456789ab"
  ]
}
```

### 4. Assign Menus to User
`POST /api/access-control/admin/assign-menus/`

Assign menus to a specific user. User will see these menus on next login.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "menu_ids": [
    "cc17dc82-a37d-423a-bd21-ff659780ed93",
    "8f9e1234-b567-89ab-cdef-0123456789ab"
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Successfully assigned 2 menu(s) to user@example.com",
  "data": {
    "user": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "assigned": [
      {
        "id": "xyz-123-abc",
        "menu_id": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "menu_name": "Dashboard",
        "menu_code": "dashboard"
      },
      {
        "id": "xyz-456-def",
        "menu_id": "8f9e1234-b567-89ab-cdef-0123456789ab",
        "menu_name": "Delivery Management",
        "menu_code": "delivery_management"
      }
    ],
    "skipped": [],
    "total_assigned": 2,
    "total_skipped": 0
  }
}
```

---

### 5. Unassign Menus from User
`POST /api/access-control/admin/unassign-menus/`

Remove menu assignments from a user.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "menu_ids": [
    "cc17dc82-a37d-423a-bd21-ff659780ed93"
  ]
}
```

### 5. Unassign Menus from User
`POST /api/access-control/admin/unassign-menus/`

Remove menu assignments from a user. User will lose access on next login.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "menu_ids": [
    "cc17dc82-a37d-423a-bd21-ff659780ed93"
  ]
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Successfully unassigned 1 menu(s) from user@example.com",
  "data": {
    "user": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "unassigned": [
      {
        "menu_id": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "menu_name": "Dashboard"
      }
    ],
    "not_found": [],
    "total_unassigned": 1,
    "total_not_found": 0
  }
}
```

---

### 6. Get User's Menu Assignments
`GET /api/access-control/admin/users/{user_id}/menus/`

View all menus assigned to a specific user.

**Headers:**
```
Authorization: Bearer {admin_token}
```

### 6. Get User's Menu Assignments
`GET /api/access-control/admin/users/{user_id}/menus/`

View all menus assigned to a specific user (admin only).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "User menu assignments retrieved successfully",
  "data": {
    "user": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "assignments": [
      {
        "id": "xyz-123-abc",
        "menu": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "menu_name": "Dashboard",
        "menu_code": "dashboard",
        "menu_url": "/dashboard",
        "is_active": true,
        "assigned_by_email": "admin@example.com",
        "assigned_at": "2025-12-03T10:30:00Z"
      }
    ],
    "menu_structure": [
      {
        "id": "cc17dc82-a37d-423a-bd21-ff659780ed93",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      }
    ],
    "total_menus": 1
  }
}
```

---

## Implementation Guide

### Backend Logic

**Login Flow:**
1. User submits credentials to `POST /api/auth/login/`
2. Server validates credentials
3. Server checks user role:
   - If `user.is_admin_or_superadmin()` → return all menus
   - Else → return only assigned menus from `UserMenu` table
4. Response includes: `access`, `refresh`, `user`, and `menus`

**Helper Method:**
```python
# User model method
def is_admin_or_superadmin(self):
    return (
        self.is_staff or 
        self.is_superuser or 
        self.role in ['ADMIN', 'SUPERADMIN']
    )
```

### Frontend Integration

**1. Store Menus on Login:**
```javascript
// After successful login
const { access, refresh, user, menus } = response.data.data;

// Store in context/state
setUser(user);
setMenus(menus);
localStorage.setItem('accessToken', access);
localStorage.setItem('refreshToken', refresh);
```

**2. Render Navigation:**
```jsx
const Navigation = () => {
  const { menus } = useAuth();
  
  return (
    <nav>
      {menus.map(menu => (
        <MenuItem key={menu.id} menu={menu}>
          {menu.children.map(child => (
            <SubMenuItem key={child.id} item={child} />
          ))}
        </MenuItem>
      ))}
    </nav>
  );
};
```

**3. Route Protection:**
```jsx
const ProtectedRoute = ({ path, children }) => {
  const { menus } = useAuth();
  
  const hasAccess = menus.some(menu => 
    menu.url === path || 
    menu.children?.some(child => child.url === path)
  );
  
  if (!hasAccess) {
    return <Navigate to="/403" />;
  }
  
  return children;
};
```

**4. Check Access Helper:**
```javascript
const useHasMenuAccess = (menuCode) => {
  const { menus } = useAuth();
  
  return menus.some(menu => 
    menu.code === menuCode || 
    menu.children?.some(child => child.code === menuCode)
  );
};

// Usage
const canAccessPicking = useHasMenuAccess('delivery_picking');
```

---

## Security Notes

1. **Backend Enforcement**: Always validate permissions server-side on each API endpoint. Frontend menu hiding is UX only.

2. **Token Expiry**: Menus are in login response, not JWT. When token expires, user must re-login to get updated menus.

3. **Menu Updates**: Changes to user menu assignments only take effect on next login. For immediate updates, call `GET /api/access-control/menus/` or implement SSE notifications.

4. **ADMIN Bypass**: ADMIN/SUPERADMIN users automatically get all menus regardless of UserMenu assignments.

---

## Available Menus Reference

## Available Menus Reference

Current menu structure in the system:

| Code | Name | URL | Icon | Parent |
|------|------|-----|------|--------|
| `dashboard` | Dashboard | `/dashboard` | dashboard | - |
| `user_management` | User Management | `/user-management` | people | - |
| `user_list` | User List | `/user-management` | people | user_management |
| `user_control` | User Control | `/user-control` | settings | user_management |
| `add_user` | Add User | `/add-user` | person_add | user_management |
| `master` | Master | `/master/job-title` | tune | - |
| `job_title` | Job Title | `/master/job-title` | work | master |
| `delivery_management` | Delivery Management | `/delivery` | local_shipping | - |
| `delivery_bills` | Bills | `/delivery/bills` | receipt | delivery_management |
| `delivery_picking` | Picking | `/delivery/picking` | inventory | delivery_management |
| `delivery_packing` | Packing | `/delivery/packing` | inventory_2 | delivery_management |
| `delivery_tasks` | Delivery Tasks | `/delivery/tasks` | local_shipping | delivery_management |
| `purchase_management` | Purchase Management | `/purchase` | shopping_cart | - |
| `purchase_orders` | Orders | `/purchase/orders` | list_alt | purchase_management |
| `purchase_vendors` | Vendors | `/purchase/vendors` | business | purchase_management |
| `purchase_invoices` | Invoices | `/purchase/invoices` | description | purchase_management |
| `payment_followup` | Payment Follow-up | `/payment` | payment | - |
| `payment_outstanding` | Outstanding | `/payment/outstanding` | account_balance | payment_followup |
| `payment_followups` | Follow-ups | `/payment/followups` | event_note | payment_followup |
| `reports` | Reports | `/reports` | assessment | - |
| `settings` | Settings | `/settings` | settings | - |

---

## Role-Based Menu Examples

### Example 1: PICKER Role
Assigned menus:
- Delivery Management → Picking

**Login Response:**
```json
{
  "menus": [
    {
      "id": "uuid",
      "name": "Delivery Management",
      "code": "delivery_management",
      "url": "/delivery",
      "children": [
        {
          "id": "uuid",
          "name": "Picking",
          "code": "delivery_picking",
          "url": "/delivery/picking"
        }
      ]
    }
  ]
}
```

### Example 2: PACKER Role
Assigned menus:
- Delivery Management → Packing

### Example 3: DRIVER Role
Assigned menus:
- Delivery Management → Delivery Tasks

### Example 4: BILLING Role
Assigned menus:
- Delivery Management → Bills
- Purchase Management → Invoices
- Payment Follow-up (all children)

### Example 5: ADMIN/SUPERADMIN Role
**All menus** automatically (no assignment needed)

---

## Testing Examples

### Test 1: Login as ADMIN
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password"
  }'
```

**Expected**: Response includes all 8 top-level menus

### Test 2: Assign Menu to User
```bash
# First, get all menu IDs
curl -X GET http://localhost:8000/api/access-control/admin/menus/ \
  -H "Authorization: Bearer {admin_token}"

# Assign picking menu to user
curl -X POST http://localhost:8000/api/access-control/admin/assign-menus/ \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "menu_ids": ["delivery_picking_uuid"]
  }'
```

### Test 3: Login as PICKER
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "picker@example.com",
    "password": "password"
  }'
```

**Expected**: Response includes only Delivery Management → Picking

---

## Troubleshooting

**Q: User not seeing assigned menus**  
**A**: User must re-login after menu assignment. Menus are loaded at login time.

**Q: ADMIN seeing no menus**  
**A**: Check MenuItem table has active records. Run: `MenuItem.objects.filter(is_active=True).count()`

**Q: Frontend shows menu but API returns 403**  
**A**: Backend must enforce permissions separately. Don't rely only on frontend menu hiding.

**Q: Want immediate menu updates without re-login**  
**A**: Call `GET /api/access-control/menus/` or implement SSE notifications for live updates.

---

## Change Log

- **v1.0** (2025-12-15): Initial implementation with login-time menu delivery
- Role-based auto-access for ADMIN/SUPERADMIN
- Direct user-to-menu assignment for other roles
- Hierarchical menu structure support
