# Menu Access Control System

Complete role-based menu control system for ALFA ERP. Users are assigned menus directly; ADMIN/SUPERADMIN users automatically get all menus.

## Overview

- **Direct User-to-Menu Assignment**: Each user can be assigned specific menu items
- **Role-Based Auto-Access**: Users with role `ADMIN` or `SUPERADMIN` (or Django `is_staff`/`is_superuser`) automatically get all menus
- **Hierarchical Structure**: Menus can have parent-child relationships (nested menus)
- **Real-time Integration**: Menu assignments are returned in login response

## Models

### MenuItem
Represents individual navigation menu items.

Fields:
- `id` (UUID): Primary key
- `name`: Display name (e.g., "Dashboard", "User Management")
- `code`: Unique code (e.g., "dashboard", "user_management")
- `icon`: Icon identifier (e.g., "dashboard", "people")
- `url`: Frontend route (e.g., "/dashboard", "/users")
- `parent`: Optional parent MenuItem for nested menus
- `order`: Display order (lower appears first)
- `is_active`: Whether menu is currently active

### UserMenu (Through Model)
Links users to menu items.

Fields:
- `id` (UUID): Primary key
- `user`: Foreign key to User
- `menu`: Foreign key to MenuItem
- `assigned_by`: Admin who assigned the menu
- `assigned_at`: Timestamp of assignment
- `is_active`: Whether assignment is active

## Login Flow

When a user logs in via `POST /api/auth/login/`, the response includes:

```json
{
  "success": true,
  "data": {
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "User Name",
      "role": "PICKER",
      "is_staff": false,
      "is_superuser": false
    },
    "menus": [
      {
        "id": "menu_uuid",
        "name": "Delivery Management",
        "code": "delivery_management",
        "icon": "local_shipping",
        "url": "/delivery",
        "order": 4,
        "children": [
          {
            "id": "child_uuid",
            "name": "Picking",
            "code": "delivery_picking",
            "icon": "inventory",
            "url": "/delivery/picking",
            "order": 1
          }
        ]
      }
    ]
  }
}
```

### Menu Logic
- If `user.is_admin_or_superadmin()` returns `True` → all menus are returned
- Otherwise → only menus assigned via `UserMenu` are returned

## API Endpoints

### User Endpoints

#### GET /api/access-control/menus/
Get menus for the authenticated user.

**Auth**: Required (JWT)

**Response**:
```json
{
  "success": true,
  "data": {
    "menus": [...],
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "User Name"
    }
  }
}
```

### Admin Endpoints (IsAdminUser required)

#### GET /api/access-control/admin/menus/
Get all available menu items (hierarchical structure).

**Auth**: Admin required

**Response**:
```json
{
  "success": true,
  "data": {
    "menus": [
      {
        "id": "uuid",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "dashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      }
    ]
  }
}
```

#### POST /api/access-control/admin/assign-menus/
Assign menus to a user.

**Auth**: Admin required

**Request**:
```json
{
  "user_id": "user_uuid",
  "menu_ids": ["menu_uuid_1", "menu_uuid_2"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "User Name"
    },
    "assigned": [
      {
        "id": "assignment_uuid",
        "menu_id": "menu_uuid_1",
        "menu_name": "Dashboard",
        "menu_code": "dashboard"
      }
    ],
    "skipped": [],
    "total_assigned": 1,
    "total_skipped": 0
  },
  "message": "Successfully assigned 1 menu(s) to user@example.com"
}
```

#### POST /api/access-control/admin/unassign-menus/
Remove menu assignments from a user.

**Auth**: Admin required

**Request**:
```json
{
  "user_id": "user_uuid",
  "menu_ids": ["menu_uuid_1"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "user": {...},
    "unassigned": [
      {
        "menu_id": "menu_uuid_1",
        "menu_name": "Dashboard"
      }
    ],
    "not_found": [],
    "total_unassigned": 1,
    "total_not_found": 0
  }
}
```

#### GET /api/access-control/admin/users/{user_id}/menus/
Get all menu assignments for a specific user.

**Auth**: Admin required

**Response**:
```json
{
  "success": true,
  "data": {
    "user": {...},
    "assignments": [
      {
        "id": "assignment_uuid",
        "menu": {
          "id": "menu_uuid",
          "name": "Dashboard",
          "code": "dashboard"
        },
        "assigned_by": "admin@example.com",
        "assigned_at": "2025-12-15T10:30:00Z",
        "is_active": true
      }
    ],
    "menu_structure": [...],
    "total_menus": 5
  }
}
```

## Role-Based Access

### Automatic Full Access
Users with any of these conditions get **all menus**:
- `role = 'ADMIN'`
- `role = 'SUPERADMIN'`
- `is_staff = True`
- `is_superuser = True`

Check implemented via `User.is_admin_or_superadmin()` helper method.

### Restricted Access
Users with operational roles (PICKER, PACKER, DRIVER, BILLING, USER) receive only menus assigned via `UserMenu`.

## Usage Examples

### 1. Assign Menus to a Picker

