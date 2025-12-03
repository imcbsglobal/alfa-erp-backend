# Menu-Based Role Access Control (RBAC) Implementation

## Overview
Implemented a simplified menu-based RBAC system for ALFA ERP where users are assigned roles, roles have menu items, and the login API returns the menu structure for the frontend to render.

## Architecture

```
User → UserRole → Role → MenuItem
```

### Data Flow
1. **Backend Seeds Menus**: Management command creates menu hierarchy
2. **Roles Get Menus**: Roles are assigned specific menu items
3. **User Gets Role**: Admin assigns a role to user (with `is_primary` flag)
4. **Login Returns Menus**: JWT token response includes menu structure
5. **Frontend Renders**: Frontend displays only the menus user has access to

## Database Schema

### MenuItem Model
```python
- id (primary key)
- label (string) - Display text for menu
- path (string, nullable) - Route path
- icon (string, nullable) - Icon name/class
- order (integer) - Display order
- parent (foreign key to self, nullable) - For nested menus
- is_active (boolean) - Menu visibility
```

### Role Model
```python
- id (primary key)
- name (string) - Role display name
- code (string, unique) - Role identifier (ADMIN, MANAGER, etc.)
- description (text)
- menus (many-to-many to MenuItem) - Assigned menu items
- is_active (boolean)
```

### UserRole Model
```python
- id (primary key)
- user (foreign key to User)
- role (foreign key to Role)
- is_primary (boolean) - Primary role used for login menus
- assigned_by (foreign key to User)
- assigned_at (datetime)
```

## Seeded Roles & Menus

### Roles Created
1. **ADMIN** - Full system access (16 menus)
2. **MANAGER** - Management oversight (14 menus)
3. **PICKER** - Warehouse picking tasks (4 menus)
4. **PACKER** - Packing operations (3 menus)
5. **DELIVERY** - Delivery management (3 menus)
6. **PURCHASE** - Purchase operations (5 menus)
7. **ACCOUNTS** - Payment & accounting (4 menus)

### Menu Hierarchy
```
📁 Dashboard (/)
📁 Delivery Management (/delivery)
   └─ Bills (/delivery/bills)
   └─ Picking (/delivery/picking)
   └─ Packing (/delivery/packing)
   └─ Delivery Tasks (/delivery/tasks)
📁 Purchase Management (/purchase)
   └─ Orders (/purchase/orders)
   └─ Vendors (/purchase/vendors)
   └─ Invoices (/purchase/invoices)
📁 Payment Follow-up (/payment)
   └─ Outstanding (/payment/outstanding)
   └─ Follow-ups (/payment/followups)
📁 Reports (/reports)
📁 User Management (/users)
📁 Settings (/settings)
```

## API Implementation

### Login Endpoint
**Endpoint**: `POST /api/auth/login/` (or `/api/accounts/login/`)

**Request**:
```json
{
  "email": "admin@gmail.com",
  "password": "admin123"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhb...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhb...",
    "user": {
      "id": 1,
      "email": "admin@gmail.com",
      "first_name": "Admin",
      "last_name": "User",
      "full_name": "Admin User",
      "avatar": null,
      "roles": ["ADMIN"],
      "primary_role": "ADMIN",
      "is_staff": true,
      "is_superuser": true,
      "groups": []
    },
    "menus": [
      {
        "id": 1,
        "label": "Dashboard",
        "path": "/",
        "icon": "dashboard",
        "order": 1,
        "children": []
      },
      {
        "id": 2,
        "label": "Delivery Management",
        "path": "/delivery",
        "icon": "local_shipping",
        "order": 2,
        "children": [
          {
            "id": 3,
            "label": "Bills",
            "path": "/delivery/bills",
            "icon": "receipt",
            "order": 1,
            "children": []
          },
          {
            "id": 4,
            "label": "Picking",
            "path": "/delivery/picking",
            "icon": "inventory",
            "order": 2,
            "children": []
          }
        ]
      }
    ],
    "role": {
      "id": 1,
      "name": "Administrator",
      "code": "ADMIN",
      "description": "Full system access with all privileges"
    }
  }
}
```

### Get User Menus Endpoint
**Endpoint**: `GET /api/access/menus/`

**Headers**: `Authorization: Bearer <access_token>`

**Response**:
```json
{
  "status": "success",
  "data": {
    "menus": [...],
    "role": {
      "id": 1,
      "name": "Administrator",
      "code": "ADMIN"
    }
  }
}
```

## Management Commands

### Seed Menus & Roles
```bash
python manage.py seed_menus
```

**What it does**:
- Creates all menu items in hierarchy
- Creates 7 default roles
- Assigns appropriate menus to each role
- Idempotent (can be run multiple times safely)

**Output**:
```
Starting menu and role seeding...
Creating menu items...
  ✓ Dashboard menu created
  ✓ Delivery Management menus created
  ...
Creating roles...
  ✓ Created 7 roles
Assigning menus to roles...
  ✓ Admin: 16 menus assigned
  ...
✓ Menu and role seeding completed successfully!
```

## Assigning Roles to Users

### Via Django Shell
```python
from django.contrib.auth import get_user_model
from apps.accesscontrol.models import Role, UserRole

User = get_user_model()

# Get user and role
user = User.objects.get(email='john@example.com')
role = Role.objects.get(code='MANAGER')
admin = User.objects.get(email='admin@example.com')

# Assign role as primary
UserRole.objects.create(
    user=user,
    role=role,
    is_primary=True,
    assigned_by=admin
)
```

