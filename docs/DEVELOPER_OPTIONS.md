# Developer Options - Frontend View Management

## Overview
The Developer Options page provides SUPERADMIN users with tools to clear data from the frontend view and view database statistics.

ℹ️ **NOTE**: Clear operations only affect the frontend display. Data remains in the database and is not deleted.

---

## Access Control

### Who Can Access:
- **SUPERADMIN ONLY**
- Menu item hidden from all other roles
- Backend API enforces `SuperAdminOnlyPermission`

### Frontend:
- Route: `/developer/settings`
- Menu: "Developer Options" (visible only to SUPERADMIN)
- Icon: Database icon

### Backend:
- Permission Class: `SuperAdminOnlyPermission`
- Inherits from `IsAuthenticated`
- Checks `request.user.role == 'SUPERADMIN'`

---

## Features

### 1. **Table Statistics**
View record counts for all database tables:
- Invoices & Items
- Sessions (Picking, Packing, Delivery)
- Customers, Salesmen, Couriers
- Users, Departments, Job Titles
- Total record count across all tables

**Endpoint:**
```http
GET /api/developer/table-stats/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "invoices": {
      "count": 150,
      "description": "Sales invoices/orders"
    },
    "customers": {
      "count": 45,
      "description": "Customer records"
    },
    ...
  },
  "total_records": 1250
}
```

---

### 2. **Clear Data from View**
Clear data from the frontend view only. Database remains unchanged.

**Endpoint:**
```http
POST /api/developer/clear-data/
Authorization: Bearer <token>
Content-Type: application/json

{
  "table_name": "invoices"
}
```

**Available Table Names:**

#### Sales & Operations:
- **`all`** - Clear ALL data from view
  - ℹ️ Database unchanged
  - Returns counts of all records
  
- **`invoices`** - Clear invoices from view
  - Shows invoice and related item counts
  - Database data intact
  
- **`picking_sessions`** - Clear picking sessions from view
  - Shows picking session counts
  - Database unchanged
  
- **`packing_sessions`** - Clear packing sessions from view
  - Shows packing session counts
  - Database unchanged
  
- **`delivery_sessions`** - Clear delivery sessions from view
  - Shows delivery session counts
  - Database unchanged
  
- **`sessions`** - Clear all sessions from view (backward compatibility)
  - Shows all picking, packing, and delivery session counts
  - Database unchanged
  
- **`customers`** - Clear customer records from view
  - Database unchanged
  
- **`salesmen`** - Clear salesman records from view
  - Database unchanged
  
- **`couriers`** - Clear courier service providers from view
  - Database unchanged

#### Users & Organization:
- **`users`** - Clear non-SUPERADMIN users from view
  - Shows count of non-SUPERADMIN users
  - Database unchanged
  
- **`departments`** - Clear departments from view
  - Database unchanged
  
- **`job_titles`** - Clear job titles from view
  - Database unchanged

**Response:**
```json
{
  "success": true,
  "message": "Invoices cleared from view (database unchanged)",
  "deleted_counts": {
    "invoices": 150,
    "invoice_items": 450
  },
  "note": "Data cleared from frontend view only. Database remains unchanged."
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Invalid table name: xyz"
}
```

---

### 3. **Reset Sequences**
Reset PostgreSQL auto-increment sequences to start from 1.

**Endpoint:**
```http
POST /api/developer/reset-sequences/
Authorization: Bearer <token>
```

**When to Use:**
- After clearing all data
- To restart IDs from 1
- Database maintenance

**Response:**
```json
{
  "success": true,
  "message": "Reset 15 database sequences",
  "reset_count": 15
}
```

**Note:** Some sequences might be skipped if actively in use.

---

## Frontend UI

### Page Layout:

```
┌─────────────────────────────────────────────────┐
│  ⚠️  Developer Options                         │
│     Database maintenance and data clearing      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  ⚠️ Danger Zone - SUPERADMIN Only               │
│  Operations are irreversible. Backup first!     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  Total Records: 1,250                           │
│  Invoices: 150    Users: 25                     │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  🔄 Refresh Stats    ⚙️ Reset Sequences         │
└─────────────────────────────────────────────────┘

┌─ Sales & Operations ─────────────────────────────┐
│  📦 All Data (DANGER)         1,250  [Clear]     │
│  📋 Invoices                    150  [Clear]     │
│  🔄 Sessions                    300  [Clear]     │
│  👥 Customers                    45  [Clear]     │
│  💼 Salesmen                     12  [Clear]     │
│  🚚 Couriers                      8  [Clear]     │
└──────────────────────────────────────────────────┘

┌─ Users & Organization ───────────────────────────┐
│  👤 Users                        25  [Clear]     │
│  🏢 Departments                   5  [Clear]     │
│  💼 Job Titles                   10  [Clear]     │
└──────────────────────────────────────────────────┘
```

### Confirmation Modal:
```
┌─────────────────────────────────────┐
│  ℹ️  Confirm View Clear              │
├─────────────────────────────────────┤
│  ℹ️ Frontend View Only             │
│  This will clear: Invoices          │
│  from your frontend view only.      │
│  Database remains intact.           │
│                                     │
│  Type CLEAR to confirm:             │
│  [_____________________]            │
│                                     │
│  [Cancel]  [Clear View]             │
└─────────────────────────────────────┘
```