As admin:
```bash
POST /api/access-control/admin/assign-menus/
{
  "user_id": "picker_user_uuid",
  "menu_ids": [
    "delivery_management_uuid",
    "delivery_picking_uuid"
  ]
}
```

### 2. Check User's Current Menus

As admin:
```bash
GET /api/access-control/admin/users/{picker_user_uuid}/menus/
```

### 3. Remove Menu Access

```bash
POST /api/access-control/admin/unassign-menus/
{
  "user_id": "picker_user_uuid",
  "menu_ids": ["delivery_picking_uuid"]
}
```

## Frontend Integration

### On Login
1. Call `POST /api/auth/login/` with credentials
2. Store `access` and `refresh` tokens
3. Store `user` object in auth context/store
4. Store `menus` array in navigation state
5. Render navigation based on `menus` array

### Route Protection
Frontend should:
- Hide/disable navigation items not in `menus` array
- Implement `ProtectedRoute` that checks if user has access to the route based on `menus`
- Redirect unauthorized access to 403 page

### Example React Implementation

```jsx
// AuthContext.jsx
const [menus, setMenus] = useState([]);

const login = async (credentials) => {
  const response = await api.post('/auth/login/', credentials);
  const { access, refresh, user, menus } = response.data.data;
  
  // Store tokens and user
  localStorage.setItem('accessToken', access);
  localStorage.setItem('refreshToken', refresh);
  setUser(user);
  setMenus(menus);
};

// Navigation.jsx
const Navigation = () => {
  const { menus } = useAuth();
  
  return (
    <nav>
      {menus.map(menu => (
        <NavItem key={menu.id} menu={menu} />
      ))}
    </nav>
  );
};

// ProtectedRoute.jsx
const ProtectedRoute = ({ path, children }) => {
  const { menus } = useAuth();
  const hasAccess = menus.some(m => 
    m.url === path || m.children?.some(c => c.url === path)
  );
  
  if (!hasAccess) return <Navigate to="/403" />;
  return children;
};
```

## Database Setup

Menus are created via Django admin or management commands. Example:

```python
# Create root menu
dashboard = MenuItem.objects.create(
    name="Dashboard",
    code="dashboard",
    icon="dashboard",
    url="/dashboard",
    order=1,
    is_active=True
)

# Create nested menu
user_mgmt = MenuItem.objects.create(
    name="User Management",
    code="user_management",
    icon="people",
    url="/users",
    order=2,
    is_active=True
)

user_list = MenuItem.objects.create(
    name="User List",
    code="user_list",
    icon="list",
    url="/users/list",
    parent=user_mgmt,
    order=1,
    is_active=True
)

# Assign to user
from apps.accounts.models import User
user = User.objects.get(email="picker@example.com")
UserMenu.objects.create(
    user=user,
    menu=dashboard,
    assigned_by=admin_user,
    is_active=True
)
```

## Security Notes

1. **Backend Enforcement**: Always validate permissions server-side on each API endpoint. Do not rely solely on frontend menu hiding.
2. **Token Expiry**: Menus are embedded in login response but not in JWT. When token expires, user must re-login to get updated menus.
3. **Real-time Updates**: If you need live menu updates (e.g., admin revokes access while user is logged in), implement WebSocket/SSE notifications or periodically refetch menus via `/api/access-control/menus/`.

## Testing

### Test ADMIN gets all menus
```bash
# Login as ADMIN
POST /api/auth/login/
{
  "email": "admin@example.com",
  "password": "password"
}

# Response should include all menus in data.menus
```

### Test PICKER gets only assigned menus
```bash
# 1. Assign specific menus to picker
POST /api/access-control/admin/assign-menus/
{
  "user_id": "picker_uuid",
  "menu_ids": ["delivery_picking_uuid"]
}

# 2. Login as picker
POST /api/auth/login/
{
  "email": "picker@example.com",
  "password": "password"
}

# Response data.menus should contain only assigned menus
```

## Next Steps & Enhancements

1. **Feature Flags**: Add `feature_flag` field to MenuItem to toggle menus based on environment/subscription tier
2. **Permissions Granularity**: Add CRUD permissions per menu (view, create, edit, delete)
3. **Multi-Role Support**: If users need multiple roles, convert `User.role` to ManyToMany with a `UserRole` model
4. **Audit Logging**: Track menu assignment/unassignment changes for compliance
5. **Batch Operations**: Add bulk assign/unassign endpoints
6. **Menu Analytics**: Track which menus are most/least used per role

## Troubleshooting

**Issue**: User not seeing assigned menus after assignment

**Solution**: User must re-login. Menus are loaded during authentication, not from token. Implement menu refresh endpoint or SSE updates if immediate reflection is required.

---

**Issue**: ADMIN seeing empty menus

**Solution**: Check that `MenuItem.get_all_menu_structure()` returns data. Ensure menus exist in database and `is_active=True`.

---

**Issue**: Frontend 404 on protected route

**Solution**: Ensure frontend route protection checks both parent and child menu URLs. A user might have parent access but not child, or vice versa depending on assignment strategy.