### Via Django Admin
1. Navigate to `/admin/`
2. Go to **Access control → User roles**
3. Click **Add user role**
4. Select user, role, and mark as primary
5. Save

## Frontend Integration

### Login Flow
```javascript
// 1. Login request
const response = await axios.post('/api/auth/login/', {
  email: 'admin@gmail.com',
  password: 'admin123'
});

// 2. Extract data
const { access, refresh, user, menus, role } = response.data.data;

// 3. Store tokens
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);

// 4. Store user data
localStorage.setItem('user', JSON.stringify(user));
localStorage.setItem('menus', JSON.stringify(menus));
localStorage.setItem('role', JSON.stringify(role));

// 5. Render navbar based on menus
renderNavbar(menus);
```

### Navbar Component Example (React)
```jsx
function Navbar({ menus }) {
  return (
    <nav>
      {menus.map(menu => (
        <MenuItem key={menu.id} item={menu} />
      ))}
    </nav>
  );
}

function MenuItem({ item }) {
  return (
    <div className="menu-item">
      <Link to={item.path}>
        <i className="material-icons">{item.icon}</i>
        <span>{item.label}</span>
      </Link>
      {item.children && item.children.length > 0 && (
        <div className="submenu">
          {item.children.map(child => (
            <MenuItem key={child.id} item={child} />
          ))}
        </div>
      )}
    </div>
  );
}
```

## File Structure

```
apps/
├── accesscontrol/
│   ├── __init__.py
│   ├── admin.py              # Django admin interface
│   ├── apps.py               # App configuration
│   ├── models.py             # MenuItem, Role, UserRole models
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # API routes
│   ├── views.py              # API views (UserMenuView)
│   ├── management/
│   │   └── commands/
│   │       └── seed_menus.py # Seeding command
│   └── migrations/
│       └── 0001_initial.py
│
└── accounts/
    ├── serializers.py        # Updated CustomTokenObtainPairSerializer
    └── ...
```

## Testing

### Test Users
```bash
# Create test users
python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.accesscontrol.models import Role, UserRole

User = get_user_model()

# Create users if they don't exist
admin, _ = User.objects.get_or_create(
    email='admin@gmail.com',
    defaults={'is_staff': True, 'is_superuser': True}
)
admin.set_password('admin123')
admin.save()

test_user, _ = User.objects.get_or_create(email='test@gmail.com')
test_user.set_password('test123')
test_user.save()

# Assign roles
admin_role = Role.objects.get(code='ADMIN')
manager_role = Role.objects.get(code='MANAGER')

UserRole.objects.get_or_create(
    user=admin,
    role=admin_role,
    defaults={'is_primary': True, 'assigned_by': admin}
)

UserRole.objects.get_or_create(
    user=test_user,
    role=manager_role,
    defaults={'is_primary': True, 'assigned_by': admin}
)

print('✓ Test users created and roles assigned')
"
```

### Test Login
```bash
# Using curl
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmail.com","password":"admin123"}'

# Or use the test script
python scripts/test_login_menus.py
```

## Security Considerations

1. **Role Validation**: Only users with `is_primary=True` role get menus on login
2. **Menu Hiding**: Frontend only renders menus returned by backend
3. **API Protection**: All menu-related endpoints require authentication
4. **Admin Only**: Only admins can assign/modify roles via Django admin
5. **Audit Trail**: UserRole tracks who assigned the role and when

## Future Enhancements

1. **Multiple Roles**: User can have multiple roles, switch between them
2. **Dynamic Menus**: Add/edit menus via admin panel without code changes
3. **Permissions**: Add fine-grained permissions (view, create, edit, delete) per menu
4. **Menu Metadata**: Add custom metadata (badge counts, tooltips, etc.)
5. **Role Hierarchy**: Implement role inheritance (Manager inherits from User)
6. **Temporary Access**: Time-limited role assignments

## Troubleshooting

### User has no menus after login
**Cause**: User doesn't have a primary role assigned

**Solution**:
```python
from apps.accesscontrol.models import Role, UserRole
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='user@example.com')
role = Role.objects.get(code='MANAGER')
admin = User.objects.get(is_superuser=True)

UserRole.objects.create(
    user=user,
    role=role,
    is_primary=True,
    assigned_by=admin
)
```

### Menus not appearing in navbar
**Check**:
1. Role has menus assigned: `role.menus.count()`
2. Menus are active: `role.menus.filter(is_active=True).count()`
3. Frontend correctly parses JSON response
4. MenuItem order is correct

### Need to reset menus
```bash
# Delete all menu data
python manage.py shell -c "
from apps.accesscontrol.models import MenuItem, Role, UserRole
UserRole.objects.all().delete()
Role.objects.all().delete()
MenuItem.objects.all().delete()
print('✓ All menu data deleted')
"

# Re-seed
python manage.py seed_menus
```

## Summary

✅ Menu-based RBAC system implemented  
✅ 7 roles created with appropriate menu assignments  
✅ Login API returns menu structure  
✅ Separate endpoint for fetching menus (`/api/access/menus/`)  
✅ Django admin interface for managing roles and assignments  
✅ Seed command for initial setup  
✅ Test users with roles assigned  

The system is now ready for frontend integration. The frontend should:
1. Call login API
2. Extract `menus` from response
3. Render navbar based on menu structure
4. Store menus in state/context for navigation
