# Response Handler Usage Guide

Global reusable response handlers for consistent API responses across the ALFA ERP Backend.

## Import

```python
from apps.common.response import (
    success_response,
    error_response,
    validation_error_response,
    created_response,
    no_content_response,
    unauthorized_response,
    forbidden_response,
    not_found_response,
    server_error_response,
)
```

## Response Format

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

## Usage Examples

### 1. Success Response (200 OK)

```python
from apps.common.response import success_response

def get_user(self, request, pk):
    user = User.objects.get(pk=pk)
    serializer = UserSerializer(user)
    return success_response(
        data=serializer.data,
        message='User retrieved successfully'
    )
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "User retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John"
  }
}
```

### 2. Created Response (201 Created)

```python
from apps.common.response import created_response

def create(self, request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return created_response(
        data=serializer.data,
        message='User created successfully'
    )
```

**Response:**
```json
{
  "success": true,
  "status_code": 201,
  "message": "User created successfully",
  "data": {
    "id": 5,
    "email": "newuser@example.com"
  }
}
```

### 3. Validation Error (400 Bad Request)

```python
from apps.common.response import validation_error_response

def update_profile(self, request):
    if not request.data.get('email'):
        return validation_error_response(
            errors={'email': ['This field is required']},
            message='Validation failed'
        )
```

**Response:**
```json
{
  "success": false,
  "status_code": 400,
  "message": "Validation failed",
  "errors": {
    "email": ["This field is required"]
  }
}
```

### 4. Unauthorized (401)

```python
from apps.common.response import unauthorized_response

def protected_view(self, request):
    if not request.user.is_authenticated:
        return unauthorized_response(
            message='Authentication credentials required'
        )
```

**Response:**
```json
{
  "success": false,
  "status_code": 401,
  "message": "Authentication credentials required"
}
```

### 5. Forbidden (403)

```python
from apps.common.response import forbidden_response

def admin_only_view(self, request):
    if not request.user.is_staff:
        return forbidden_response(
            message='Admin access required'
        )
```

**Response:**
```json
{
  "success": false,
  "status_code": 403,
  "message": "Admin access required"
}
```

### 6. Not Found (404)

```python
from apps.common.response import not_found_response

def get_user(self, request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return not_found_response(message='User not found')
```

**Response:**
```json
{
  "success": false,
  "status_code": 404,
  "message": "User not found"
}
```

### 7. No Content (204)

```python
from apps.common.response import no_content_response

def delete(self, request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    return no_content_response(message='User deleted successfully')
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### 8. Server Error (500)

```python
from apps.common.response import server_error_response

def process_data(self, request):
    try:
        # ... complex operation
        pass
    except Exception as e:
        return server_error_response(
            message=f'Processing failed: {str(e)}'
        )
```

**Response:**
```json
{
  "success": false,
  "status_code": 500,
  "message": "Processing failed: Database connection timeout"
}
```

### 9. Generic Error Response

```python
from apps.common.response import error_response
from rest_framework import status

