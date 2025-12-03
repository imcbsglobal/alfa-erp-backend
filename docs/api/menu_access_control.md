# Menu Access Control API

API endpoints for managing user menu assignments and retrieving menu structures.

## Base URL
```
/api/access
```

## Overview

The ALFA ERP system uses a **direct user-to-menu assignment** approach for access control. Instead of role-based permissions, menus are assigned directly to individual users. This provides maximum flexibility and simplicity.

**Flow**: User → UserMenu → MenuItem (No roles!)

---

## Endpoints

### Get User Menus

Retrieve the hierarchical menu structure for the authenticated user.

**Endpoint**: `GET /api/access/menus/`

**Authentication**: Required (Bearer Token)

**Request Headers**:
```http
Authorization: Bearer <access_token>
```

**Response**:
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
          },
          {
            "id": "2b3c4d5e-6f7g-8h9i-0j1k-l2m3n4o5p6q7",
            "name": "Picking",
            "code": "delivery_picking",
            "icon": "inventory",
            "url": "/delivery/picking",
            "order": 2
          },
          {
            "id": "3c4d5e6f-7g8h-9i0j-1k2l-m3n4o5p6q7r8",
            "name": "Packing",
            "code": "delivery_packing",
            "icon": "inventory_2",
            "url": "/delivery/packing",
            "order": 3
          },
          {
            "id": "4d5e6f7g-8h9i-0j1k-2l3m-n4o5p6q7r8s9",
            "name": "Delivery Tasks",
            "code": "delivery_tasks",
            "icon": "local_shipping",
            "url": "/delivery/tasks",
            "order": 4
          }
        ]
      },
      {
        "id": "5e6f7g8h-9i0j-1k2l-3m4n-o5p6q7r8s9t0",
        "name": "Purchase Management",
        "code": "purchase",
        "icon": "shopping_cart",
        "url": "/purchase",
        "order": 3,
        "children": [
          {
            "id": "6f7g8h9i-0j1k-2l3m-4n5o-p6q7r8s9t0u1",
            "name": "Orders",
            "code": "purchase_orders",
            "icon": "list_alt",
            "url": "/purchase/orders",
            "order": 1
          },
          {
            "id": "7g8h9i0j-1k2l-3m4n-5o6p-q7r8s9t0u1v2",
            "name": "Vendors",
            "code": "purchase_vendors",
            "icon": "business",
            "url": "/purchase/vendors",
            "order": 2
          },
          {
            "id": "8h9i0j1k-2l3m-4n5o-6p7q-r8s9t0u1v2w3",
            "name": "Invoices",
            "code": "purchase_invoices",
            "icon": "description",
            "url": "/purchase/invoices",
            "order": 3
          }
        ]
      },
      {
        "id": "9i0j1k2l-3m4n-5o6p-7q8r-s9t0u1v2w3x4",
        "name": "Payment Follow-up",
        "code": "payment",
        "icon": "payment",
        "url": "/payment",
        "order": 4,
        "children": [
          {
            "id": "0j1k2l3m-4n5o-6p7q-8r9s-t0u1v2w3x4y5",
            "name": "Outstanding",
            "code": "payment_outstanding",
            "icon": "account_balance",
            "url": "/payment/outstanding",
            "order": 1
          },
          {
            "id": "1k2l3m4n-5o6p-7q8r-9s0t-u1v2w3x4y5z6",
            "name": "Follow-ups",
            "code": "payment_followups",
            "icon": "event_note",
            "url": "/payment/followups",
            "order": 2
          }
        ]
      },
      {
        "id": "2l3m4n5o-6p7q-8r9s-0t1u-v2w3x4y5z6a7",
        "name": "Reports",
        "code": "reports",
        "icon": "assessment",
        "url": "/reports",
        "order": 5,
        "children": []
      },
      {
        "id": "3m4n5o6p-7q8r-9s0t-1u2v-w3x4y5z6a7b8",
        "name": "User Management",
        "code": "users",
        "icon": "people",
        "url": "/users",
        "order": 6,
        "children": []
      },
      {
        "id": "4n5o6p7q-8r9s-0t1u-2v3w-x4y5z6a7b8c9",
        "name": "Settings",
        "code": "settings",
        "icon": "settings",
        "url": "/settings",
        "order": 7,
        "children": []
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

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `menus` | Array | Hierarchical array of menu items assigned to the user |
| `menus[].id` | UUID | Unique identifier for the menu item |
| `menus[].name` | String | Display name of the menu (e.g., "Dashboard", "Delivery Management") |
| `menus[].code` | String | Unique code identifier (e.g., "dashboard", "delivery") |
| `menus[].icon` | String | Icon class or name for UI rendering |
| `menus[].url` | String | Frontend route path |
| `menus[].order` | Integer | Display order (ascending) |
| `menus[].children` | Array | Child menu items (sub-menus) |
| `user` | Object | Basic user information |

**Error Responses**:

```json
// 401 Unauthorized - Invalid or missing token
{
  "status": "error",
  "message": "Authentication credentials were not provided.",
  "status_code": 401
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:8000/api/access/menus/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

**JavaScript Example**:
```javascript
const response = await fetch('/api/access/menus/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
const menus = data.data.menus;

// Render navigation
renderNavbar(menus);
```

**Python Example**:
```python
import requests

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/access/menus/', headers=headers)
data = response.json()

menus = data['data']['menus']
user = data['data']['user']

print(f"User: {user['email']}")
print(f"Menus: {len(menus)} items")
```

---

## Login with Menus

When a user logs in, the menu structure is automatically included in the response. This eliminates the need for a separate API call to fetch menus.

**Endpoint**: `POST /api/auth/login/`

See [Authentication API Documentation](./authentication.md) for full details.

**Quick Example**:
```json
// Request
{
  "email": "user@example.com",
  "password": "password123"
}

// Response includes menus
{
  "status": "success",
  "data": {
    "access": "jwt_token...",
    "refresh": "jwt_token...",
    "user": {...},
    "menus": [...]  // ← Menu structure included here
  }
}
```

---

## Menu Structure

### Menu Hierarchy

Menus follow a parent-child hierarchy:
- **Top-level menus** (`parent=null`): Main navigation items
- **Sub-menus** (`parent=menu_id`): Nested under a parent menu

### Available Menu Items

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

### Menu Icons

Icons are provided as Material Icons class names. Frontend should map these to appropriate icon libraries:

- `dashboard` - Home/Dashboard icon
- `local_shipping` - Delivery truck icon
- `receipt` - Document/Bill icon
- `inventory` - Box/Package icon
- `inventory_2` - Stacked boxes icon
- `shopping_cart` - Shopping cart icon
- `list_alt` - List icon
- `business` - Building/Company icon
- `description` - Document icon
- `payment` - Credit card icon
- `account_balance` - Bank/Finance icon
- `event_note` - Calendar/Notes icon
- `assessment` - Chart/Report icon
- `people` - Users icon
- `settings` - Gear icon

---

## Frontend Integration

### React/Next.js Example

```jsx
import { useEffect, useState } from 'react';
import Link from 'next/link';

function Navbar() {
  const [menus, setMenus] = useState([]);
  
  useEffect(() => {
    // Get menus from login response or fetch separately
    const storedMenus = localStorage.getItem('menus');
    if (storedMenus) {
      setMenus(JSON.parse(storedMenus));
    } else {
      fetchMenus();
    }
  }, []);
  
  const fetchMenus = async () => {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/access/menus/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    setMenus(data.data.menus);
    localStorage.setItem('menus', JSON.stringify(data.data.menus));
  };
  
  return (
    <nav className="navbar">
      {menus.map(menu => (
        <NavItem key={menu.id} item={menu} />
      ))}
    </nav>
  );
}

function NavItem({ item }) {
  return (
    <div className="nav-item">
      <Link href={item.url}>
        <span className="icon">{item.icon}</span>
        <span className="label">{item.name}</span>
      </Link>
      {item.children && item.children.length > 0 && (
        <div className="submenu">
          {item.children.map(child => (
            <NavItem key={child.id} item={child} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <nav class="navbar">
    <nav-item 
      v-for="menu in menus" 
      :key="menu.id" 
      :item="menu" 
    />
  </nav>
</template>

<script>
export default {
  data() {
    return {
      menus: []
    };
  },
  async mounted() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/access/menus/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    this.menus = data.data.menus;
  }
};
</script>
```

### Angular Example

```typescript
import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-navbar',
  template: `
    <nav class="navbar">
      <app-nav-item 
        *ngFor="let menu of menus" 
        [item]="menu">
      </app-nav-item>
    </nav>
  `
})
export class NavbarComponent implements OnInit {
  menus: any[] = [];
  
  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    const token = localStorage.getItem('access_token');
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
    
    this.http.get('/api/access/menus/', { headers })
      .subscribe(response => {
        this.menus = response.data.menus;
      });
  }
}
```

---

## Admin Operations

Menu assignments are managed through the Django Admin panel or programmatically.

### Django Admin

1. Navigate to `/admin/`
2. Go to **Access control → User menus**
3. Click **Add user menu**
4. Select:
   - User
   - Menu item
   - Assigned by (optional)
   - Is active (checkbox)
5. Save

### Programmatic Assignment

```python
from django.contrib.auth import get_user_model
from apps.accesscontrol.models import MenuItem, UserMenu

User = get_user_model()

# Get user and admin
user = User.objects.get(email='john@example.com')
admin = User.objects.get(email='admin@example.com')

# Assign specific menus
dashboard = MenuItem.objects.get(code='dashboard')
delivery = MenuItem.objects.get(code='delivery')

UserMenu.objects.create(user=user, menu=dashboard, assigned_by=admin)
UserMenu.objects.create(user=user, menu=delivery, assigned_by=admin)

# Assign all top-level menus
menus = MenuItem.objects.filter(parent=None)
for menu in menus:
    UserMenu.objects.get_or_create(
        user=user,
        menu=menu,
        defaults={'assigned_by': admin}
    )
```

---

## Best Practices

### Caching
Store menus in localStorage/sessionStorage after login to avoid repeated API calls:

```javascript
// After login
localStorage.setItem('menus', JSON.stringify(loginResponse.data.menus));

// On app load
const menus = JSON.parse(localStorage.getItem('menus') || '[]');

// Refresh on logout
localStorage.removeItem('menus');
```

### Route Protection
Use menu data to protect routes on the frontend:

```javascript
function ProtectedRoute({ path, children }) {
  const menus = JSON.parse(localStorage.getItem('menus') || '[]');
  const hasAccess = checkMenuAccess(menus, path);
  
  if (!hasAccess) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
}

function checkMenuAccess(menus, path) {
  for (const menu of menus) {
    if (menu.url === path) return true;
    if (menu.children) {
      for (const child of menu.children) {
        if (child.url === path) return true;
      }
    }
  }
  return false;
}
```

### Dynamic Navigation
Build navigation dynamically based on available menus:

```javascript
// Only render menu items user has access to
{menus.map(menu => (
  <Link key={menu.id} to={menu.url}>
    {menu.name}
  </Link>
))}
```

### Menu Refresh
Refresh menus when permissions change:

```javascript
async function refreshMenus() {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/access/menus/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  localStorage.setItem('menus', JSON.stringify(data.data.menus));
  // Trigger UI update
  window.location.reload();
}
```

---

## Notes

- Menus are assigned per user (not per role)
- Sub-menus inherit parent menu's access (if user has parent, they should also have children assigned explicitly)
- Inactive menus (`is_active=false`) are not returned
- Menu order is respected in the response
- UUIDs are used for menu IDs

---

## See Also

- [Authentication API](./authentication.md) - Login endpoint includes menu structure
- [User Management API](./users.md) - Managing users
