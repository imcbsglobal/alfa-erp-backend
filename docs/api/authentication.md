# Authentication & User Management API

**Base URL**: `http://localhost:8000/api/auth`  
**Authentication**: JWT Bearer Token (except login endpoints)

---

## 📋 Complete Endpoint List

### Authentication Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/login/` | Login and get JWT tokens | Public |
| POST | `/api/auth/token/refresh/` | Refresh access token | Public |

### User Management Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/auth/users/` | List all users | Admin |
| POST | `/api/auth/users/` | Create new user | Admin |
| GET | `/api/auth/users/{id}/` | Get user by ID | Admin |
| PUT | `/api/auth/users/{id}/` | Update user (full) | Admin |
| PATCH | `/api/auth/users/{id}/` | Update user (partial) | Admin |
| DELETE | `/api/auth/users/{id}/` | Delete user | Admin |
| GET | `/api/auth/users/me/` | Get current user profile | User |
| POST | `/api/auth/users/change_password/` | Change own password | User |
| POST | `/api/auth/users/{id}/activate/` | Activate user account | Admin |
| POST | `/api/auth/users/{id}/deactivate/` | Deactivate user account | Admin |

### Job Title Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/auth/job-titles/` | List all job titles | User |
| POST | `/api/auth/job-titles/` | Create new job title | Admin |
| GET | `/api/auth/job-titles/{id}/` | Get job title by ID | User |
| PUT/PATCH | `/api/auth/job-titles/{id}/` | Update job title | Admin |
| DELETE | `/api/auth/job-titles/{id}/` | Delete job title | Admin |

---

## Authentication Endpoints

### 1. Login

`POST /api/auth/login/`

Authenticate user and obtain JWT tokens with user information and assigned menus.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "admin@gmail.com",
  "password": "admin@123"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "admin@gmail.com",
      "first_name": "Admin",
      "last_name": "User",
      "full_name": "Admin User",
      "avatar": null,
      "role": "ADMIN",
      "department": "Administration",
      "job_title": {
        "id": "job-uuid-456",
        "title": "System Administrator"
      },
      "is_staff": true,
      "is_superuser": true
    },
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

**Error (401 Unauthorized):**
```json
{
  "status": "error",
  "message": "No active account found with the given credentials",
  "status_code": 401
}
```

**Error (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "email": ["This field is required"],
    "password": ["This field is required"]
  },
  "status_code": 400
}
```

---

### 2. Refresh Token
`POST /api/auth/token/refresh/`

Obtain a new access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
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

---

## User Management Endpoints

### 3. List All Users (Admin)
`GET /api/auth/users/`

Get a list of all users in the system.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (default: 10)

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Users retrieved successfully",
  "data": {
    "count": 25,
    "next": "http://localhost:8000/api/auth/users/?page=2",
    "previous": null,
    "results": [
      {
        "id": "uuid-1",
        "email": "admin@gmail.com",
        "first_name": "Admin",
        "last_name": "User",
        "full_name": "Admin User",
        "role": "ADMIN",
        "department": "Administration",
        "job_title": "job-uuid-456",
        "is_active": true,
        "is_staff": true
      },
      {
        "id": "uuid-2",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "phone": "+0987654321",
        "is_active": true,
        "is_staff": false,
        "date_joined": "2025-02-20T14:20:00Z",
        "last_login": "2025-12-02T16:30:00Z"
      }
    ]
  }
}
```

---

### 4. Create User (Admin)
`POST /api/auth/users/`

Create a new user account.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+1122334455",
  "password": "SecurePass123!",
  "is_staff": false,
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "id": 3,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "phone": "+1122334455",
    "avatar": null,
    "roles": [],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-12-03T10:00:00Z",
    "last_login": null
  }
}
```

---

### 5. Get User by ID (Admin)
`GET /api/auth/users/{id}/`

Get detailed information about a specific user.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "id": 2,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+0987654321",
    "avatar": null,
    "roles": ["VIEWER"],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-02-20T14:20:00Z",
    "last_login": "2025-12-02T16:30:00Z"
  }
}
```

---