def custom_error(self, request):
    return error_response(
        message='Custom error occurred',
        errors={'field': ['Error details']},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
```

### 10. Success with Extra Fields

```python
from apps.common.response import success_response

def get_stats(self, request):
    return success_response(
        data={'total_users': 100},
        message='Statistics retrieved',
        meta={'generated_at': '2025-12-02T10:00:00Z'},
        version='v1'
    )
```

**Response:**
```json
{
  "success": true,
  "status_code": 200,
  "message": "Statistics retrieved",
  "data": {
    "total_users": 100
  },
  "meta": {
    "generated_at": "2025-12-02T10:00:00Z"
  },
  "version": "v1"
}
```

## Complete ViewSet Example

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model

from apps.common.response import (
    success_response,
    created_response,
    validation_error_response,
    not_found_response,
    forbidden_response,
    no_content_response
)
from .serializers import ProductSerializer

User = get_user_model()


class ProductViewSet(viewsets.ModelViewSet):
    """Product management with consistent responses"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all products"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(
            data=serializer.data,
            message='Products retrieved successfully',
            count=queryset.count()
        )
    
    def retrieve(self, request, pk=None):
        """Get single product"""
        try:
            product = self.get_queryset().get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return not_found_response(message='Product not found')
        
        serializer = self.get_serializer(product)
        return success_response(
            data=serializer.data,
            message='Product retrieved successfully'
        )
    
    def create(self, request):
        """Create new product (admin only)"""
        if not request.user.is_staff:
            return forbidden_response(message='Only admins can create products')
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return validation_error_response(
                errors=serializer.errors,
                message='Validation failed'
            )
        
        product = serializer.save(created_by=request.user)
        return created_response(
            data=serializer.data,
            message='Product created successfully'
        )
    
    def update(self, request, pk=None):
        """Update product (admin only)"""
        if not request.user.is_staff:
            return forbidden_response(message='Only admins can update products')
        
        try:
            product = self.get_queryset().get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return not_found_response(message='Product not found')
        
        serializer = self.get_serializer(product, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return validation_error_response(
                errors=serializer.errors,
                message='Validation failed'
            )
        
        serializer.save()
        return success_response(
            data=serializer.data,
            message='Product updated successfully'
        )
    
    def destroy(self, request, pk=None):
        """Delete product (admin only)"""
        if not request.user.is_staff:
            return forbidden_response(message='Only admins can delete products')
        
        try:
            product = self.get_queryset().get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return not_found_response(message='Product not found')
        
        product.delete()
        return no_content_response(message='Product deleted successfully')
    
    @action(detail=True, methods=['post'])
    def add_stock(self, request, pk=None):
        """Custom action with response handler"""
        try:
            product = self.get_queryset().get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return not_found_response(message='Product not found')
        
        quantity = request.data.get('quantity')
        
        if not quantity or not isinstance(quantity, int):
            return validation_error_response(
                errors={'quantity': ['Valid integer required']},
                message='Invalid quantity'
            )
        
        product.stock += quantity
        product.save()
        
        return success_response(
            data={'stock': product.stock},
            message=f'Added {quantity} units to stock'
        )
```

## Best Practices

1. **Always include a message**: Helps frontend display user-friendly notifications
   ```python
   return success_response(data=data, message='Operation completed')
   ```

2. **Use appropriate status codes**: Use the shortcut functions for common cases
   ```python
   return created_response(...)  # 201
   return not_found_response(...)  # 404
   ```

3. **Provide detailed errors**: Help frontend display validation errors
   ```python
   return validation_error_response(
       errors=serializer.errors,
       message='Please correct the errors'
   )
   ```

4. **Add extra context when useful**: Use kwargs for additional metadata
   ```python
   return success_response(
       data=data,
       message='Success',
       total=100,
       page=1
   )
   ```

5. **Handle exceptions gracefully**:
   ```python
   try:
       # ... operation
       return success_response(data=result)
   except ValidationError as e:
       return validation_error_response(errors=str(e))
   except Exception as e:
       return server_error_response(message=str(e))
   ```

## Migration from Standard DRF Response

### Before (Standard DRF)
```python
from rest_framework.response import Response
from rest_framework import status

return Response({'email': user.email}, status=status.HTTP_200_OK)
```

### After (With Response Handlers)
```python
from apps.common.response import success_response

return success_response(
    data={'email': user.email},
    message='User data retrieved'
)
```

## Testing Response Handlers

```python
from django.test import TestCase
from rest_framework.test import APIClient
from apps.common.response import success_response, error_response

class ResponseHandlerTestCase(TestCase):
    def test_success_response_format(self):
        """Test success response structure"""
        response = success_response(
            data={'key': 'value'},
            message='Test message'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Test message')
        self.assertIn('data', response.data)
    
    def test_error_response_format(self):
        """Test error response structure"""
        response = error_response(
            message='Error occurred',
            errors={'field': ['Error']}
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
```

## Benefits

✅ **Consistent API responses** across all endpoints  
✅ **Easier frontend integration** with predictable structure  
✅ **Better error handling** with detailed error messages  
✅ **Reduced boilerplate** with reusable functions  
✅ **Type safety** with clear function signatures  
✅ **Better documentation** with standardized formats
