# Access Control API Documentation

**Base URL**: `http://localhost:8000/api/access`  
**Authentication**: JWT Bearer Token

---

## Endpoints

### 1. Get User Menus
`GET /api/access/menus/`

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

### 2. Get All Available Menus (Admin)
`GET /api/access/admin/menus/`

Get all menu items in the system.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "All menus retrieved successfully",
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
    ]
  }
}
```

---

### 3. Assign Menus to User (Admin)
`POST /api/access/admin/assign-menus/`

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

**Response (201 Created):**
```json
{
  "status": "success",
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
        "menu_code": "delivery"
      }
    ],
    "skipped": [],
    "total_assigned": 2,
    "total_skipped": 0
  }
}
```

---

### 4. Unassign Menus from User (Admin)
`POST /api/access/admin/unassign-menus/`

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

**Response (200 OK):**

```json
{
  "status": "success",
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

### 5. Get User's Menu Assignments (Admin)
`GET /api/access/admin/users/{user_id}/menus/`

View all menus assigned to a specific user.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**

```json
{
  "status": "success",
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
        "menu_url": "/",
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
        "url": "/",
        "order": 1,
        "children": []
      }
    ],
    "total_menus": 1
  }
}
```

---

## Available Menus

| Code | Name | URL | Parent |
|------|------|-----|--------|
| `dashboard` | Dashboard | `/` | - |
| `delivery` | Delivery Management | `/delivery` | - |
| `delivery_bills` | Bills | `/delivery/bills` | delivery |
| `delivery_picking` | Picking | `/delivery/picking` | delivery |
| `delivery_packing` | Packing | `/delivery/packing` | delivery |
| `delivery_tasks` | Delivery Tasks | `/delivery/tasks` | delivery |
| `purchase` | Purchase Management | `/purchase` | - |
| `purchase_orders` | Orders | `/purchase/orders` | purchase |
| `purchase_vendors` | Vendors | `/purchase/vendors` | purchase |
| `purchase_invoices` | Invoices | `/purchase/invoices` | purchase |
| `payment` | Payment Follow-up | `/payment` | - |
| `payment_outstanding` | Outstanding | `/payment/outstanding` | payment |
| `payment_followups` | Follow-ups | `/payment/followups` | payment |
| `reports` | Reports | `/reports` | - |
| `users` | User Management | `/users` | - |
| `settings` | Settings | `/settings` | - |
