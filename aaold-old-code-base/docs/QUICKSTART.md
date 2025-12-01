# Quick Start Guide

## Prerequisites

- Python 3.12 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher (for Celery)
- Git

## Installation Steps

### 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd alfa-erp-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt
```

### 2. Database Setup

```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE erp_db;
CREATE USER erp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE erp_db TO erp_user;
\q
```

### 3. Environment Configuration

```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
# Update DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY
```

### 4. Run Migrations

```bash
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Seed Database (Optional)

```bash
# Populate with sample data
python scripts/seed_database.py
```

This creates:
- Default roles (ADMIN, MANAGER, FINANCE, SALES, INVENTORY)
- Admin user: `admin` / `admin123`
- Manager user: `manager` / `manager123`
- Sample departments, products, customers, accounts

### 6. Run Development Server

```bash
# Start Django server
python manage.py runserver

# In another terminal, start Celery (optional)
celery -A config worker --loglevel=info

# In another terminal, start Celery Beat (optional)
celery -A config beat --loglevel=info
```

### 7. Access the Application

- **API Base**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Docs (Swagger)**: http://localhost:8000/api/docs/
- **API Docs (ReDoc)**: http://localhost:8000/api/redoc/

## Docker Setup (Alternative)

```bash
# Copy environment file
copy .env.example .env

# Build and start containers
cd docker
docker-compose up --build -d

# Create superuser
docker exec -it erp_backend python manage.py createsuperuser

# Seed database (optional)
docker exec -it erp_backend python scripts/seed_database.py

# View logs
docker-compose logs -f
```

## Testing the API

### 1. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

Response will include:
- User information
- JWT tokens (access and refresh)
- User roles (for frontend navigation)
- Permissions

### 2. Use Access Token

```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Create a Role

```bash
curl -X POST http://localhost:8000/api/auth/roles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Sales Manager\",
    \"code\": \"SALES_MGR\",
    \"description\": \"Manages sales operations\",
    \"permissions\": {
      \"sales\": [\"create\", \"read\", \"update\"],
      \"inventory\": [\"read\"]
    }
  }"
```

## Common Tasks

### Create a new app

```bash
python manage.py startapp myapp apps/myapp
```

Then:
1. Add to `INSTALLED_APPS` in `config/settings/base.py`
2. Create models, serializers, views
3. Add URL configuration
4. Register in admin

### Run migrations after model changes

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collect static files

```bash
python manage.py collectstatic
```

### Create admin user

```bash
python manage.py createsuperuser
```

### Run tests

```bash
pytest
# or with coverage
pytest --cov=apps
```

## Frontend Integration

### Example: React/JavaScript

```javascript
// 1. Login
const login = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
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
  throw new Error(data.message);
};

// 2. Make authenticated requests
const fetchData = async (endpoint) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/api/${endpoint}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
};

// 3. Control navigation based on roles
const userRoles = JSON.parse(localStorage.getItem('user_roles') || '[]');

const canAccessFinance = userRoles.includes('ADMIN') || 
                         userRoles.includes('FINANCE');

if (canAccessFinance) {
  // Show finance menu
}
```

## Troubleshooting

### Port already in use

```bash
# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On Unix/MacOS
lsof -ti:8000 | xargs kill -9
```

### Database connection error

1. Check PostgreSQL is running
2. Verify credentials in `.env`
3. Ensure database exists

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements/dev.txt --force-reinstall
```

### Celery not running

1. Check Redis is running: `redis-cli ping`
2. Check Celery broker URL in `.env`
3. Restart Celery worker

## Next Steps

1. Read the [API Documentation](docs/API_DOCUMENTATION.md)
2. Review [Code Documentation](docs/CODE_DOCUMENTATION.md)
3. Customize models for your needs
4. Add business logic
5. Create tests
6. Deploy to production

## Useful Commands

```bash
# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Show migrations
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run tests
pytest

# Code formatting
black .
isort .

# Linting
flake8
pylint apps/
```

## Production Deployment

1. Set `DJANGO_ENVIRONMENT=production`
2. Change `SECRET_KEY`
3. Set `DEBUG=False`
4. Configure `ALLOWED_HOSTS`
5. Setup SSL/HTTPS
6. Use gunicorn: `gunicorn config.wsgi:application`
7. Setup Nginx reverse proxy
8. Configure PostgreSQL backups
9. Setup monitoring (Sentry, etc.)
10. Use Docker Compose for deployment

For detailed deployment instructions, see the main README.md

---

**Need Help?** Check the documentation or create an issue on GitHub.
