# Code Documentation

## Architecture Overview

The ERP system follows a modular, layered architecture with clear separation of concerns.

### Layers

1. **Presentation Layer** (Views)
   - RESTful API endpoints
   - Request/response handling
   - Input validation

2. **Business Logic Layer** (Serializers & Services)
   - Data validation
   - Business rules enforcement
   - Data transformation

3. **Data Access Layer** (Models)
   - Database models
   - ORM queries
   - Data persistence

4. **Common Layer** (Utilities)
   - Shared utilities
   - Base models
   - Common mixins

## Project Structure

```
alfa-erp-backend/
├── config/                 # Project configuration
├── apps/
│   ├── common/            # Shared utilities
│   ├── authentication/    # Auth & RBAC
│   ├── hrm/              # HR Management
│   ├── inventory/        # Inventory Management
│   ├── sales/            # Sales Management
│   ├── finance/          # Finance Management
│   └── reports/          # Reporting
```

## Common App

### Base Models

#### TimeStampedModel
```python
class TimeStampedModel(models.Model):
    """
    Abstract model providing automatic timestamps.
    All models inherit this for audit trail.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### UserTrackingModel
```python
class UserTrackingModel(TimeStampedModel):
    """
    Tracks which user created/modified records.
    """
    created_by = models.ForeignKey('authentication.User', ...)
    updated_by = models.ForeignKey('authentication.User', ...)
```

#### SoftDeleteModel
```python
class SoftDeleteModel(models.Model):
    """
    Provides soft delete functionality.
    Records marked as deleted instead of removed.
    """
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
```

#### BaseModel
```python
class BaseModel(UserTrackingModel, SoftDeleteModel, ActiveModel):
    """
    Complete base model with all common functionality.
    Use this for most models in the system.
    """
```

### Utilities

#### Response Formatting
```python
from apps.common.utils import format_response

response = format_response(
    success=True,
    message='Operation successful',
    data={'key': 'value'},
    status_code=200
)
```

#### Pagination
```python
from apps.common.utils import paginate_queryset

result = paginate_queryset(
    queryset=User.objects.all(),
    page=1,
    page_size=20
)
```

### Mixins

#### ResponseMixin
```python
class MyView(APIView, ResponseMixin):
    def get(self, request):
        return self.success_response(data={'key': 'value'})
```

#### UserTrackingMixin
```python
class MyViewSet(viewsets.ModelViewSet, UserTrackingMixin):
    # Automatically sets created_by/updated_by
```

## Authentication App

### User Model

Custom user model extending AbstractBaseUser with:
- Username/email authentication
- Multiple roles support
- Password validation
- Session tracking

```python
from apps.authentication.models import User

user = User.objects.create_user(
    username='john_doe',
    email='john@example.com',
    password='secure_password'
)

# Check roles
if user.has_role('ADMIN'):
    # Admin logic
    pass

# Get role codes
roles = user.get_role_codes()  # ['ADMIN', 'MANAGER']
```

### Role Model

Flexible role system with JSON permissions:

```python
from apps.authentication.models import Role

role = Role.objects.create(
    name='Manager',
    code='MANAGER',
    permissions={
        'users': ['read'],
        'inventory': ['create', 'read', 'update'],
        'sales': ['create', 'read', 'update']
    }
)

# Assign to user
user.roles.add(role)
```

### Authentication Flow

1. **Login Request** → `LoginView`
2. **Authenticate** → Django auth backend
3. **Generate JWT** → simplejwt
4. **Return Response** → User data + tokens + roles
5. **Frontend Stores** → Tokens + roles in localStorage
6. **Subsequent Requests** → JWT in Authorization header

### Permission System

#### Decorators

```python
from apps.authentication.permissions import (
    require_role,
    require_any_role,
    require_all_roles
)

@require_role('ADMIN')
def admin_view(request):
    pass

@require_any_role('ADMIN', 'MANAGER')
def manager_view(request):
    pass
```

#### Permission Classes

```python
from apps.authentication.permissions import HasRole, HasAnyRole

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ['ADMIN', 'MANAGER']
```

### Serializers

#### LoginSerializer
- Validates credentials
- Generates JWT tokens
- Returns user data with roles
- Aggregates permissions from roles

```python
{
    "user": {...},
    "tokens": {"access": "...", "refresh": "..."},
    "roles": ["ADMIN"],
    "permissions": {...}
}
```

## View Patterns

### Standard ViewSet Pattern

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.common.mixins import ResponseMixin, UserTrackingMixin

class ProductViewSet(viewsets.ModelViewSet, ResponseMixin, UserTrackingMixin):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Custom filtering
        return super().get_queryset()
    
    @action(detail=False, methods=['get'])
    def custom_action(self, request):
        return self.success_response(data={})
```

