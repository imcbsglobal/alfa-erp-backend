# Role-Based Access Control (RBAC)

## Overview
The User model now includes a `role` field that controls access to different parts of the application based on the user's assigned role.

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
class Role(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    STORE = 'STORE', 'Store'
    DELIVERY = 'DELIVERY', 'Delivery'
    PURCHASE = 'PURCHASE', 'Purchase'
    ACCOUNTS = 'ACCOUNTS', 'Accounts'
    VIEWER = 'VIEWER', 'Viewer'

role = models.CharField(
    max_length=20,
    choices=Role.choices,
    default=Role.VIEWER,
    help_text='User role for access control'
)
```

### Login Response
When a user logs in, the response includes the `role` field:

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
    "role": "ADMIN",
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
Use the role from the login response to display the appropriate menu:

```javascript
const role = user.role; // from backend login response

const menuToShow = sidebarMenu[role];

return (
  <Sidebar>
    {menuToShow.map(item => (
      <Link key={item.path} to={item.path}>{item.label}</Link>
    ))}
  </Sidebar>
);
```

### Protected Routes
You can also use the role to protect routes:

```javascript
const ProtectedRoute = ({ allowedRoles, children }) => {
  const user = useAuth(); // Get user from context/store
  
  if (!allowedRoles.includes(user.role)) {
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
```

## Database Migration

Run the following commands to apply the migration:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Admin Interface

The role field is now visible and editable in the Django Admin:
- List view shows the role column
- Filter by role available
- Role can be set when creating or editing users

## API Endpoints

### Get Current User
```
GET /api/accounts/me/
```
Returns the current user's information including the `role` field.

### Update User
```
PATCH /api/accounts/users/{id}/
```
Admin can update user roles via this endpoint.

## Security Considerations

1. **Backend Validation**: Always validate permissions on the backend. Frontend role checks are for UX only.
2. **API Endpoints**: Protect API endpoints with role-based permissions.
3. **Default Role**: New users are assigned the `VIEWER` role by default (least privilege).
4. **Role Changes**: Only admins should be able to change user roles.

## Testing

Test different user roles by:
1. Creating users with different roles in Django Admin
2. Logging in with each user
3. Verifying the correct menu items and access rights

## Future Enhancements

Consider implementing:
- Role hierarchy (ADMIN inherits all permissions)
- Custom permissions per role
- Department-based access control
- Time-based access restrictions