**UI Features:**
- Real-time record counts from database
- Color-coded categories
- Disabled buttons when count = 0
- Blue info banners
- Type-to-confirm action (type "CLEAR")
- Loading states
- Success/error toasts
- View-only operations (database unchanged)

---

## Safety Features

### Backend Protections:

1. **Permission Check**
   - Only SUPERADMIN can access
   - Returns 403 Forbidden otherwise

2. **No Database Modification**
   - Clear operations only return counts
   - Database remains unchanged
   - Read-only operations

3. **Statistics Display**
   - Shows current database state
   - No data modification

### Frontend Protections:

1. **Role Check**
   - Menu hidden for non-SUPERADMIN
   - Route protected

2. **Confirmation Modal**
   - User must type "CLEAR"
   - Case-sensitive validation

3. **Info Banners**
   - Clear messaging about view-only operations
   - Blue color scheme for info

4. **Disabled States**
   - Clear button disabled when count = 0
   - Loading states during operations

---

## View Operations

### How It Works:

**Clear Operations:**
- Frontend calls backend API
- Backend returns current database counts
- No data is modified or deleted
- Frontend receives confirmation message
- Statistics reflect actual database state

**Statistics:**
- Real-time count queries
- No caching
- Accurate database state

---

## Common Operations

### View All Data Counts:
```bash
# Backend
GET /api/developer/table-stats/
```

### Clear Invoices from View:
```bash
POST /api/developer/clear-data/
Body: { "table_name": "invoices" }
# Returns counts, database unchanged
```

### Clear Sessions from View:
```bash
POST /api/developer/clear-data/
Body: { "table_name": "sessions" }
# Returns counts, database unchanged
```

### Clear All from View:
```bash
POST /api/developer/clear-data/
Body: { "table_name": "all" }
# Returns all counts, database unchanged
```

---

## Testing Checklist

### Backend API:
- [ ] `GET /api/developer/table-stats/` returns stats
- [ ] Non-SUPERADMIN gets 403 Forbidden
- [ ] `POST /api/developer/clear-data/` returns counts (no deletion)
- [ ] `POST /api/developer/clear-data/` with "all" returns all counts
- [ ] All operations read-only
- [ ] `POST /api/developer/reset-sequences/` works

### Frontend UI:
- [ ] Page only visible to SUPERADMIN
- [ ] Statistics load correctly
- [ ] Refresh button updates stats
- [ ] Clear buttons show confirmation modal
- [ ] Must type "CLEAR" to confirm
- [ ] Success toast on completion
- [ ] Error toast on failure
- [ ] Blue info styling (not red danger)
- [ ] Reset sequences button works
- [ ] Loading states shown

---

## Error Handling

### Backend Errors:

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Invalid table name: xyz"
}
```

**400 Bad Request:**
```json
{
  "success": false,
  "message": "Invalid table name: xyz"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Error clearing view: <error details>"
}
```

### Frontend Errors:
- Toast notifications for all errors
- Network errors caught and displayed
- Loading states cleared on error

---

## Best Practices

### Using the Tool:

1. **View Statistics**
   - Check current database state
   - Monitor record counts
   - Verify data integrity

2. **Clear Operations**
   - Understand these are view-only
   - Database remains unchanged
   - Use for UI testing/debugging

3. **Refresh Stats**
   - Click refresh to update counts
   - Verify current state
   - Monitor changes

### When to Use:

1. **Testing UI behavior**
   - See how UI responds to "cleared" state
   - Test empty state handling

2. **Debugging**
   - Check record counts
   - Verify data exists
   - Monitor statistics

3. **Development**
   - Quick database stats
   - No risk of data loss
   - Safe operations

---

## Files Modified

### Backend:
```
apps/
├── common/
│   ├── developer.py          # NEW: API views
│   └── urls.py               # NEW: Developer URLs
config/
└── urls.py                   # MODIFIED: Added common URLs
```

### Frontend:
```
src/
├── pages/
│   └── DeveloperSettingsPage.jsx    # NEW: UI component
├── app/
│   └── router.jsx                   # MODIFIED: Added route
└── layout/Sidebar/
    └── menuConfig.js                 # MODIFIED: Added menu item
```

---

## Security Considerations

1. **Access Control:**
   - ✅ SUPERADMIN only access
   - Backend permission enforcement
   - Frontend route protection

2. **Read-Only Operations:**
   - No data modification
   - Safe for production
   - View database statistics only

3. **Audit Logging:**
   - Consider logging stats queries
   - Monitor SUPERADMIN actions
   - Track access patterns

---

## Future Enhancements

### Potential Features:
1. Export data to CSV/JSON
2. Import data from file
3. Data analytics dashboard
4. Record comparison tool
5. Query builder interface
6. Custom statistics views
7. Data visualization charts
8. Scheduled reports
9. Activity audit log
10. API usage statistics

---

**Created:** January 24, 2026
**Updated:** January 30, 2026
**Status:** ✅ View-Only Mode
**Risk Level:** 🟢 LOW - Read-only operations, safe for all environments
