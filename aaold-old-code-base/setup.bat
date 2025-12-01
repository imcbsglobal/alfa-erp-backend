@echo off
REM Setup script for Windows
REM This script helps set up the Django ERP backend

echo ========================================
echo Django ERP Backend Setup
echo ========================================
echo.

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.12+ and try again
    pause
    exit /b 1
)

echo [1/6] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install --upgrade pip
pip install -r requirements\dev.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo [INFO] Please edit .env file with your database credentials
) else (
    echo [INFO] .env file already exists, skipping...
)

echo [5/6] Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [WARNING] Migration failed. Please check database configuration in .env
)

echo [6/6] Creating superuser...
echo Please create an admin user:
python manage.py createsuperuser

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your database credentials
echo 2. Run: python manage.py migrate (if migrations failed)
echo 3. Run: python scripts\seed_database.py (optional, for sample data)
echo 4. Run: python manage.py runserver
echo.
echo Visit: http://localhost:8000/api/docs/
echo.
pause
