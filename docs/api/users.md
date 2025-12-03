# User Management API

Complete API documentation for user management endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.onrender.com`

**Authentication Required:** All endpoints require JWT authentication unless noted otherwise.

**Authorization Header:**
```
Authorization: Bearer <access_token>
```

---

## List Users

Get paginated list of users. **Admin only**.

### Endpoint

```
GET /api/auth/users/
```

### Authentication

Required (Admin/Staff only)

### Query Parameters

- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20, max: 100)
- `search` (string, optional): Search by email, first_name, last_name
- `ordering` (string, optional): Order by field (prefix with `-` for descending)
  - Examples: `email`, `-date_joined`, `first_name`

### Request Example

```
GET /api/auth/users/?page=1&search=john&ordering=-date_joined
Authorization: Bearer <access_token>
```

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "List retrieved successfully",
  "data": {
    "count": 25,
    "next": "http://localhost:8000/api/auth/users/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "is_active": true,
        "is_staff": false
      },
      {
        "id": 2,
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "full_name": "Jane Smith",
        "is_active": true,
        "is_staff": true
      }
    ]
  }
}
```

**Error (403 Forbidden):**
```json
{
  "success": false,
  "status_code": 403,
  "message": "You do not have permission to perform this action"
}
```

### Usage Examples

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/auth/users/?page=1&search=john" \
  -H "Authorization: Bearer <access_token>"
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/api/auth/users/?page=1', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const result = await response.json();
if (result.success) {
  const users = result.data.results;
  console.log('Total users:', result.data.count);
}
```

---

## Get Current User Profile

Get authenticated user's own profile.

### Endpoint

```
GET /api/auth/users/me/
```

### Authentication

Required (Any authenticated user)

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "avatar": "http://localhost:8000/media/avatars/2025/12/01/photo.jpg",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-01-15T08:00:00Z",
    "last_login": "2025-12-02T10:00:00Z"
  }
}
```

### Usage Example

**cURL:**
```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

**JavaScript:**
```javascript
const response = await fetch('http://localhost:8000/api/auth/users/me/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

const result = await response.json();
if (result.success) {
  const profile = result.data;
  console.log('Current user:', profile.email);
}
```

---

## Get User by ID

Get specific user details. Admins can view any user, regular users only themselves.

### Endpoint

```
GET /api/auth/users/{id}/
```

### Authentication

Required

### Path Parameters

- `id` (integer, required): User ID

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Detail retrieved successfully",
  "data": {
    "id": 5,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "avatar": null,
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-01-15T08:00:00Z",
    "last_login": "2025-12-01T14:30:00Z"
  }
}
```

**Error (404 Not Found):**
```json
{
  "success": false,
  "status_code": 404,
  "message": "Not found"
}
```

---

## Create User

Create new user account. **Admin only**.

### Endpoint

```
POST /api/auth/users/
```

### Authentication

Required (Admin/Staff only)

### Request

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+9876543210",
  "is_staff": false,
  "is_active": true
}
```

**Fields:**
- `email` (string, required): User's email (must be unique)
- `password` (string, required): User's password (min 8 characters)
- `first_name` (string, optional): First name
- `last_name` (string, optional): Last name
- `phone` (string, optional): Phone number
- `is_staff` (boolean, optional): Admin status (default: false)
- `is_active` (boolean, optional): Active status (default: true)

### Response

**Success (201 Created):**
```json
{
  "success": true,
  "status_code": 201,
  "message": "Resource created successfully",
  "data": {
    "id": 10,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "full_name": "Jane Smith",
    "phone": "+9876543210",
    "avatar": null,
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-12-02T11:00:00Z",
    "last_login": null
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
    "email": ["User with this email already exists"],
    "password": ["This password is too short. It must contain at least 8 characters."]
  }
}
```

### Usage Example

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

---

## Update User

Update user details. **Admin can update any user**, regular users can update themselves.

### Endpoint

```
PUT /api/auth/users/{id}/
PATCH /api/auth/users/{id}/
```

### Authentication

Required

### Path Parameters

- `id` (integer, required): User ID

### Request

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body (PATCH - partial update):**
```json
{
  "first_name": "Johnny",
  "phone": "+1112223333"
}
```

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Resource updated successfully",
  "data": {
    "id": 5,
    "email": "user@example.com",
    "first_name": "Johnny",
    "last_name": "Doe",
    "full_name": "Johnny Doe",
    "phone": "+1112223333",
    "avatar": null,
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-01-15T08:00:00Z",
    "last_login": "2025-12-02T10:00:00Z"
  }
}
```

**Note:** Cannot update `email`, `date_joined`, `last_login` (read-only fields)

---

## Change Password

Change authenticated user's password.

### Endpoint

```
POST /api/auth/users/change_password/
```

### Authentication

Required

### Request

**Body:**
```json
{
  "old_password": "CurrentPass123!",
  "new_password": "NewSecurePass456!"
}
```

**Fields:**
- `old_password` (string, required): Current password
- `new_password` (string, required): New password (min 8 characters)

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Password changed successfully"
}
```

**Error (400 Bad Request):**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Password verification failed",
  "errors": {
    "old_password": ["Wrong password"]
  }
}
```

---

## Activate User

Activate a deactivated user account. **Admin only**.

### Endpoint

```
POST /api/auth/users/{id}/activate/
```

### Authentication

Required (Admin/Staff only)

### Path Parameters

- `id` (integer, required): User ID

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "User user@example.com activated successfully",
  "data": {
    "email": "user@example.com",
    "is_active": true
  }
}
```

---

## Deactivate User

Deactivate an active user account. **Admin only**.

### Endpoint

```
POST /api/auth/users/{id}/deactivate/
```

### Authentication

Required (Admin/Staff only)

### Path Parameters

- `id` (integer, required): User ID

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "User user@example.com deactivated successfully",
  "data": {
    "email": "user@example.com",
    "is_active": false
  }
}
```

---

## Delete User

Delete user account. **Admin only**.

### Endpoint

```
DELETE /api/auth/users/{id}/
```

### Authentication

Required (Admin/Staff only)

### Path Parameters

- `id` (integer, required): User ID

### Response

**Success (204 No Content):**
```json
{
  "success": true,
  "status_code": 204,
  "message": "Resource deleted successfully"
}
```

---

## Upload Avatar

Upload or update user's profile photo.

### Endpoint

```
PATCH /api/auth/users/{id}/
```

### Authentication

Required

### Request

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body (multipart/form-data):**
```
avatar: [file]
```

**Supported Formats:** JPG, JPEG, PNG, GIF  
**Max Size:** 5MB (configurable)

### Response

**Success (200 OK):**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Resource updated successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "avatar": "http://localhost:8000/media/avatars/2025/12/02/photo_abc123.jpg",
    ...
  }
}
```

### Usage Example

**cURL:**
```bash
curl -X PATCH http://localhost:8000/api/auth/users/1/ \
  -H "Authorization: Bearer <access_token>" \
  -F "avatar=@/path/to/photo.jpg"
```

**JavaScript (FormData):**
```javascript
const formData = new FormData();
formData.append('avatar', fileInput.files[0]);

const response = await fetch(`http://localhost:8000/api/auth/users/${userId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  body: formData
});

const result = await response.json();
if (result.success) {
  console.log('New avatar URL:', result.data.avatar);
}
```

---

## Related Documentation

- [Authentication API](./authentication.md) - Login and token refresh
- [Response Format Guide](../response_handlers.md) - Standard response structure
