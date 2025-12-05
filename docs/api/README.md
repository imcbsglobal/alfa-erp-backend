# API Documentation

Complete API reference for ALFA ERP Backend.

## Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.onrender.com`

## Authentication

Most endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Get tokens via the [Login endpoint](./authentication.md#login). The login response includes user `role` (single value), `department` (text field), and `job_title` (object with id and title).

## Standard Response Format

All API endpoints return responses in a consistent format:

### Success Response
```json
{
  "success": true,
  "status_code": 200,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "status_code": 400,
  "message": "Error message",
  "errors": { ... }
}
```

For detailed response format documentation, see [Response Handlers Guide](../response_handlers.md).

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required or failed
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Pagination

List endpoints support pagination:

### Query Parameters
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

### Response Format
```json
{
  "success": true,
  "status_code": 200,
  "message": "List retrieved successfully",
  "data": {
    "count": 100,
    "next": "http://localhost:8000/api/endpoint/?page=2",
    "previous": null,
    "results": [ ... ]
  }
}
```

## Filtering & Search

List endpoints support filtering and searching:

### Query Parameters
- `search` - Full-text search across multiple fields
- `ordering` - Sort by field (prefix with `-` for descending)

### Examples
```
GET /api/auth/users/?search=john
GET /api/auth/users/?ordering=-date_joined
GET /api/auth/users/?search=admin&ordering=email
```

## API Endpoints

### Authentication
- [Login](./authentication.md#login) - `POST /api/auth/login/` - Returns JWT tokens and user menus
- [Refresh Token](./authentication.md#refresh-token) - `POST /api/auth/token/refresh/`

### Menu Access Control
- [Get User Menus](./menu_access_control.md#get-user-menus) - `GET /api/access/menus/` - Retrieve user's assigned menus

### User Management
- [List Users](./users.md#list-users) - `GET /api/auth/users/`
- [Get Current User](./users.md#get-current-user-profile) - `GET /api/auth/users/me/`
- [Get User by ID](./users.md#get-user-by-id) - `GET /api/auth/users/{id}/`
- [Create User](./users.md#create-user) - `POST /api/auth/users/`
- [Update User](./users.md#update-user) - `PUT/PATCH /api/auth/users/{id}/`
- [Delete User](./users.md#delete-user) - `DELETE /api/auth/users/{id}/`
- [Change Password](./users.md#change-password) - `POST /api/auth/users/change_password/`
- [Activate User](./users.md#activate-user) - `POST /api/auth/users/{id}/activate/`
- [Deactivate User](./users.md#deactivate-user) - `POST /api/auth/users/{id}/deactivate/`
- [Upload Avatar](./users.md#upload-avatar) - `PATCH /api/auth/users/{id}/`

### Job Titles
- [List Job Titles](./job_titles.md#list-all-job-titles) - `GET /api/auth/job-titles/`
- [Get Job Title](./job_titles.md#get-job-title-by-id) - `GET /api/auth/job-titles/{id}/`
- [Create Job Title](./job_titles.md#create-job-title) - `POST /api/auth/job-titles/`
- [Update Job Title](./job_titles.md#update-job-title) - `PUT/PATCH /api/auth/job-titles/{id}/`
- [Delete Job Title](./job_titles.md#delete-job-title) - `DELETE /api/auth/job-titles/{id}/`

## Quick Start Examples

### 1. Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@gmail.com", "password":"admin@123"}'
```

### 2. Get Current User Profile
```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

Note: The returned user object includes a single `role` field (ADMIN, USER, or SUPERADMIN), `department` as a text field, and `job_title` as a UUID reference.

### 3. Create New User (Admin Only)
```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 4. Refresh Access Token
```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

## JavaScript/Frontend Integration

### Setup Axios Instance
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/token/refresh/', {
            refresh: refreshToken
          });
          localStorage.setItem('access_token', data.access);
          // Retry original request
          error.config.headers.Authorization = `Bearer ${data.access}`;
          return axios(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Usage Examples
```javascript
// Login
const login = async (email, password) => {
  const response = await api.post('/api/auth/login/', {
    username: email,
    password: password
  });
  
  if (response.data.success) {
    localStorage.setItem('access_token', response.data.data.access);
    localStorage.setItem('refresh_token', response.data.data.refresh);
    return response.data.data.user;
  }
};

// Get current user
const getCurrentUser = async () => {
  const response = await api.get('/api/auth/users/me/');
  return response.data.data;
};

// Create user (admin only)
const createUser = async (userData) => {
  const response = await api.post('/api/auth/users/', userData);
  return response.data.data;
};

// Upload avatar
const uploadAvatar = async (userId, file) => {
  const formData = new FormData();
  formData.append('avatar', file);
  
  const response = await api.patch(`/api/auth/users/${userId}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data.data;
};
```

## Error Handling

All API errors follow this format:

```json
{
  "success": false,
  "status_code": 400,
  "message": "Error description",
  "errors": {
    "field_name": ["Error message for field"]
  }
}
```

### Common Error Codes

| Status | Meaning | Common Causes |
|--------|---------|---------------|
| 400 | Bad Request | Invalid data, validation errors |
| 401 | Unauthorized | Missing/invalid token, expired token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server error |

## Rate Limiting

Currently not implemented. Will be added in future versions.

**Planned limits:**
- Authentication endpoints: 5 requests/minute
- API endpoints: 100 requests/minute

## Versioning

Current version: **v1** (implicit in URLs)

Future versions will use:
- URL-based: `/api/v2/auth/login/`
- Header-based: `Accept: application/vnd.alfaerp.v2+json`

## CORS

Frontend domains must be configured in `CORS_ALLOWED_ORIGINS`:
- Development: `localhost:3000`, `localhost:3001`
- Production: Configure based on deployment

## Additional Resources

- [Response Handlers Guide](../response_handlers.md) - Detailed response format documentation
- [Development Setup](../development_setup.md) - Local development guide
- [Adding New Apps](../adding_new_app.md) - Creating new API modules

## Support

For questions or issues:
- Check documentation in `docs/` folder
- Review code examples in repository
- Contact development team
