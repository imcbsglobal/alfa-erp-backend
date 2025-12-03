# Direct User-to-Menu Assignment System

## Overview
Simplified access control system where **menus are assigned directly to users** without using roles.

**Flow**: User → UserMenu → MenuItem (No roles!)

## Key Changes from Previous System
- ❌ **Removed**: Role model, UserRole model
- ✅ **Added**: UserMenu model (direct user-to-menu assignment)
- ✅ **Simplified**: No role hierarchy, just assign menus to users

## How It Works

### 1. Menu Items
Menu items represent individual navbar links that can be assigned to users.

**Model**: `MenuItem`
- `name` - Display name (e.g., "Dashboard", "Delivery Management")
- `code` - Unique identifier (e.g., "dashboard", "delivery")
- `icon` - Icon class (e.g., "dashboard", "local_shipping")
- `url` - Frontend route (e.g., "/", "/delivery")
- `parent` - Parent menu for nesting (nullable)
- `order` - Display order
- `is_active` - Whether menu is active

### 2. User-Menu Assignment
Users are directly assigned menus through the UserMenu model.

**Model**: `UserMenu`
- `user` - User who has access
- `menu` - Menu item assigned
- `assigned_by` - Admin who made the assignment
- `assigned_at` - Timestamp
- `is_active` - Whether assignment is active

## Setup

### 1. Seed Menus
```bash
python manage.py seed_menus
```

This creates 16 menu items:
- Dashboard
- Delivery Management (with 4 sub-menus)
- Purchase Management (with 3 sub-menus)
- Payment Follow-up (with 2 sub-menus)
- Reports
- User Management
- Settings

### 2. Assign Menus to Users

#### Via Django Admin
1. Go to `/admin/`
2. Navigate to **Access control → User menus**
3. Click **Add user menu**
4. Select:
   - **User**: Choose user
   - **Menu**: Choose menu item
   - **Assigned by**: Admin making assignment
   - **Is active**: Check to activate
5. Save

#### Via Django Shell
```python
from django.contrib.auth import get_user_model
from apps.accesscontrol.models import MenuItem, UserMenu

User = get_user_model()

# Get user and admin
user = User.objects.get(email='john@example.com')
admin = User.objects.get(email='admin@example.com')

# Get menus to assign
dashboard = MenuItem.objects.get(code='dashboard')
delivery = MenuItem.objects.get(code='delivery')

# Assign menus
UserMenu.objects.create(user=user, menu=dashboard, assigned_by=admin)
UserMenu.objects.create(user=user, menu=delivery, assigned_by=admin)
```

#### Assign All Top-Level Menus
```python
# Get all parent menus (top-level)
menus = MenuItem.objects.filter(parent=None)

# Assign all to user
for menu in menus:
    UserMenu.objects.create(user=user, menu=menu, assigned_by=admin)
```

## API Usage

### Login API
**Endpoint**: `POST /api/auth/login/` (or `/api/accounts/login/`)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access": "jwt_access_token...",
    "refresh": "jwt_refresh_token...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      ...
    },
    "menus": [
      {
        "id": "uuid-here",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/",
        "order": 1,
        "children": []
      },
      {
        "id": "uuid-here",
        "name": "Delivery Management",
        "code": "delivery",
        "icon": "local_shipping",
        "url": "/delivery",
        "order": 2,
        "children": [
          {
            "id": "uuid-here",
            "name": "Bills",
            "code": "delivery_bills",
            "icon": "receipt",
            "url": "/delivery/bills",
            "order": 1
          },
          ...
        ]
      }
    ]
  }
}
```

### Get User Menus API
**Endpoint**: `GET /api/access/menus/`

**Headers**: `Authorization: Bearer <access_token>`

**Response**:
```json
{
  "status": "success",
  "message": "User menus retrieved successfully",
  "data": {
    "menus": [...],  // Same structure as login
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe"
    }
  }
}
```

## Frontend Integration

### React Example
```jsx
// Login and store menus
const handleLogin = async (email, password) => {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, password})
  });
  
  const data = await response.json();
  
  // Store tokens and menus
  localStorage.setItem('access_token', data.data.access);
  localStorage.setItem('refresh_token', data.data.refresh);
  localStorage.setItem('menus', JSON.stringify(data.data.menus));
  localStorage.setItem('user', JSON.stringify(data.data.user));
  
  // Render navbar
  renderNavbar(data.data.menus);
};

// Navbar component
function Navbar() {
  const menus = JSON.parse(localStorage.getItem('menus') || '[]');
  
  return (
    <nav>
      {menus.map(menu => (
        <NavItem key={menu.id} item={menu} />
      ))}
    </nav>
  );
}

