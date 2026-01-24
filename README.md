# ALFA ERP Backend

Modern Django ASGI backend for ALFA ERP system with real-time updates, JWT authentication, and comprehensive warehouse workflow management.

## 🚀 Features

### Core System
- **ASGI Architecture**: Built on Django's ASGI for async support and real-time capabilities
- **Real-time Updates**: Server-Sent Events (SSE) via django-eventstream for live invoice updates
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Role-Based Access Control**: Menu-based permissions with dynamic access control
- **Email-Based User Management**: Admin-controlled user creation with email as identifier

### Sales & Invoice Management
- **Invoice Import API**: External system integration with duplicate detection
- **Real-time Invoice Streaming**: Live SSE updates pushed to all connected clients
- **Invoice List & Detail**: Paginated API with nested customer, salesman, and items

### Warehouse Workflow
- **Picking Session**: Email-scan workflow to track item picking with session timing
- **Packing Session**: User-verified packing process with status transitions
- **Delivery Management**: Multi-type delivery (DIRECT, COURIER, INTERNAL) with tracking
- **Status Transitions**: Automated invoice state machine (CREATED → PICKED → PACKED → DELIVERED)
- **User Verification**: Email-based identity verification at each workflow stage

### Developer Tools
- **Developer Options**: SUPERADMIN-only database management interface
- **Table Statistics**: Real-time record counts across all tables
- **Data Clearing**: Selective or complete database table truncation
- **Sequence Reset**: Reset auto-increment IDs for clean testing
- **Safety Features**: Transaction-safe with confirmation modals

### Infrastructure
- **PostgreSQL Database**: Production-ready RDBMS with proper indexing
- **Cloudflare R2 Storage**: Optional S3-compatible media storage
- **CORS Ready**: Configurable cross-origin support for frontend integration
- **Modular Architecture**: Apps-based structure for easy extension

## 🛠 Tech Stack

- **Django 5.0.14**: Web framework with ASGI support
- **Uvicorn**: Lightning-fast ASGI server
- **Django REST Framework 3.16**: RESTful API toolkit
- **django-eventstream**: Real-time SSE implementation
- **djangorestframework-simplejwt 5.5**: JWT authentication
- **PostgreSQL 12+**: Primary database
- **Python 3.10+**: Programming language
- **Channels**: ASGI layer support
- **django-cors-headers**: CORS middleware
- **django-storages + boto3**: Cloud storage integration

## 📦 Quick Start

### Prerequisites

