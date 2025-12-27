# ALFA ERP Backend - Project Handover Documentation

**Last Updated**: December 2025  
**Version**: 1.0.0

This document provides a comprehensive overview of the ALFA ERP Backend project for handover purposes, including architecture, setup, API documentation, and maintenance guidelines.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Tech Stack](#2-architecture--tech-stack)
3. [Project Structure](#3-project-structure)
4. [Getting Started](#4-getting-started)
5. [Environment Configuration](#5-environment-configuration)
6. [Database Setup](#6-database-setup)
7. [API Overview](#7-api-overview)
8. [Core Features](#8-core-features)
9. [Authentication & Authorization](#9-authentication--authorization)
10. [Warehouse Workflow](#10-warehouse-workflow)
11. [Real-time Updates (SSE)](#11-real-time-updates-sse)
12. [Management Commands](#12-management-commands)
13. [Deployment](#13-deployment)
14. [Testing](#14-testing)
15. [Troubleshooting](#15-troubleshooting)
16. [Documentation Index](#16-documentation-index)
17. [Future Roadmap](#17-future-roadmap)
18. [Contact & Support](#18-contact--support)

---

## 1. Project Overview

**ALFA ERP Backend** is a modern Django ASGI backend for a Pharmacy Management ERP system focused on bulk distribution. The system handles 400+ active billings daily and manages the complete warehouse fulfillment workflow from invoice creation to delivery.

### Key Capabilities
- Invoice import and management from external billing systems
- Real-time SSE updates for live invoice tracking
- Complete warehouse workflow: Picking → Packing → Delivery
- Role-based access control with dynamic menu assignment
- JWT authentication with refresh tokens
- User verification at each workflow stage via email/QR scanning

### Business Flow
```
External System → Invoice Import → Picking → Packing → Delivery
     ↓                                ↓         ↓         ↓
  V-TASK API            Email Scan Verification at Each Stage
```

---

## 2. Architecture & Tech Stack

### Core Technologies

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 5.0.14 |
| API Layer | Django REST Framework | 3.16+ |
| ASGI Server | Uvicorn | Latest |
| Database | PostgreSQL | 12+ |
| Authentication | JWT (simplejwt) | 5.5+ |
| Real-time | django-eventstream (SSE) | Latest |
| CORS | django-cors-headers | Latest |
| Storage | Cloudflare R2 (optional) | - |

### Architecture Pattern
- **ASGI-based**: Supports async operations and long-lived SSE connections
- **Modular Apps**: Separation of concerns with dedicated Django apps
- **RESTful APIs**: Standard REST endpoints with consistent response format
- **Event-Driven**: SSE for real-time invoice updates

---

## 3. Project Structure

```
alfa-erp-backend/
├── apps/                           # Django applications
│   ├── accounts/                   # User management & authentication
│   │   ├── management/commands/    # createstoreuser command
│   │   ├── models.py              # User, Department, JobTitle models
│   │   ├── serializers.py         # User serializers
│   │   ├── views.py               # Auth & user views
│   │   └── urls.py                # Auth routes
│   ├── accesscontrol/             # Menu-based access control
│   │   ├── management/commands/   # seed_menus command
│   │   ├── models.py              # MenuItem, UserMenu models
│   │   ├── views.py               # Menu management views
│   │   └── urls.py                # Access control routes
│   ├── sales/                     # Sales & warehouse workflow
│   │   ├── management/commands/   # seed_invoices, clear_data
│   │   ├── models.py              # Invoice, Session models
│   │   ├── serializers.py         # Invoice/session serializers
│   │   ├── views.py               # Invoice & workflow views
│   │   ├── events.py              # SSE event handling
│   │   └── urls.py                # Sales routes
│   ├── analytics/                 # Analytics (planned)
│   │   └── models.py              # Analytics models
│   └── common/                    # Shared utilities
│       ├── response.py            # Standardized API responses
│       └── viewsets.py            # Custom viewsets
├── config/                        # Project configuration
│   ├── settings/
│   │   ├── base.py               # Shared settings
│   │   ├── development.py        # Dev settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py                   # ASGI application
│   └── storage_backends.py       # R2 storage config
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   └── *.md                      # Feature guides
├── requirements.txt              # Python dependencies
├── manage.py                     # Django management
├── .env.example                  # Environment template
├── README.md                     # Main documentation
├── flow.md                       # Business flow design
└── notes.md                      # Development notes
```

---

## 4. Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Git
- pip & virtualenv

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/imcbsglobal/alfa-erp-backend
cd alfa-erp-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Create database
psql -U postgres -c "CREATE DATABASE ALFA_ERP ENCODING 'UTF8';"

# 6. Run migrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Seed initial data (optional)
python manage.py seed_menus

# 9. Start server
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`

---

## 5. Environment Configuration

Create `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=ALFA_ERP
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# CORS (Frontend URLs)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT Settings
ACCESS_TOKEN_LIFETIME_HOURS=1
REFRESH_TOKEN_LIFETIME_DAYS=7

# External API Key (for invoice import)
SALES_IMPORT_API_KEY=your-secure-api-key

# Cloudflare R2 Storage (Optional)
CLOUDFLARE_R2_ENABLED=false
CLOUDFLARE_R2_ACCESS_KEY=your-access-key
CLOUDFLARE_R2_SECRET_KEY=your-secret-key
CLOUDFLARE_R2_BUCKET=your-bucket-name
CLOUDFLARE_R2_BUCKET_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_PUBLIC_URL=your-public-domain.com
```

---

## 6. Database Setup

### Data Models Overview

**accounts app**:
- `User` - Custom user model with email login, roles, department/job_title
- `Department` - Organization departments
- `JobTitle` - Job positions linked to departments
- `Courier` - Courier/delivery service providers (master data)

**accesscontrol app**:
- `MenuItem` - Navigation menu items (hierarchical)
- `UserMenu` - User-to-menu assignments

**sales app**:
- `Customer` - Customer records
- `Salesman` - Sales personnel
- `Invoice` - Invoice headers
- `InvoiceItem` - Invoice line items
- `InvoiceReturn` - Return/review records
- `PickingSession` - Picking workflow sessions
- `PackingSession` - Packing workflow sessions
- `DeliverySession` - Delivery workflow sessions (references Courier)

### Running Migrations

```bash
# Show migration status
python manage.py showmigrations

# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback specific migration
python manage.py migrate <app_name> <migration_name>
```

---

## 7. API Overview

### Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://alfa-erp-backend.onrender.com`

### Authentication
Most endpoints require JWT authentication:
```
Authorization: Bearer <access_token>
```

### Standard Response Format

**Success**:
```json
{
  "success": true,
  "status_code": 200,
  "message": "Operation successful",
  "data": { ... }
}
```

**Error**:
```json
{
  "success": false,
  "status_code": 400,
  "message": "Error description",
  "errors": { ... }
}
```

### Main API Endpoints

| Category | Endpoint | Description |
|----------|----------|-------------|
| **Auth** | `POST /api/auth/login/` | Login, get JWT + menus |
| **Auth** | `POST /api/auth/token/refresh/` | Refresh access token |
| **Users** | `GET/POST /api/auth/users/` | User management |
| **Users** | `GET /api/auth/users/me/` | Current user profile |
| **Menus** | `GET /api/access-control/menus/` | User's assigned menus |
| **Menus** | `POST /api/access-control/admin/assign-menus/` | Assign menus to user |
| **Invoices** | `GET /api/sales/invoices/` | List invoices (with filters) |
| **Invoices** | `POST /api/sales/import/invoice/` | Import new invoice |
| **SSE** | `GET /api/sales/sse/invoices/` | Real-time invoice stream |
| **Picking** | `POST /api/sales/picking/start/` | Start picking session |
| **Picking** | `POST /api/sales/picking/complete/` | Complete picking |
| **Packing** | `POST /api/sales/packing/start/` | Start packing session |
| **Packing** | `POST /api/sales/packing/complete/` | Complete packing |
| **Delivery** | `POST /api/sales/delivery/start/` | Start delivery |
| **Delivery** | `POST /api/sales/delivery/complete/` | Complete delivery |
| **History** | `GET /api/sales/picking/history/` | Picking session history |
| **History** | `GET /api/sales/packing/history/` | Packing session history |
| **History** | `GET /api/sales/delivery/history/` | Delivery session history |

For complete API documentation, see [docs/api/README.md](api/README.md).

---

## 8. Core Features

### 8.1 Invoice Management
- **Import**: External systems (V-TASK) push invoices via API
- **Duplicate Detection**: Prevents duplicate invoice_no entries
- **Status Tracking**: Full lifecycle from CREATED to DELIVERED
- **Return to Billing**: Invoices can be returned for corrections

### 8.2 User Management
- Email-based authentication
- Role assignment (ADMIN, PICKER, PACKER, DRIVER, BILLING, etc.)
- Department and Job Title assignment
- Activate/deactivate users

### 8.3 Menu Access Control
- Hierarchical menu structure
- Direct user-to-menu assignment
- ADMIN/SUPERADMIN get all menus automatically
- Menus returned at login for frontend rendering

### 8.4 History & Analytics
- Complete session history for picking, packing, delivery
- Duration tracking for each session
- Filtering by status, date range, worker
- Admin vs user-specific views

---

## 9. Authentication & Authorization

### Login Flow
```
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password"
}

Response:
{
  "data": {
    "access": "eyJ...",
    "refresh": "eyJ...",
    "user": { ... },
    "menus": [ ... ]
  }
}
```

### Token Refresh
```
POST /api/auth/token/refresh/
{
  "refresh": "eyJ..."
}
```

### Role-Based Access
- **SUPERADMIN**: Full system access
- **ADMIN**: Full operational access
- **PICKER/PACKER/DRIVER/BILLING**: Role-specific access
- **USER**: Basic access

### Permission Checking
```python
# In views
def is_admin_or_superadmin(user):
    return (
        user.is_staff or 
        user.is_superuser or 
        user.role in ['ADMIN', 'SUPERADMIN']
    )
```

---

## 10. Warehouse Workflow

### Status Flow
```
INVOICED → PICKING → PICKED → PACKING → PACKED → DISPATCHED → DELIVERED
              ↓          ↓          ↓
           REVIEW (returned for corrections)
```

### Picking Workflow
1. User scans email (QR code) to start picking
2. System creates PickingSession, sets invoice to PICKING
3. User picks items from shelves
4. User scans email again to complete
5. System verifies same user, sets status to PICKED

### Packing Workflow
1. Invoice must be in PICKED status
2. User scans email to start packing
3. System creates PackingSession, sets invoice to PACKING
4. User packs items
5. User scans email to complete
6. System sets status to PACKED

### Delivery Workflow
Three delivery types:
- **DIRECT**: Customer counter pickup
- **COURIER**: External courier (with tracking number)
- **INTERNAL**: Company driver delivery

Each type has specific validation rules.

---

## 11. Real-time Updates (SSE)

### SSE Endpoint
```
GET /api/sales/sse/invoices/
```

### Event Types
Events are broadcast on invoice changes:
- New invoice imported
- Picking started/completed
- Packing started/completed
- Delivery started/completed
- Invoice returned to billing

### Client Example
```javascript
const eventSource = new EventSource('http://localhost:8000/api/sales/sse/invoices/');

eventSource.onmessage = (event) => {
  const invoice = JSON.parse(event.data);
  console.log('Invoice update:', invoice);
  // Update UI
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
};
```

### Nginx Configuration for SSE
```nginx
location /api/sales/sse/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding off;
    proxy_buffering off;
    proxy_cache off;
}
```

---

## 12. Management Commands

### User Management
```bash
# Create operational user (picker, packer, etc.)
python manage.py createstoreuser

# Create superuser
python manage.py createsuperuser
```

### Data Seeding
```bash
# Seed menu items
python manage.py seed_menus

# Seed test invoices
python manage.py seed_invoices
python manage.py seed_invoices --count 50
python manage.py seed_invoices --count 30 --with-sessions
python manage.py seed_invoices --count 30 --status INVOICED
```

### Data Cleanup
```bash
# Clear all sales data
python manage.py clear_data
python manage.py clear_data --confirm

# Clear only sessions
python manage.py clear_data --sessions-only --confirm

# Clear only invoices
python manage.py clear_data --invoices-only --confirm
```

---

## 13. Deployment

### Production with Uvicorn + Supervisor

1. Create supervisor config (`/etc/supervisor/conf.d/alfa-erp.conf`):
```ini
[program:alfa-erp]
directory=/path/to/alfa-erp-backend
command=/path/to/venv/bin/uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/alfa-erp/err.log
stdout_logfile=/var/log/alfa-erp/out.log
```

2. Start service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start alfa-erp
```

### Production with Gunicorn
```bash
pip install gunicorn uvicorn[standard]

gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 4
```

### Production Environment Variables
```env
DEBUG=False
SECRET_KEY=<strong-random-key>
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Static Files
```bash
python manage.py collectstatic --noinput
```

---

## 14. Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.sales

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8 .

# Type checking
mypy apps/
```

---

## 15. Troubleshooting

### Common Issues

**SSE events not received**:
- Check CORS settings include frontend domain
- Verify EVENTSTREAM_ALLOW_ORIGIN in settings
- Ensure Nginx doesn't buffer SSE responses

**ASGI server won't start**:
- Ensure django-eventstream is installed
- Verify ASGI_APPLICATION in settings
- Check config/asgi.py imports after Django setup

**Database connection errors**:
- Verify PostgreSQL is running
- Check .env database credentials
- Test: `psql -U postgres -d ALFA_ERP`

**Migration issues**:
```bash
python manage.py showmigrations
python manage.py migrate --fake <app> <migration>
```

---

## 16. Documentation Index

### API Documentation
| Document | Description |
|----------|-------------|
| [docs/api/README.md](api/README.md) | API overview & quick start |
| [docs/api/authentication.md](api/authentication.md) | Auth endpoints |
| [docs/api/users.md](api/users.md) | User management |
| [docs/api/sales.md](api/sales.md) | Sales, workflow & courier APIs |
| [docs/api/billing.md](api/billing.md) | Billing API |
| [docs/api/menu_access_control.md](api/menu_access_control.md) | Menu control API |
| [docs/api/job_titles.md](api/job_titles.md) | Departments & job titles |
| [docs/api/V-TASK_import_invoice.md](api/V-TASK_import_invoice.md) | External invoice import |

### Feature Documentation
| Document | Description |
|----------|-------------|
| [docs/development_setup.md](development_setup.md) | Development environment setup |
| [docs/ASGI_MIGRATION.md](ASGI_MIGRATION.md) | WSGI to ASGI migration guide |
| [docs/adding_new_app.md](adding_new_app.md) | Creating new Django apps |
| [docs/menu_access_control.md](menu_access_control.md) | Menu access control system |
| [docs/HISTORY_FEATURE_IMPLEMENTATION.md](HISTORY_FEATURE_IMPLEMENTATION.md) | History feature guide |
| [docs/HISTORY_QUICK_START.md](HISTORY_QUICK_START.md) | History quick start |
| [docs/BILLING_QUICK_REFERENCE.md](BILLING_QUICK_REFERENCE.md) | Billing quick reference |
| [docs/QUERY_FILTERING_IMPLEMENTATION.md](QUERY_FILTERING_IMPLEMENTATION.md) | Query filtering guide |
| [docs/WORKER_FILTERING_IMPLEMENTATION.md](WORKER_FILTERING_IMPLEMENTATION.md) | Worker filtering guide |
| [docs/createstoreuser.md](createstoreuser.md) | Store user creation command |
| [docs/seed_and_clear_data.md](seed_and_clear_data.md) | Data seeding commands |
| [docs/invoice_import.md](invoice_import.md) | Invoice import behavior |

### Root Documents
| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Main project documentation |
| [flow.md](../flow.md) | Business flow & workflow design |
| [notes.md](../notes.md) | Development notes |

---

## 17. Future Roadmap

### Planned Features
- [ ] Analytics dashboard endpoints
- [ ] CSV/PDF export functionality
- [ ] WebSocket support for bi-directional communication
- [ ] Rate limiting on API endpoints
- [ ] API versioning (v2)
- [ ] Inventory management module
- [ ] Purchase order management
- [ ] Payment follow-up module

### Suggested Improvements
- Add Redis-backed pub/sub for multi-instance SSE
- Implement audit logging
- Add bulk operations for menu/user management
- Implement push notifications
- Add mobile app API optimizations

---

## 18. Contact & Support

### Repository
- **GitHub**: https://github.com/imcbsglobal/alfa-erp-backend

### Related Projects
- **Frontend**: [ALFA ERP Frontend](https://github.com/imcbsglobal/alfa-erp-frontend)

### Getting Help
1. Check documentation in `docs/` folder
2. Review API docs in `docs/api/`
3. Check troubleshooting section above
4. Open GitHub issue for bugs/features

---

*This handover document was generated on December 2025. For the latest information, always refer to the repository documentation.*
