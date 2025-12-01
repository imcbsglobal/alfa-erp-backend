#!/bin/bash
# Setup script for Unix/Linux/MacOS
# This script helps set up the Django ERP backend

echo "========================================"
echo "Django ERP Backend Setup"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.12+ and try again"
    exit 1
fi

echo "[1/6] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements/dev.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[4/6] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[INFO] Please edit .env file with your database credentials"
else
    echo "[INFO] .env file already exists, skipping..."
fi

echo "[5/6] Running migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[WARNING] Migration failed. Please check database configuration in .env"
fi

echo "[6/6] Creating superuser..."
echo "Please create an admin user:"
python manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Run: python manage.py migrate (if migrations failed)"
echo "3. Run: python scripts/seed_database.py (optional, for sample data)"
echo "4. Run: python manage.py runserver"
echo ""
echo "Visit: http://localhost:8000/api/docs/"
echo ""