### Custom Action Pattern

```python
@action(detail=True, methods=['post'])
def assign_roles(self, request, pk=None):
    """Custom action on detail endpoint."""
    obj = self.get_object()
    # Logic here
    return self.success_response(message='Success')
```

## Model Design Patterns

### Standard Model Pattern

```python
from django.db import models
from apps.common.models import BaseModel

class Product(BaseModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'inventory_products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
```

### Relationships

```python
# Foreign Key
department = models.ForeignKey(
    Department,
    on_delete=models.CASCADE,
    related_name='employees'
)

# Many-to-Many
roles = models.ManyToManyField(
    Role,
    related_name='users',
    blank=True
)
```

## Serializer Patterns

### Basic Serializer

```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
```

### Nested Serializer

```python
class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer', 'items', 'total']
```

### Custom Fields

```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_codes = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_role_codes(self, obj):
        return obj.get_role_codes()
```

## URL Configuration

### App URLs Pattern

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('custom/', custom_view, name='custom'),
]
```

## Admin Configuration

### Standard Admin Pattern

```python
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'sku']
    readonly_fields = ['created_at', 'updated_at']
```

## Testing Patterns

### Model Tests

```python
from django.test import TestCase
from apps.authentication.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='test123'
        )
    
    def test_has_role(self):
        role = Role.objects.create(name='Admin', code='ADMIN')
        self.user.roles.add(role)
        self.assertTrue(self.user.has_role('ADMIN'))
```

### API Tests

```python
from rest_framework.test import APITestCase
from rest_framework import status

class LoginAPITest(APITestCase):
    def test_login_success(self):
        response = self.client.post('/api/auth/login/', {
            'username': 'test',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data['data'])
```

## Celery Tasks

### Task Definition

```python
from celery import shared_task

@shared_task
def send_email_task(user_id, subject, message):
    """Send email asynchronously."""
    user = User.objects.get(id=user_id)
    send_mail(subject, message, 'from@example.com', [user.email])
```

### Task Usage

```python
# Call async
send_email_task.delay(user.id, 'Subject', 'Message')

# Call with countdown
send_email_task.apply_async(
    args=[user.id, 'Subject', 'Message'],
    countdown=60  # Execute after 60 seconds
)
```

## Best Practices

### 1. Always Use Base Models
```python
# Good
class MyModel(BaseModel):
    pass

# Avoid
class MyModel(models.Model):
    # Manual timestamp fields
```

### 2. Use Soft Delete
```python
# Query active records
products = Product.objects.filter(is_deleted=False)

# Or use custom manager
class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
```

### 3. Role-Based Views
```python
# Always protect sensitive endpoints
class FinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ['ADMIN', 'FINANCE']
```

### 4. Consistent Response Format
```python
# Use ResponseMixin
return self.success_response(data=data, message='Success')
return self.error_response(message='Error', errors=errors)
```

### 5. Validation in Serializers
```python
class ProductSerializer(serializers.ModelSerializer):
    def validate_sku(self, value):
        if not value.isupper():
            raise serializers.ValidationError('SKU must be uppercase')
        return value
```

## Database Optimization

### Select Related
```python
# Good - One query
users = User.objects.select_related('department').all()

# Bad - N+1 queries
users = User.objects.all()
for user in users:
    print(user.department.name)
```

### Prefetch Related
```python
# Good - Two queries
users = User.objects.prefetch_related('roles').all()
```

### Indexing
```python
class Product(BaseModel):
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name', 'sku']),
        ]
```

## Security Considerations

1. **Never expose sensitive data**
   - Use `write_only=True` for passwords
   - Exclude sensitive fields from serializers

2. **Validate all inputs**
   - Use serializer validation
   - Sanitize user inputs

3. **Use permissions consistently**
   - Always set `permission_classes`
   - Use role-based decorators

4. **Environment variables**
   - Never hardcode secrets
   - Use `django-environ`

5. **HTTPS in production**
   - Set `SECURE_SSL_REDIRECT = True`
   - Use secure cookies

---

For more information, refer to:
- Django Documentation: https://docs.djangoproject.com/
- DRF Documentation: https://www.django-rest-framework.org/
- Celery Documentation: https://docs.celeryproject.org/