- **Python 3.10+**: Required for Django 5.x
- **PostgreSQL 12+**: Primary database
- **pip & virtualenv**: Python package management
- **Uvicorn**: ASGI server (installed via requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/imcbsglobal/alfa-erp-backend
   cd alfa-erp-backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Django
   SECRET_KEY=your-secret-key-here-generate-with-django
   DEBUG=True
   DJANGO_SETTINGS_MODULE=config.settings.development
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database
   DB_NAME=ALFA_ERP
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   
   # CORS - Frontend URLs
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
   
   # JWT Settings (Optional - defaults provided)
   ACCESS_TOKEN_LIFETIME_HOURS=1
   REFRESH_TOKEN_LIFETIME_DAYS=7
   
   # Sales API Key (for external invoice import)
   SALES_IMPORT_API_KEY=your-secure-api-key-here
   
   # Cloudflare R2 (Optional - for production media storage)
   CLOUDFLARE_R2_ENABLED=false
   CLOUDFLARE_R2_ACCESS_KEY=your-access-key
   CLOUDFLARE_R2_SECRET_KEY=your-secret-key
   CLOUDFLARE_R2_BUCKET=your-bucket-name
   CLOUDFLARE_R2_BUCKET_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
   CLOUDFLARE_R2_PUBLIC_URL=your-public-domain.com
   ```

5. **Create PostgreSQL database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE ALFA_ERP ENCODING 'UTF8';
   
   # Exit
   \q
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Seed initial data (optional)**
   ```bash
   # Seed menu access control data
   python manage.py seed_menus
   ```

8. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

9. **Start ASGI development server**
   ```bash
   uvicorn config.asgi:application \
     --reload \
     --host 0.0.0.0 \
     --port 8000
   ```
   
   Or use the convenience script:
   ```bash
   ./run_asgi.sh
   ```

Server will start at `http://localhost:8000`

### Test the Installation

- **Admin Panel**: `http://localhost:8000/admin/`
- **API Root**: `http://localhost:8000/api/`
- **SSE Stream**: `http://localhost:8000/api/sales/sse/invoices/`
- **API Docs**: See `docs/api/` directory

## 📁 Project Structure

```
alfa-erp-backend/
├── apps/                          # Django applications
│   ├── accounts/                  # User authentication & management
│   │   ├── migrations/            # Database migrations
│   │   ├── admin.py              # Django admin config
│   │   ├── models.py             # User, Department, JobTitle models
│   │   ├── serializers.py        # DRF serializers
│   │   ├── urls.py               # API routes
│   │   └── views.py              # API views (login, register, profile)
│   ├── accesscontrol/            # Role-based access control
│   │   ├── management/commands/
│   │   │   └── seed_menus.py    # Seed initial menu data
│   │   ├── models.py             # Menu, MenuAccess models
│   │   ├── serializers.py        # Menu serializers
│   │   └── views.py              # Menu & access API
│   ├── sales/                     # Sales & warehouse workflow
│   │   ├── migrations/
│   │   ├── models.py             # Invoice, InvoiceItem, Customer, Salesman
│   │   │                         # PickingSession, PackingSession, DeliverySession
│   │   ├── serializers.py        # Invoice & workflow serializers
│   │   ├── views.py              # Invoice, Picking, Packing, Delivery APIs
│   │   ├── events.py             # SSE channel configuration
│   │   ├── urls.py               # Sales API routes
│   │   └── tests/                # Unit tests
│   └── common/                    # Shared utilities
│       ├── response.py           # Standardized API responses
│       └── viewsets.py           # Custom viewsets
├── config/                        # Project configuration
│   ├── settings/
│   │   ├── base.py               # Shared settings (ASGI, SSE, CORS, JWT)
│   │   ├── development.py        # Dev-specific settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # Main URL routing
│   ├── wsgi.py                   # WSGI config (legacy)
│   ├── asgi.py                   # ASGI config (primary)
│   └── storage_backends.py       # Custom storage backends
├── docs/                          # Comprehensive documentation
│   ├── api/
│   │   ├── README.md             # API overview
│   │   ├── authentication.md     # Auth endpoints
│   │   ├── users.md              # User management
│   │   ├── sales.md              # Sales & workflow APIs
│   │   ├── menu_access_control.md # Access control API
│   │   └── job_titles.md         # Job titles API
│   ├── ASGI_MIGRATION.md         # WSGI to ASGI migration guide
│   ├── development_setup.md      # Dev environment setup
│   └── adding_new_app.md         # Creating new Django apps
├── media/                         # User uploads (avatars, documents)
│   └── avatars/
├── static/                        # Static files
├── scripts/                       # Utility scripts
│   └── test_login_menus.py       # Test authentication & menus
├── requirements.txt               # Python dependencies
├── manage.py                      # Django management
├── run_asgi.sh                   # ASGI server startup script
├── test_sse.html                 # SSE testing interface
└── .env.example                  # Environment template
```

## 📚 API Documentation

Complete API documentation is available in the `docs/api/` directory:

- **[API Overview](docs/api/README.md)** - Quick start, response format, pagination, filtering
- **[Authentication](docs/api/authentication.md)** - Login, token refresh, logout
- **[User Management](docs/api/users.md)** - User CRUD, profile, password management
- **[Sales & Invoices](docs/api/sales.md)** - Invoice import, SSE streaming, workflow APIs
- **[Access Control](docs/api/menu_access_control.md)** - Menu permissions, role management
- **[Job Titles](docs/api/job_titles.md)** - Job title management

### 🔌 Key API Endpoints

#### Authentication
```bash
# Login
POST /api/auth/login/
Content-Type: application/json
{
  "username": "user@example.com",
  "password": "password123"
}

# Response includes: access_token, refresh_token, user data, menus
```

#### Sales & Invoices
```bash
# List invoices (paginated)
GET /api/sales/invoices/?page=1&page_size=20
Authorization: Bearer <token>

# Import invoice (external systems)
POST /api/sales/import/invoice/
X-API-KEY: your-api-key
Content-Type: application/json
{
  "invoice_no": "INV-001",
  "invoice_date": "2025-12-14",
  "salesman": "John Doe",
  "customer": { ... },
  "items": [ ... ]
}

# Real-time SSE stream
GET /api/sales/sse/invoices/
# Returns: text/event-stream
```

#### Warehouse Workflow
```bash
# Start picking
POST /api/sales/picking/start/
Authorization: Bearer <token>
{
  "invoice_no": "INV-001",
  "user_email": "picker@company.com",
  "notes": "Starting picking"
}

# Complete picking
POST /api/sales/picking/complete/
Authorization: Bearer <token>
{
  "invoice_no": "INV-001",
  "user_email": "picker@company.com",
  "notes": "All items picked"
}

# Similar endpoints for:
# - /api/sales/packing/start/
# - /api/sales/packing/complete/
# - /api/sales/delivery/start/
# - /api/sales/delivery/complete/
```

### 🔄 Real-time Updates (SSE)

Connect to SSE stream for live invoice updates:

```javascript
const eventSource = new EventSource('http://localhost:8000/api/sales/sse/invoices/');

eventSource.onmessage = (event) => {
  const invoice = JSON.parse(event.data);
  console.log('Invoice update:', invoice);
  // Update UI with new invoice data
};

eventSource.onerror = (error) => {
  console.error('SSE connection error:', error);
};
```

Events are automatically pushed when:
- New invoice is imported
- Picking starts/completes
- Packing starts/completes
- Delivery starts/completes

### 📖 Response Format

All API responses follow a consistent format:

**Success:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "message": "Error description",
  "errors": { ... }
}
```

For detailed API documentation with all endpoints, request/response schemas, and integration examples, see the [docs/api/](docs/api/) directory.

## 🏭 Warehouse Workflow

The system implements a complete warehouse fulfillment workflow with user verification at each stage:

### Workflow States

```
CREATED → PENDING → PICKED → PACKING → PACKED → DISPATCHED → DELIVERED
```

### Workflow Steps

1. **Picking** (`PENDING` → `PICKED`)
   - User scans email to start picking session
   - System tracks picker, start time, and session notes
   - User scans email again to complete (verified against starter)
   - Invoice status updated to `PICKED`

2. **Packing** (`PICKED` → `PACKED`)
   - User scans email to start packing session
   - System tracks packer, timing, and status
   - User verification on completion
   - Invoice status updated to `PACKED`

3. **Delivery** (`PACKED` → `DISPATCHED` → `DELIVERED`)
   - Three delivery types:
     - **DIRECT**: Assigned driver (email required)
     - **COURIER**: Third-party courier (courier name required)
     - **INTERNAL**: Internal delivery (email required)
   - Tracking information captured
   - User verification for DIRECT/INTERNAL deliveries
   - Invoice status updated to `DISPATCHED` then `DELIVERED`

### User Verification

All workflow actions require email-based user verification:
- Frontend scans QR code or barcode containing user email
- System validates email exists in database
- System verifies same user completes session they started
- Prevents unauthorized workflow transitions

## 🚀 Deployment

### Production with Uvicorn + Supervisor

1. **Install Supervisor**
   ```bash
   sudo apt install supervisor
   ```

2. **Create supervisor config** (`/etc/supervisor/conf.d/alfa-erp.conf`)
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

3. **Start service**
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start alfa-erp
   ```

