#!/bin/bash

# ASGI Server Startup Script for ALFA ERP Backend
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ALFA ERP Backend - ASGI Server${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
    echo -e "${YELLOW}Consider activating your venv first${NC}\n"
fi

# Check for required packages
echo -e "Checking dependencies..."
python -c "import uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: uvicorn not installed${NC}"
    echo -e "Run: pip install uvicorn"
    exit 1
fi

python -c "import django_eventstream" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: django-eventstream not installed${NC}"
    echo -e "Run: pip install django-eventstream"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies found${NC}\n"

# Set environment
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"config.settings.development"}

# Server configuration
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-"8000"}
WORKERS=${WORKERS:-"1"}

echo -e "Starting server with configuration:"
echo -e "  Settings: ${GREEN}$DJANGO_SETTINGS_MODULE${NC}"
echo -e "  Host:     ${GREEN}$HOST${NC}"
echo -e "  Port:     ${GREEN}$PORT${NC}"
echo -e "  Workers:  ${GREEN}$WORKERS${NC}\n"

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${RED}Error: Port $PORT is already in use${NC}"
    echo -e "Kill existing process or choose a different port:"
    echo -e "  PORT=8001 ./run_asgi.sh"
    exit 1
fi

echo -e "${GREEN}Starting Uvicorn server...${NC}\n"
echo -e "SSE Endpoint: http://$HOST:$PORT/api/sales/sse/invoices/"
echo -e "API Base:     http://$HOST:$PORT/api/"
echo -e "\nPress CTRL+C to stop\n"

# Start the server
if [ "$WORKERS" -eq 1 ]; then
    # Single worker with hot reload (development)
    uvicorn config.asgi:application \
        --host $HOST \
        --port $PORT \
        --reload \
        --reload-dir apps \
        --reload-dir config \
        --log-level info
else
    # Multiple workers (production-like)
    uvicorn config.asgi:application \
        --host $HOST \
        --port $PORT \
        --workers $WORKERS \
        --log-level info
fi