### 6. Update User (Admin)
`PUT /api/auth/users/{id}/` (Full Update)  
`PATCH /api/auth/users/{id}/` (Partial Update)

Update user information.

**Headers:**
```
Authorization: Bearer {admin_token}
Content-Type: application/json
```

**Request Body (PATCH example):**
```json
{
  "first_name": "Johnny",
  "phone": "+1111111111"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User updated successfully",
  "data": {
    "id": 2,
    "email": "user@example.com",
    "first_name": "Johnny",
    "last_name": "Doe",
    "full_name": "Johnny Doe",
    "phone": "+1111111111",
    "avatar": null,
    "roles": ["VIEWER"],
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-02-20T14:20:00Z",
    "last_login": "2025-12-02T16:30:00Z"
  }
}
```

---

### 7. Delete User (Admin)
`DELETE /api/auth/users/{id}/`

Delete a user account.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User deleted successfully"
}
```

---

### 8. Get Current User Profile
`GET /api/auth/users/me/`

Get the authenticated user's own profile.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "admin@gmail.com",
    "first_name": "Admin",
    "last_name": "User",
    "full_name": "Admin User",
    "phone": "+1234567890",
    "avatar": null,
    "roles": ["ADMIN"],
    "is_active": true,
    "is_staff": true,
    "date_joined": "2025-01-15T10:30:00Z",
    "last_login": "2025-12-03T08:45:00Z"
  }
}
```

---

### 9. Change Password
`POST /api/auth/users/change_password/`

Change the authenticated user's password.

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Password changed successfully"
}
```

**Error (400 Bad Request):**
```json
{
  "status": "error",
  "message": "Password verification failed",
  "errors": {
    "old_password": ["Wrong password"]
  },
  "status_code": 400
}
```

---

### 10. Activate User (Admin)
`POST /api/auth/users/{id}/activate/`

Activate a deactivated user account.

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User user@example.com activated successfully",
  "data": {
    "email": "user@example.com",
    "is_active": true
  }
}
```

---

### 11. Deactivate User (Admin)
`POST /api/auth/users/{id}/deactivate/`

Deactivate a user account (soft delete).

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "User user@example.com deactivated successfully",
  "data": {
    "email": "user@example.com",
    "is_active": false
  }
}
```

---

## Code Examples

### Login and Store Tokens
```javascript
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const result = await response.json();
  
  if (result.status === 'success') {
    localStorage.setItem('access_token', result.data.access);
    localStorage.setItem('refresh_token', result.data.refresh);
    localStorage.setItem('user', JSON.stringify(result.data.user));
    localStorage.setItem('menus', JSON.stringify(result.data.menus));
    return result.data;
  } else {
    throw new Error(result.message);
  }
}
```

### Auto-Refresh Token
```javascript
axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      
      try {
        const response = await axios.post('/api/auth/token/refresh/', {
          refresh: refreshToken
        });
        
        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

### Fetch Current User Profile
```javascript
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/auth/users/me/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const result = await response.json();
  return result.data;
}
```

### Create New User (Admin)
```python
import requests

admin_token = "your_admin_access_token"

headers = {
    'Authorization': f'Bearer {admin_token}',
    'Content-Type': 'application/json'
}

new_user_data = {
    'email': 'newuser@example.com',
    'first_name': 'Jane',
    'last_name': 'Smith',
    'phone': '+1122334455',
    'password': 'SecurePass123!',
    'is_staff': False,
    'is_active': True
}

response = requests.post(
    'http://localhost:8000/api/auth/users/',
    headers=headers,
    json=new_user_data
)

if response.status_code == 201:
    user = response.json()['data']
    print(f"Created user: {user['email']}")
```

---

## Notes

- **Access Token**: Expires in 1 hour
- **Refresh Token**: Expires in 7 days
- **Menus**: Automatically included in login response based on user assignments
- **Admin Endpoints**: Require `is_staff=True`
- **User Must Be Active**: `is_active=True` required for login
- **Password Requirements**: Minimum 8 characters (configurable)
- **Pagination**: Default page size is 10 items

---

## Related Documentation

- [User Management API](./users.md) - User CRUD operations
- [Response Format Guide](../response_handlers.md) - Standard response structure
