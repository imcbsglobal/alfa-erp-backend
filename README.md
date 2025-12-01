# ERP System Backend

A comprehensive Django-based ERP (Enterprise Resource Planning) system with JWT authentication, role-based access control (RBAC), and modular architecture.

## 🚀 Features

- **JWT Authentication**: Secure token-based authentication using `djangorestframework-simplejwt`
- **Role-Based Access Control (RBAC)**: Flexible permission system with multiple roles per user
- **Modular Architecture**: Separate apps for HRM, Inventory, Sales, Finance, and Reports
- **RESTful API**: Built with Django REST Framework
- **PostgreSQL Database**: Production-ready database backend
- **Celery Integration**: Asynchronous task processing with Redis
- **Docker Support**: Containerized deployment with Docker Compose
- **API Documentation**: Auto-generated with drf-yasg (Swagger/ReDoc)

## 📋 Requirements

- Python 3.12+
- PostgreSQL 13+
- Redis 6+ (for Celery)
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alfa-erp-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/dev.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Configure environment**
   ```bash
   copy .env.example .env
   ```

2. **Build and run containers**
   ```bash
   cd docker
   docker-compose up --build
   ```

3. **Create superuser (in container)**
   ```bash
   docker exec -it erp_backend python manage.py createsuperuser
   ```

## 📁 Project Structure

```
alfa-erp-backend/
├── config/                      # Project configuration
│   ├── settings/
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Development settings
│   │   └── production.py       # Production settings
│   ├── urls.py                 # Main URL configuration
│   ├── wsgi.py                 # WSGI configuration
│   ├── asgi.py                 # ASGI configuration
│   └── celery.py               # Celery configuration
│
├── apps/                        # Application modules
│   ├── common/                 # Shared utilities
│   ├── authentication/         # User auth & RBAC
│   ├── hrm/                    # Human Resource Management
│   ├── inventory/              # Inventory Management
│   ├── sales/                  # Sales Management
│   ├── finance/                # Finance Management
│   └── reports/                # Reports & Analytics
│
├── requirements/               # Python dependencies
│   ├── base.txt               # Base requirements
│   ├── dev.txt                # Development requirements
│   └── prod.txt               # Production requirements
│
├── docker/                     # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/                    # Utility scripts
├── static/                     # Static files
├── media/                      # Media files
├── logs/                       # Application logs
├── docs/                       # Documentation
├── manage.py                   # Django management script
└── README.md
```

## 🔐 Authentication & RBAC

### Login Endpoint

**POST** `/api/auth/login/`

```json
{
    "username": "john_doe",
    "password": "password123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "roles": [...],
            "role_codes": ["ADMIN", "MANAGER"],
            "permissions": {...}
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        },
        "roles": ["ADMIN", "MANAGER"],
        "permissions": {...}
    }
}
```

### Using Roles in Frontend

The `roles` array returned on login can be used to control navigation:

```javascript
// Example frontend code
const userRoles = loginResponse.data.roles;

if (userRoles.includes('ADMIN')) {
    // Show admin menu
}
if (userRoles.includes('FINANCE')) {
    // Show finance menu
}
```

### Role-Based Permission Decorators

```python
from apps.authentication.permissions import require_role, require_any_role

# Require specific role
@require_role('ADMIN')
def admin_only_view(request):
    pass

# Require any of specified roles
@require_any_role('ADMIN', 'MANAGER')
def manager_view(request):
    pass
```

### Permission Classes for ViewSets

```python
from apps.authentication.permissions import HasRole, HasAnyRole

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ['ADMIN', 'MANAGER']
```

## 📚 API Documentation

Once the server is running, access the API documentation at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/

## 🔑 Key Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/users/me/` - Get current user profile
- `POST /api/auth/users/change_password/` - Change password

### Roles
- `GET /api/auth/roles/` - List all roles
- `POST /api/auth/roles/` - Create role (Admin only)
- `GET /api/auth/roles/{id}/` - Get role details
- `PUT /api/auth/roles/{id}/` - Update role (Admin only)

### HRM
- `GET /api/hrm/departments/` - List departments
- `POST /api/hrm/departments/` - Create department

### Inventory
- `GET /api/inventory/products/` - List products
- `POST /api/inventory/products/` - Create product

### Sales
- `GET /api/sales/customers/` - List customers
- `POST /api/sales/customers/` - Create customer

### Finance
- `GET /api/finance/accounts/` - List accounts (Finance role required)
- `POST /api/finance/accounts/` - Create account (Finance role required)

### Reports
- `GET /api/reports/dashboard/` - Get dashboard summary

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example`):

- `DJANGO_ENVIRONMENT` - Set to `development` or `production`
- `SECRET_KEY` - Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `CELERY_BROKER_URL` - Redis URL for Celery
- `CORS_ALLOWED_ORIGINS` - Frontend URLs

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations status
python manage.py showmigrations
```

## 🚀 Running Celery

For asynchronous tasks:

```bash
# Start Celery worker
celery -A config worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A config beat --loglevel=info
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific test file
pytest apps/authentication/tests.py
```

## 📦 Deployment

### Using Docker Compose (Recommended)

```bash
cd docker
docker-compose up -d
```

### Manual Deployment

1. Set `DJANGO_ENVIRONMENT=production`
2. Update `SECRET_KEY` and database credentials
3. Set `DEBUG=False`
4. Configure `ALLOWED_HOSTS`
5. Run `python manage.py collectstatic`
6. Use gunicorn: `gunicorn config.wsgi:application`

## 🔒 Security Considerations

- Change `SECRET_KEY` in production
- Use strong database passwords
- Enable HTTPS in production
- Keep dependencies updated
- Use environment variables for sensitive data
- Implement rate limiting for API endpoints
- Regular security audits

## 📝 Creating Roles

```python
from apps.authentication.models import Role

# Create roles programmatically
admin_role = Role.objects.create(
    name='Administrator',
    code='ADMIN',
    description='Full system access',
    permissions={
        'users': ['create', 'read', 'update', 'delete'],
        'inventory': ['create', 'read', 'update', 'delete'],
        'sales': ['create', 'read', 'update', 'delete'],
        'finance': ['create', 'read', 'update', 'delete']
    }
)

manager_role = Role.objects.create(
    name='Manager',
    code='MANAGER',
    description='Management access',
    permissions={
        'users': ['read'],
        'inventory': ['read', 'update'],
        'sales': ['create', 'read', 'update']
    }
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📧 Support

For support, email: support@erp-system.com

---

**Built with ❤️ using Django 5.x, DRF, and PostgreSQL**
