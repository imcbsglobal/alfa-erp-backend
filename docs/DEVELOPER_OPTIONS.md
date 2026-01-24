# Developer Options - Database Management

## Overview
The Developer Options page provides SUPERADMIN users with database maintenance tools to clear/truncate tables and view database statistics.

⚠️ **WARNING**: These operations are irreversible and permanently delete data. Use with extreme caution!

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

### 2. **Clear Data**
Permanently delete records from specific tables or all data.

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
- **`all`** - Clear ALL data (invoices, customers, sessions, salesmen, couriers)
  - ⚠️ **DANGER**: Clears everything!
  - Cascade deletes all related records
  
- **`invoices`** - All invoices and related data
  - Deletes invoices (cascade handles items, sessions, returns)
  
- **`sessions`** - All session data (picking, packing, delivery)
  - Keeps invoices intact
  - Clears DeliverySession, PackingSession, PickingSession
  
- **`customers`** - All customer records
  - ❌ Fails if invoices exist (foreign key constraint)
  - Clear invoices first
  
- **`salesmen`** - All salesman records
  
- **`couriers`** - All courier service providers

#### Users & Organization:
- **`users`** - All non-SUPERADMIN users
  - ✅ Keeps at least one SUPERADMIN
  - Prevents system lockout
  
- **`departments`** - All departments
  
- **`job_titles`** - All job title definitions

**Response:**
```json
{
  "success": true,
  "message": "All invoices and related data cleared",
  "deleted_counts": {
    "invoices": 150,
    "invoice_items": 450,
    "picking_sessions": 120,
    "packing_sessions": 100,
    "delivery_sessions": 80
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Cannot delete customers while invoices exist. Clear invoices first."
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
│  ⚠️  Confirm Data Deletion          │
├─────────────────────────────────────┤
│  ⚠️ This action cannot be undone!   │
│  You are about to permanently       │
│  delete: Invoices                   │
│                                     │
│  Type DELETE to confirm:            │
│  [_____________________]            │
│                                     │
│  [Cancel]  [Delete Permanently]     │
└─────────────────────────────────────┘
```

**UI Features:**
- Real-time record counts
- Color-coded categories
- Disabled buttons when count = 0
- Red warning banners
- Type-to-confirm deletion
- Loading states
- Success/error toasts

---

## Safety Features

### Backend Protections:

1. **Permission Check**
   - Only SUPERADMIN can access
   - Returns 403 Forbidden otherwise

2. **Transaction Safety**
   - All operations wrapped in `transaction.atomic()`
   - Rollback on any error

3. **Dependency Validation**
   - Prevents deleting customers if invoices exist
   - Prevents deleting all users (keeps SUPERADMIN)

4. **Cascade Handling**
   - Foreign key cascades handled correctly
   - Related records deleted automatically

### Frontend Protections:

1. **Role Check**
   - Menu hidden for non-SUPERADMIN
   - Route protected

2. **Confirmation Modal**
   - User must type "DELETE"
   - Case-sensitive validation

3. **Warning Banners**
   - Multiple warnings displayed
   - Red color scheme for danger

4. **Disabled States**
   - Clear button disabled when count = 0
   - Loading states during operations

---

## Database Relationships

### Cascade Deletes:

**Invoices (CASCADE):**
- InvoiceItems → Deleted
- PickingSession → Deleted
- PackingSession → Deleted
- DeliverySession → Deleted
- InvoiceReturns → Deleted

**Customers:**
- ❌ Cannot delete if Invoices exist
- Must clear Invoices first

**Users:**
- ✅ Keeps SUPERADMIN
- Deletes all other roles

**Foreign Keys:**
- SET_NULL: Salesmen in Invoices
- CASCADE: Most session relationships

---

## Common Operations

### Clear Everything:
```bash
# Backend
POST /api/developer/clear-data/
Body: { "table_name": "all" }

# Then reset IDs
POST /api/developer/reset-sequences/
```

### Clear Only Invoices:
```bash
POST /api/developer/clear-data/
Body: { "table_name": "invoices" }
```

### Clear Sessions Only:
```bash
POST /api/developer/clear-data/
Body: { "table_name": "sessions" }
```

### Clear Test Users:
```bash
POST /api/developer/clear-data/
Body: { "table_name": "users" }
# Keeps SUPERADMIN safe
```

---

## Testing Checklist

### Backend API:
- [ ] `GET /api/developer/table-stats/` returns stats
- [ ] Non-SUPERADMIN gets 403 Forbidden
- [ ] `POST /api/developer/clear-data/` with valid table
- [ ] `POST /api/developer/clear-data/` with "all"
- [ ] Cannot delete customers with invoices
- [ ] Cannot delete all users (keeps SUPERADMIN)
- [ ] `POST /api/developer/reset-sequences/` works
- [ ] All operations use transactions

### Frontend UI:
- [ ] Page only visible to SUPERADMIN
- [ ] Statistics load correctly
- [ ] Refresh button updates stats
- [ ] Clear buttons show confirmation modal
- [ ] Must type "DELETE" to confirm
- [ ] Success toast on completion
- [ ] Error toast on failure
- [ ] Counts update after clear
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

**400 Constraint Violation:**
```json
{
  "success": false,
  "message": "Cannot delete customers while invoices exist. Clear invoices first."
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Error clearing data: <error details>"
}
```

### Frontend Errors:
- Toast notifications for all errors
- Network errors caught and displayed
- Loading states cleared on error

---

## Best Practices

### Before Clearing Data:

1. **Backup Database**
   ```bash
   pg_dump alfa_erp > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Verify Environment**
   - Double-check you're not on production
   - Confirm database connection

3. **Plan Sequence**
   - Clear dependent tables first
   - Example: Invoices → Customers

4. **Test on Development**
   - Never test on production
   - Use separate test database

### After Clearing Data:

1. **Reset Sequences**
   - Click "Reset Sequences" button
   - Ensures IDs start from 1

2. **Seed Fresh Data** (if needed)
   ```bash
   python manage.py seed_invoices --count 50 --with-sessions
   ```

3. **Verify Application**
   - Test invoice creation
   - Verify workflows
   - Check foreign keys

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

1. **Production Safety:**
   - ⚠️ Should be disabled in production
   - Consider environment-based access
   - Add additional confirmation

2. **Audit Logging:**
   - Consider logging all clear operations
   - Track who cleared what and when
   - Store in separate audit table

3. **Backup Verification:**
   - Prompt for backup confirmation
   - Verify backup before clear
   - Auto-backup before operation

4. **Rate Limiting:**
   - Consider rate limits on clear operations
   - Prevent accidental rapid deletions

---

## Future Enhancements

### Potential Features:
1. Selective backup before clear
2. Restore from backup
3. Schedule automated cleanups
4. Soft delete (mark as deleted)
5. Clear by date range
6. Clear by status
7. Export data before clear
8. Activity audit log
9. Email notification on clear
10. Multi-step confirmation

---

**Created:** January 24, 2026
**Status:** ✅ Fully Implemented
**Risk Level:** 🔴 HIGH - Use with extreme caution