### Production with Gunicorn + Uvicorn Workers

```bash
pip install gunicorn uvicorn[standard]

gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --access-logfile - \
  --error-logfile -
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE specific configuration
    location /api/sales/sse/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Required for SSE
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }

    # Static files
    location /static/ {
        alias /path/to/alfa-erp-backend/staticfiles/;
    }

    # Media files
    location /media/ {
        alias /path/to/alfa-erp-backend/media/;
    }
}
```

### Environment Variables (Production)

```env
DEBUG=False
SECRET_KEY=<use-strong-random-key>
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=ALFA_ERP
DB_USER=alfa_erp_user
DB_PASSWORD=<strong-password>
DB_HOST=your-db-host
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# Optional: Cloudflare R2 for media storage
CLOUDFLARE_R2_ENABLED=true
CLOUDFLARE_R2_ACCESS_KEY=<your-key>
CLOUDFLARE_R2_SECRET_KEY=<your-secret>
CLOUDFLARE_R2_BUCKET=alfa-erp-media
CLOUDFLARE_R2_BUCKET_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
CLOUDFLARE_R2_PUBLIC_URL=media.your-domain.com
```

## 🛠 Development

### Daily Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Pull latest changes
git pull origin main

# 3. Install new dependencies (if any)
pip install -r requirements.txt

