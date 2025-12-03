# Role-Based Access Control (RBAC)

## Overview
The User model now includes a `roles` field (array) that allows users to have **multiple roles** for flexible access control across different parts of the application.

## Available Roles

### ADMIN
Full access to all features:
- Dashboard
- Delivery
- Purchase
- Payments
- Users Management

### STORE
Access to store-related features:
- Dashboard
- Delivery

### DELIVERY
Access to delivery operations:
- Dashboard
- Delivery

### PURCHASE
Access to purchase management:
- Dashboard
- Purchase

### ACCOUNTS
Access to financial operations:
- Dashboard
- Payments

### VIEWER
Read-only access (default role):
- Dashboard only

## Backend Implementation

### Model
The `User` model in `apps/accounts/models.py` includes:

```python
from django.contrib.postgres.fields import ArrayField

class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    STORE = 'STORE', 'Store'
    DELIVERY = 'DELIVERY', 'Delivery'
    PURCHASE = 'PURCHASE', 'Purchase'
    ACCOUNTS = 'ACCOUNTS', 'Accounts'
    VIEWER = 'VIEWER', 'Viewer'

roles = ArrayField(
    models.CharField(max_length=20, choices=Role.choices),
    default=list,
    blank=True,
    help_text='List of roles assigned to the user for access control'
)

# Helper methods
def has_role(self, role):
    """Check if user has a specific role"""
    return role in self.roles

def has_any_role(self, *roles):
    """Check if user has any of the specified roles"""
    return any(role in self.roles for role in roles)

@property
def primary_role(self):
    """Return the first/primary role or VIEWER if no roles assigned"""
    return self.roles[0] if self.roles else self.Role.VIEWER
```

### Login Response
When a user logs in, the response includes the `roles` array and `primary_role`:

```json
{
  "access": "...",
  "refresh": "...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "avatar": null,
    "roles": ["ADMIN", "ACCOUNTS"],
    "primary_role": "ADMIN",
    "is_staff": true,
    "is_superuser": false
  }
}
```

## Frontend Implementation

### Sidebar Menu Configuration
Define the sidebar menu for each role in your frontend:

```javascript
const sidebarMenu = {
  ADMIN: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Delivery", path: "/delivery" },
    { label: "Purchase", path: "/purchase" },
    { label: "Payments", path: "/payments" },
    { label: "Users", path: "/users" },
  ],

  STORE: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Delivery", path: "/delivery" },
  ],

  DELIVERY: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Delivery", path: "/delivery" },
  ],

  PURCHASE: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Purchase", path: "/purchase" },
  ],

  ACCOUNTS: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Payments", path: "/payments" },
  ],

  VIEWER: [
    { label: "Dashboard", path: "/dashboard" },
  ],
};
```

### Usage in Components
Use the roles array to build a combined menu or use the primary role:

**Option 1: Use primary role for main menu**
```javascript
const primaryRole = user.primary_role; // from backend login response

const menuToShow = sidebarMenu[primaryRole];

return (
  <Sidebar>
    {menuToShow.map(item => (
      <Link key={item.path} to={item.path}>{item.label}</Link>
    ))}
  </Sidebar>
);
```

**Option 2: Combine menus from all roles (no duplicates)**
```javascript
const userRoles = user.roles; // ["ADMIN", "ACCOUNTS"] from backend

// Combine all menu items from all roles
const allMenuItems = userRoles.flatMap(role => sidebarMenu[role] || []);

// Remove duplicates based on path
const uniqueMenuItems = Array.from(
  new Map(allMenuItems.map(item => [item.path, item])).values()
);

return (
  <Sidebar>
    {uniqueMenuItems.map(item => (
      <Link key={item.path} to={item.path}>{item.label}</Link>
    ))}
  </Sidebar>
);
```

### Protected Routes
You can also use the roles array to protect routes:

```javascript
const ProtectedRoute = ({ allowedRoles, children }) => {
  const user = useAuth(); // Get user from context/store
  
  // Check if user has any of the allowed roles
  const hasAccess = user.roles.some(role => allowedRoles.includes(role));
  
  if (!hasAccess) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
};

// Usage
<Route 
  path="/users" 
  element={
    <ProtectedRoute allowedRoles={['ADMIN']}>
      <UsersPage />
    </ProtectedRoute>
  } 
/>

<Route 
  path="/payments" 
  element={
    <ProtectedRoute allowedRoles={['ADMIN', 'ACCOUNTS']}>
      <PaymentsPage />
    </ProtectedRoute>
  } 
/>
```

## Database Migration

Run the following commands to apply the migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Admin Interface

The roles field is now visible and editable in the Django Admin:
- List view shows roles as comma-separated values
- Multiple roles can be assigned using Django admin's array widget
- Roles can be set when creating or editing users

## API Endpoints

### Get Current User
```
GET /api/accounts/me/
```
Returns the current user's information including the `roles` array and `primary_role`.

### Update User
```
PATCH /api/accounts/users/{id}/
```
Admins can update user roles via this endpoint by sending a `roles` array.

## Security Considerations

1. **Backend Validation**: Always validate permissions on the backend. Frontend role checks are for UX only.
2. **API Endpoints**: Protect API endpoints with role-based permissions using the helper methods (`has_role`, `has_any_role`).
3. **Default Roles**: New users can be assigned an empty roles array or default roles as needed.
4. **Role Changes**: Only admins should be able to change user roles.

## Testing

Test multiple user roles by:
1. Creating users with single or multiple roles in Django Admin
2. Logging in with each user
3. Verifying the correct combined menu items and access rights
4. Testing users with multiple roles to ensure proper access to all assigned areas

## Future Enhancements

Consider implementing:
- Role hierarchy (ADMIN inherits all permissions)
- Custom permissions per role
- Department-based access control
- Time-based access restrictions
