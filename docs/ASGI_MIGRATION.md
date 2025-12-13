# ASGI Migration Guide

This document explains the migration from WSGI to ASGI and the implementation of Server-Sent Events (SSE) using `django-eventstream`.

## Changes Made

### 1. Configuration Updates

#### settings/base.py
- Added `django_eventstream` to `INSTALLED_APPS`
- Added `ASGI_APPLICATION = 'config.asgi.application'`
- Added eventstream configuration:
  ```python
  EVENTSTREAM_ALLOW_ORIGIN = '*'
  EVENTSTREAM_ALLOW_CREDENTIALS = True
  ```

#### config/asgi.py
- Updated to handle both regular HTTP requests and SSE connections
- Integrated `django_eventstream` for SSE handling

### 2. Event System Refactored

#### apps/sales/events.py
- **Before**: Used Python's `queue.Queue()` for event handling
- **After**: Uses django-eventstream channels
- Channel name: `'invoices'`

#### apps/sales/views.py
- Removed custom `invoice_stream()` function
- Replaced all `invoice_events.put()` calls with `django_eventstream.send_event()`
- Updated imports to remove `queue` and add `django_eventstream`

#### apps/sales/urls.py
- Replaced custom SSE endpoint with django-eventstream URL pattern
- URL: `/api/sales/sse/invoices/` now handled by django-eventstream

## Running the Server

### Development with Uvicorn

```bash
# Using uvicorn directly
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000

# Or with custom settings
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000 --env-file .env
```

### Alternative: Daphne (Django Channels ASGI Server)

```bash
# Install daphne (optional)
pip install daphne

# Run with daphne
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Development Server (Basic Testing Only)

```bash
# Django's built-in server has basic ASGI support
python manage.py runserver
```

**Note**: Django's `runserver` has limited ASGI support. For production-like testing, use Uvicorn or Daphne.

## SSE Client Connection

### Frontend JavaScript Example

```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('http://localhost:8000/api/sales/sse/invoices/');

eventSource.onmessage = function(event) {
    const invoice = JSON.parse(event.data);
    console.log('Invoice update:', invoice);
    
    // Update your UI with the new invoice data
    updateInvoiceList(invoice);
};

eventSource.onerror = function(error) {
    console.error('SSE Error:', error);
};

// Close connection when done
// eventSource.close();
```

### Testing with cURL

```bash
curl -N http://localhost:8000/api/sales/sse/invoices/
```

## How Events Are Sent

When any of these actions occur, an SSE event is automatically sent:
1. New invoice imported (`POST /api/sales/import/invoice/`)
2. Picking started (`POST /api/sales/picking/start/`)
3. Picking completed (`POST /api/sales/picking/complete/`)
4. Packing started (`POST /api/sales/packing/start/`)
5. Packing completed (`POST /api/sales/packing/complete/`)
6. Delivery started (`POST /api/sales/delivery/start/`)
7. Delivery completed (`POST /api/sales/delivery/complete/`)

Example of sending an event in code:

```python
from .events import INVOICE_CHANNEL
import django_eventstream

# Send event to all connected clients
django_eventstream.send_event(
    INVOICE_CHANNEL,     # Channel name
    'message',           # Event type
    invoice_data         # Data (will be JSON serialized)
)
```

## Production Deployment

### With Uvicorn + Supervisor

Create `/etc/supervisor/conf.d/alfa-erp.conf`:

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

### With Gunicorn + Uvicorn Worker

```bash
pip install gunicorn uvicorn[standard]

gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4
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
    }

    # SSE specific configuration
    location /api/sales/sse/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE requires these headers
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## Benefits of ASGI + django-eventstream

1. **Better SSE Support**: Native ASGI support for long-lived connections
2. **Scalability**: Can handle more concurrent connections
3. **Standards-Based**: Uses django-eventstream which is maintained and tested
4. **Channel Support**: Easy to add multiple channels for different event types
5. **Async Ready**: Foundation for adding async views and WebSocket support in the future

## Troubleshooting

### Events not received on frontend
- Check CORS settings in `settings/base.py`
- Verify `EVENTSTREAM_ALLOW_ORIGIN` includes your frontend domain
- Check browser console for connection errors

### Server won't start
- Ensure `django-eventstream` is installed: `pip install django-eventstream`
- Verify `uvicorn` is installed: `pip install uvicorn`
- Check for syntax errors in `config/asgi.py`

### Old queue-based events
- All old `invoice_events.put()` calls have been replaced
- The `queue` module is no longer used
- Old `invoice_stream()` function has been removed

## Next Steps

Consider these enhancements:
1. Add authentication to SSE endpoint (currently open)
2. Create additional channels for different event types
3. Add event filtering based on user permissions
4. Implement reconnection logic on frontend
5. Add heartbeat/keepalive configuration
6. Consider adding WebSocket support for bi-directional communication
