# Development Setup Guide

Complete guide for setting up your development environment for ALFA ERP Backend.

## Prerequisites

### Required Software

1. **Python 3.10 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify: `python --version`

2. **PostgreSQL 12 or higher**
   - Download from [postgresql.org](https://www.postgresql.org/download/)
   - Verify: `psql --version`

3. **Git**
   - Download from [git-scm.com](https://git-scm.com/)
   - Verify: `git --version`

4. **pip** (usually comes with Python)
   - Verify: `pip --version`
   - Update: `python -m pip install --upgrade pip`

### Recommended Tools

- **VS Code** or **PyCharm**: IDE with Python support
- **Postman** or **HTTPie**: API testing
- **pgAdmin** or **DBeaver**: Database management GUI
- **Git GUI** (optional): SourceTree, GitKraken, or GitHub Desktop

## Initial Setup

### 1. Clone Repository

```bash
# Clone the repo
git clone <repository-url>
cd alfa-erp-backend


# Create a new branch for your work
git checkout -b feature/your-feature-name

```

### 2. Set Up Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Verify activation (you should see (venv) in prompt)
```

**Linux/Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify activation (you should see (venv) in prompt)
```

To deactivate later:
```bash
deactivate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

If you encounter errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### 4. Configure Environment Variables

Create `.env` file from template:

```bash
# Copy template
cp .env.example .env

# Edit with your preferred editor
# Windows: notepad .env
# Linux/Mac: nano .env or vim .env
```

Required environment variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-generate-a-strong-one
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=ALFA_ERP
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432

# CORS (Frontend URLs)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000

# JWT (Optional - defaults are fine for development)
ACCESS_TOKEN_LIFETIME_HOURS=1
REFRESH_TOKEN_LIFETIME_DAYS=7
```


### 5. Set Up PostgreSQL Database

**Option A: Command Line**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ALFA_ERP ENCODING 'UTF8';

# Create user (if not using postgres user)
CREATE USER alfa_user WITH PASSWORD 'your-password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ALFA_ERP TO alfa_user;

# Exit
\q
```

**Option B: pgAdmin GUI**

1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `ALFA_ERP`
4. Encoding: `UTF8`
5. Click "Save"

**Verify connection:**
```bash
python manage.py dbshell
# Should connect to database
# Exit with: \q
```

### 6. Run Migrations

```bash
# Create initial migrations (if needed)
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify
python manage.py showmigrations
```

Expected output: All migrations should show `[X]` (applied).

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Enter:
- Email: `admin@example.com` (or your email)
- Password: (enter twice, min 8 characters)

### 8. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 9. Run Development Server

```bash
uvicorn config.asgi:application \
   --reload \
   --timeout-graceful-shutdown 1
```
```
uvicorn config.asgi:application --host 0.0.0.0 --port 8000

```
Server starts at: `http://localhost:8000`

Test endpoints:
- Admin: `http://localhost:8000/admin/`
- API Root: `http://localhost:8000/api/`
- Login: `http://localhost:8000/api/auth/login/`


### Daily Workflow

1. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

3. **Install new dependencies (if any):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations (if any new ones):**
   ```bash
   python manage.py migrate
   ```

5. **Start development server:**
   ```bash
uvicorn config.asgi:application \
  --reload \
  --timeout-graceful-shutdown 1
   ```

### Before Committing

1. **Format code:**
   ```bash
   black .
   isort .
   ```

## Testing API Endpoints