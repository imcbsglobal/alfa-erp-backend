# ALFA ERP Backend

Django REST Framework backend for ALFA ERP system with JWT authentication and admin-managed users.

## Features

- **Custom User Authentication**: Email-based login with JWT tokens
- **Admin-Only User Creation**: No self-registration; all users created by admins
- **Role-Based Access Control**: Django groups as roles, returned in login response
- **User Profile Management**: Avatar uploads, profile updates, password changes
- **RESTful API**: Clean REST endpoints with Django REST Framework
- **PostgreSQL Database**: Production-ready database setup
- **Modular Architecture**: Easy to extend with new apps

## Tech Stack

- **Django 5.0.14**: Web framework
- **Django REST Framework**: API toolkit
- **djangorestframework-simplejwt**: JWT authentication
- **PostgreSQL**: Database
- **Python 3.10+**: Programming language

## Quick Start

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 12 or higher
- pip and virtualenv

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
   
   Copy `.env.example` to `.env` and update:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   # Django
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DJANGO_SETTINGS_MODULE=config.settings.development
   
   # Database
   DB_NAME=ALFA_ERP
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   
   # CORS
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
   ```

5. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE ALFA_ERP ENCODING 'UTF8';
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Server will start at `http://localhost:8000`

## Project Structure

```
alfa-erp-backend/
├── apps/                      # Django applications
│   ├── accounts/              # User authentication and management
│   │   ├── migrations/
│   │   ├── admin.py          # Django admin configuration
│   │   ├── apps.py           # App configuration
│   │   ├── models.py         # User model
│   │   ├── serializers.py    # API serializers
│   │   ├── urls.py           # URL routing
│   │   └── views.py          # API views
│   ├── accesscontrol/         # (Future) RBAC module
│   └── __init__.py
├── config/                    # Project configuration
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── development.py    # Dev settings
│   │   └── production.py     # Production settings
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py               # WSGI config
│   └── asgi.py               # ASGI config
├── docs/                      # Documentation
│   ├── api/                  # API documentation
│   │   ├── README.md         # API overview and quick start
│   │   ├── authentication.md # Login and token endpoints
│   │   └── users.md          # User management endpoints
│   ├── adding_new_app.md     # Guide for creating new apps
│   ├── development_setup.md  # Development environment setup
│   └── response_handlers.md  # API response format guide
├── media/                     # User-uploaded files
│   └── avatars/              # User profile photos
├── static/                    # Static files (CSS, JS, images)
├── requirements.txt           # Python dependencies (all-in-one)
├── scripts/                   # Utility scripts
├── manage.py                  # Django management script
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## API Documentation

Complete API documentation is available in the `docs/api/` directory:

- **[API Overview](docs/api/README.md)** - Quick start, response format, pagination, filtering
- **[Authentication API](docs/api/authentication.md)** - Login, token refresh endpoints
- **[User Management API](docs/api/users.md)** - User CRUD operations, profile, password management

### Quick API Examples

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@gmail.com","password":"admin@123"}'
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/auth/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

For complete API documentation with all endpoints, request/response examples, and integration guides, see [docs/api/README.md](docs/api/README.md).

