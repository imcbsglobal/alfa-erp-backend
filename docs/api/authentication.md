# Authentication API

Complete API documentation for authentication endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.onrender.com`

---

## Login

Authenticate user and obtain JWT tokens with user information.

### Endpoint

```
POST /api/auth/login/
```

### Authentication

Not required (public endpoint)

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "admin@gmail.com",
  "password": "admin@123"
}
```

**Alternative (also supported):**
```json
{
  "email": "admin@gmail.com",
  "password": "admin@123"
}
```

**Fields:**
- `username` (string, required): User's email address
- `password` (string, required): User's password
- Note: Both `username` and `email` keys are accepted for the email field

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Login successful",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "admin@gmail.com",
      "first_name": "Admin",
      "last_name": "User",
      "full_name": "Admin User",
      "avatar": "http://localhost:8000/media/avatars/2025/12/01/photo.jpg",
      "is_staff": true,
      "is_superuser": true,
      "roles": ["Admin", "Manager"]
    }
  }
}
```

**Response Fields:**
- `success` (boolean): Always `true` for successful requests
- `status_code` (integer): HTTP status code (200)
- `message` (string): Human-readable success message
- `data` (object): Response payload
  - `access` (string): JWT access token (expires in 1 hour)
  - `refresh` (string): JWT refresh token (expires in 7 days)
  - `user` (object): Authenticated user information
    - `id` (integer): User ID
    - `email` (string): User's email
    - `first_name` (string): First name
    - `last_name` (string): Last name
    - `full_name` (string): Combined full name
    - `avatar` (string|null): Avatar image URL or null
    - `is_staff` (boolean): Admin/staff status
    - `is_superuser` (boolean): Superuser status
    - `roles` (array): List of role names from Django groups

**Error (401 Unauthorized):**
```json
{
  "success": false,
  "status_code": 401,
  "message": "Authentication failed",
  "errors": {
    "detail": "No active account found with the given credentials"
  }
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation failed",
  "errors": {
    "username": ["This field is required"],
    "password": ["This field is required"]
  }
}
```

### Usage Examples

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@gmail.com", "password":"admin@123"}'
```

**HTTPie:**
```bash
http POST http://localhost:8000/api/auth/login/ \
  username=admin@gmail.com \
  password=admin@123
```

**JavaScript (Fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin@gmail.com',
    password: 'admin@123'
  })
});

const result = await response.json();

if (result.success) {
  // Store tokens securely
  localStorage.setItem('access_token', result.data.access);
  localStorage.setItem('refresh_token', result.data.refresh);
  
  // Use user data for UI
  console.log('User roles:', result.data.user.roles);
  console.log('Avatar:', result.data.user.avatar);
}
```

**Python (requests):**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/auth/login/',
    json={
        'username': 'admin@gmail.com',
        'password': 'admin@123'
    }
)

data = response.json()
if data['success']:
    access_token = data['data']['access']
    user = data['data']['user']
```

### Notes

- Both `username` and `email` field names are accepted (both map to email internally)
- Access tokens expire after 1 hour (configurable in settings)
- Refresh tokens expire after 7 days (configurable in settings)
- Use access token in `Authorization: Bearer <token>` header for protected endpoints
- Tokens are rotated on refresh for security
- User must have `is_active=True` to login
- Roles are derived from Django `Group` memberships
- Avatar URL is absolute and includes media domain

---

## Refresh Token

Obtain a new access token using a valid refresh token.

### Endpoint

```
POST /api/auth/token/refresh/
```

### Authentication

Not required (uses refresh token)

### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Fields:**
- `refresh` (string, required): Valid refresh token from login

### Response

**Success (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

### Usage Example

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<your-refresh-token>"}'
```

**JavaScript:**
```javascript
const refreshToken = localStorage.getItem('refresh_token');

const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
});

const result = await response.json();
if (response.ok) {
  localStorage.setItem('access_token', result.access);
}
```

### Notes

- Refresh tokens are single-use when `ROTATE_REFRESH_TOKENS=True` (default)
- Old refresh token becomes invalid after successful refresh
- New refresh token is returned in response when rotation is enabled
- Implement auto-refresh logic in frontend before access token expires

---

## Related Documentation

- [User Management API](./users.md) - User CRUD operations
- [Response Format Guide](../response_handlers.md) - Standard response structure
