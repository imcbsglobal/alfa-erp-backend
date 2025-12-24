# Adding a New Django App

This guide walks you through creating a new Django app in the ALFA ERP Backend project.

## Overview

Django apps are modular components that encapsulate specific functionality. Each app should have a single, well-defined purpose.
- [ ] Create Folder name in apps
- [ ] App created in `apps/` directory
- [ ] App config updated with correct name
- [ ] Added to `INSTALLED_APPS`

- [ ] Models created with proper fields
- [ ] Migrations created and applied
- [ ] Serializers implemented
- [ ] Views/ViewSets created
- [ ] URLs configured

- [ ] API documentation created
- [ ] Main README updated

## Step-by-Step Guide

### 1. Create the App

Use Django's `startapp` command to create the app inside the `apps/` directory:

```bash
python manage.py startapp <app_name> apps/<app_name>
```

Example for an inventory app:
```bash
python manage.py startapp inventory apps/inventory
```

This creates:
```
apps/inventory/
├── migrations/
│   └── __init__.py
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
└── views.py
```

### 2. Update App Configuration

Edit `apps/<app_name>/apps.py` to set the correct name:

```python
from django.apps import AppConfig

class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'  # Full Python path
    verbose_name = 'Inventory Management'
```

### 3. Register App in Settings

Add the app to `INSTALLED_APPS` in `config/settings/base.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'apps.accounts',
    'apps.inventory',  # Add your new app here
]
```

### 4. Create Models

Define your data models in `apps/<app_name>/models.py`:

```python
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    """Product model for inventory"""
    
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_products'
    )
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
```

### 5. Create Serializers

Create `apps/<app_name>/serializers.py`:

```python
from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    
    created_by_email = serializers.EmailField(
        source='created_by.email',
        read_only=True
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'price',
            'stock_quantity', 'created_at', 'updated_at',
            'created_by', 'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        """Set created_by from request user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
```

### 6. Create Views

Create API views in `apps/<app_name>/views.py`:

```python
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['sku', 'stock_quantity']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Admin only for create, update, delete"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def adjust_stock(self, request, pk=None):
        """Adjust product stock quantity"""
        product = self.get_object()
        adjustment = request.data.get('adjustment', 0)
        
        try:
            adjustment = int(adjustment)
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid adjustment value'},
                status=400
            )
        
        product.stock_quantity += adjustment
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
```

### 7. Create URL Configuration

Create `apps/<app_name>/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

app_name = 'inventory'

urlpatterns = [
    path('', include(router.urls)),
]
```

### 8. Register URLs in Main Config

Add to `config/urls.py`:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/inventory/', include('apps.inventory.urls')),  # Add this
]
```

### 9. Configure Admin Interface

Update `apps/<app_name>/admin.py`:

```python
from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock_quantity', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'sku', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'sku', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Audit Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
```

### 10. Create and Run Migrations

```bash
# Create migration files
python manage.py makemigrations inventory

# Review the migration
python manage.py sqlmigrate inventory 0001

# Apply migrations
python manage.py migrate inventory
```

### 11. Create Tests

### 12. Document Your API

Create `docs/<app_name>_api.md`:

```markdown
# Inventory API Documentation

## Endpoints

### List Products
- **URL**: `/api/inventory/products/`
- **Method**: `GET`
- **Auth**: Required
- **Response**: List of products with pagination

### Create Product
- **URL**: `/api/inventory/products/`
- **Method**: `POST`
- **Auth**: Admin only
- **Body**:
  ```json
  {
    "name": "Product Name",
    "sku": "PROD-001",
    "description": "Product description",
    "price": "99.99",
    "stock_quantity": 100
  }
  ```

[Add more endpoints...]
```

## Checklist

- [ ] App created in `apps/` directory
- [ ] App config updated with correct name
- [ ] Added to `INSTALLED_APPS`
- [ ] Models created with proper fields
- [ ] Migrations created and applied
- [ ] Serializers implemented
- [ ] Views/ViewSets created
- [ ] URLs configured
- [ ] Admin interface configured
- [ ] Tests written and passing
- [ ] API documentation created
- [ ] Main README updated