# 4. Run migrations (if any)
python manage.py migrate

# 5. Start ASGI server
uvicorn config.asgi:application --reload
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.sales

# Run specific test file
python manage.py test apps.sales.tests.test_picking_start

# With coverage
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

### Database Management

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate <app_name> <migration_name>

# Database shell
python manage.py dbshell
```

### Seed Data

```bash
# Seed menu access control data
python manage.py seed_menus
```

## 🔧 Troubleshooting

### SSE Connection Issues

**Problem**: SSE events not received on frontend

**Solutions**:
1. Verify CORS settings include frontend domain
2. Check `EVENTSTREAM_ALLOW_ORIGIN` in settings
3. Ensure Nginx/proxy doesn't buffer SSE responses
4. Use browser dev tools to check EventSource connection

### ASGI Server Won't Start

**Problem**: `NameError` or import errors on uvicorn startup

**Solutions**:
1. Ensure `django-eventstream` is installed: `pip install django-eventstream`
2. Verify `ASGI_APPLICATION` is set in settings
3. Check `config/asgi.py` imports after Django setup
4. Use `--reload` flag only in development

### Database Connection Errors

**Problem**: Can't connect to PostgreSQL

**Solutions**:
1. Verify PostgreSQL is running: `sudo systemctl status postgresql`
2. Check `.env` database credentials
3. Test connection: `psql -U postgres -d ALFA_ERP`
4. Ensure database exists: `CREATE DATABASE ALFA_ERP;`

### Migration Issues

**Problem**: Migration conflicts or errors

**Solutions**:
```bash
# Show migration status
python manage.py showmigrations

# Reset migrations (CAUTION: data loss)
python manage.py migrate <app> zero
python manage.py migrate <app>

# Fake migration (if already applied manually)
python manage.py migrate --fake <app> <migration>
```

## 📝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Create Pull Request

## 📄 License

[Specify your license here]

## 🤝 Support

For issues and questions:
- Check [documentation](docs/)
- Review [API docs](docs/api/)
- Open GitHub issue
- Contact: [your-email@example.com]

## 🔗 Related Projects

- [ALFA ERP Frontend](https://github.com/imcbsglobal/alfa-erp-frontend) - React frontend application

---

Built with ❤️ using Django, ASGI, and modern Python practices.

