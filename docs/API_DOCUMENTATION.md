# API Documentation

## Overview

This document provides comprehensive API documentation for the ERP System Backend.

## Base URL

- **Development**: `http://localhost:8000/api/`
- **Production**: `https://your-domain.com/api/`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

### Obtaining Tokens

**POST** `/auth/login/`

Request:
```json
{
    "username": "john_doe",
    "password": "password123"
}
```

Response:
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "roles": [
                {
                    "id": 1,
                    "name": "Administrator",
                    "code": "ADMIN",
                    "description": "Full system access"
                }
            ],
            "role_codes": ["ADMIN"],
            "permissions": {
                "users": ["create", "read", "update", "delete"],
                "inventory": ["create", "read", "update", "delete"]
            }
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        },
        "roles": ["ADMIN"],
        "permissions": {...}
    }
}
```

### Refreshing Tokens

**POST** `/auth/token/refresh/`

Request:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## User Management

### Register User

**POST** `/auth/register/`

Request:
```json
{
    "username": "jane_doe",
    "email": "jane@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role_ids": [2, 3]
}
```

### Get Current User

**GET** `/auth/users/me/`

Response:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "roles": [...],
        "role_codes": ["ADMIN"]
    }
}
```

### Update Profile

**PUT/PATCH** `/auth/users/update_profile/`

Request:
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "phone": "+1234567890"
}
```

### Change Password

**POST** `/auth/users/change_password/`

Request:
```json
{
    "old_password": "OldPass123!",
    "new_password": "NewPass456!",
    "new_password_confirm": "NewPass456!"
}
```

### List Users

**GET** `/auth/users/`

Query Parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `is_active`: Filter by active status

Response:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/auth/users/?page=2",
    "previous": null,
    "results": [...]
}
```

### Assign Roles to User

**POST** `/auth/users/{id}/assign_roles/`

Request:
```json
{
    "role_ids": [1, 2, 3]
}
```

## Role Management

### List Roles

**GET** `/auth/roles/`

### Create Role

**POST** `/auth/roles/`

Request:
```json
{
    "name": "Sales Manager",
    "code": "SALES_MGR",
    "description": "Manages sales operations",
    "permissions": {
        "sales": ["create", "read", "update"],
        "inventory": ["read"],
        "customers": ["create", "read", "update"]
    }
}
```

### Get Active Roles

**GET** `/auth/roles/active/`

## HRM Endpoints

### Departments

**GET** `/hrm/departments/`
- List all departments

**POST** `/hrm/departments/`
- Create new department

**GET** `/hrm/departments/{id}/`
- Get department details

**PUT/PATCH** `/hrm/departments/{id}/`
- Update department

**DELETE** `/hrm/departments/{id}/`
- Delete department (soft delete)

## Inventory Endpoints

### Products

**GET** `/inventory/products/`
- List all products

**POST** `/inventory/products/`
- Create new product

Request:
```json
{
    "name": "Laptop",
    "sku": "LAP-001",
    "description": "15-inch laptop",
    "unit_price": "999.99",
    "stock_quantity": 50,
    "reorder_level": 10
}
```

**GET** `/inventory/products/{id}/`
- Get product details

**PUT/PATCH** `/inventory/products/{id}/`
- Update product

**DELETE** `/inventory/products/{id}/`
- Delete product (soft delete)

## Sales Endpoints

### Customers

**GET** `/sales/customers/`
- List all customers

**POST** `/sales/customers/`
- Create new customer

Request:
```json
{
    "name": "Acme Corporation",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Business St",
    "company": "Acme Corp"
}
```

## Finance Endpoints

### Accounts

**Permissions Required**: ADMIN or FINANCE role

**GET** `/finance/accounts/`
- List all accounts

**POST** `/finance/accounts/`
- Create new account

Request:
```json
{
    "name": "Cash Account",
    "account_number": "1001",
    "account_type": "ASSET",
    "balance": "10000.00"
}
```

## Reports Endpoints

### Dashboard Summary

**GET** `/reports/dashboard/`

Response:
```json
{
    "total_users": 150,
    "total_products": 500,
    "total_customers": 200,
    "total_revenue": 150000.00
}
```

## Error Responses

All error responses follow this format:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error detail"]
    }
}
```

### Common HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- **Authenticated users**: 1000 requests per hour
- **Anonymous users**: 100 requests per hour

## Pagination

List endpoints support pagination:

Query Parameters:
- `page`: Page number
- `page_size`: Items per page (max: 100)

Response format:
```json
{
    "count": 1000,
    "next": "http://api.example.com/users/?page=2",
    "previous": null,
    "results": [...]
}
```

## Frontend Integration Example

### JavaScript/React

```javascript
// Login
const login = async (username, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Store tokens
        localStorage.setItem('access_token', data.data.tokens.access);
        localStorage.setItem('refresh_token', data.data.tokens.refresh);
        
        // Store roles for navigation control
        localStorage.setItem('user_roles', JSON.stringify(data.data.roles));
        
        return data.data;
    }
};

// Make authenticated request
const fetchProducts = async () => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/inventory/products/', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
    });
    
    return await response.json();
};

// Check user role for navigation
const userRoles = JSON.parse(localStorage.getItem('user_roles') || '[]');
const canAccessFinance = userRoles.includes('ADMIN') || userRoles.includes('FINANCE');
```

## WebSocket Support (Future)

WebSocket endpoints will be available for real-time features:
- Live notifications
- Real-time inventory updates
- Chat support

---

For more details, visit the interactive documentation:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