function NavItem({ item }) {
  return (
    <div>
      <Link to={item.url}>
        <i className={`icon-${item.icon}`}></i>
        {item.name}
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

## Database Schema

```sql
-- Menu Items table
CREATE TABLE menu_items (
  id UUID PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  code VARCHAR(50) UNIQUE NOT NULL,
  icon VARCHAR(50),
  url VARCHAR(200) NOT NULL,
  parent_id UUID REFERENCES menu_items(id),
  order INTEGER NOT NULL,
  is_active BOOLEAN NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- User Menu Assignments table
CREATE TABLE user_menus (
  id UUID PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  menu_id UUID NOT NULL REFERENCES menu_items(id),
  assigned_by_id BIGINT REFERENCES users(id),
  assigned_at TIMESTAMP WITH TIME ZONE NOT NULL,
  is_active BOOLEAN NOT NULL,
  UNIQUE (user_id, menu_id)
);
```

## Common Tasks

### View User's Assigned Menus
```python
from apps.accesscontrol.models import UserMenu

# Get user's menus
user_menus = UserMenu.objects.filter(
    user__email='john@example.com',
    is_active=True
).select_related('menu')

for um in user_menus:
    print(f"- {um.menu.name} ({um.menu.url})")
```

### Bulk Assign Menus
```python
from django.contrib.auth import get_user_model
from apps.accesscontrol.models import MenuItem, UserMenu

User = get_user_model()
user = User.objects.get(email='john@example.com')
admin = User.objects.get(email='admin@example.com')

# Assign specific menus by code
menu_codes = ['dashboard', 'delivery', 'purchase']
menus = MenuItem.objects.filter(code__in=menu_codes)

for menu in menus:
    UserMenu.objects.get_or_create(
        user=user,
        menu=menu,
        defaults={'assigned_by': admin}
    )
```

### Remove User's Menu Access
```python
# Deactivate instead of deleting (for audit trail)
UserMenu.objects.filter(
    user__email='john@example.com',
    menu__code='purchase'
).update(is_active=False)

# Or delete completely
UserMenu.objects.filter(
    user__email='john@example.com',
    menu__code='purchase'
).delete()
```

### Add New Menu Item
```python
from apps.accesscontrol.models import MenuItem

# Create new top-level menu
new_menu = MenuItem.objects.create(
    name='Inventory',
    code='inventory',
    icon='inventory',
    url='/inventory',
    order=8,
    is_active=True
)

# Create sub-menu
sub_menu = MenuItem.objects.create(
    name='Stock Levels',
    code='inventory_stock',
    icon='bar_chart',
    url='/inventory/stock',
    parent=new_menu,
    order=1,
    is_active=True
)
```

## Advantages of Direct Assignment

1. **Simplicity**: No role hierarchy to manage
2. **Flexibility**: Each user gets exactly the menus they need
3. **Granular Control**: Admin can add/remove individual menus per user
4. **Easy to Understand**: Clear user → menu relationship
5. **Quick Setup**: No need to define roles first

## Migration from Role-Based System

If you had a role-based system, you can convert it:

```python
from apps.accesscontrol.models import UserMenu, MenuItem
from django.contrib.auth import get_user_model

User = get_user_model()

# Example: Convert "Manager" role users to direct assignments
manager_users = User.objects.filter(roles__contains=['MANAGER'])
manager_menus = MenuItem.objects.filter(
    code__in=['dashboard', 'delivery', 'purchase', 'payment', 'reports']
)

admin = User.objects.get(is_superuser=True)

for user in manager_users:
    for menu in manager_menus:
        UserMenu.objects.get_or_create(
            user=user,
            menu=menu,
            defaults={'assigned_by': admin}
        )
```

## Troubleshooting

### User has no menus after login
**Cause**: No menus assigned to user

**Solution**:
```python
from apps.accesscontrol.models import UserMenu, MenuItem
user = User.objects.get(email='user@example.com')

# Check assignments
print(f"User has {UserMenu.objects.filter(user=user, is_active=True).count()} menus")

# Assign dashboard at minimum
dashboard = MenuItem.objects.get(code='dashboard')
UserMenu.objects.create(user=user, menu=dashboard, assigned_by=admin)
```

### Menus not appearing in correct order
Check the `order` field:
```python
# Update menu order
MenuItem.objects.filter(code='dashboard').update(order=1)
MenuItem.objects.filter(code='delivery').update(order=2)
```

## Summary

✅ **Simple**: No roles, just users and menus  
✅ **Direct**: Assign menus directly to users  
✅ **Flexible**: Each user gets custom menu set  
✅ **API-Ready**: Login returns full menu structure  
✅ **Frontend-Friendly**: Easy to render navbar  

**Key Command**: `python manage.py seed_menus` to get started!
