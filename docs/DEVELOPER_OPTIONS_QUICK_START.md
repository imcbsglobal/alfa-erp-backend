# Developer Options - Quick Start Guide

## ✅ What Was Implemented

A complete database management interface for SUPERADMIN users to:
- View database statistics
- Clear/truncate specific tables or all data
- Reset auto-increment sequences
- **SUPERADMIN ONLY** - Secured at both frontend and backend

---

## 🚀 How to Use

### 1. Login as SUPERADMIN
- Only SUPERADMIN role can access
- Menu item "Developer Options" appears in sidebar

### 2. Access Developer Settings
- Navigate to: `/developer/settings`
- Or click "Developer Options" in sidebar menu (Database icon)

### 3. View Statistics
- Page loads with current record counts
- Click "Refresh Stats" to update
- Shows total records across all tables

### 4. Clear Data

**WARNING:** Operations cannot be undone!

**Steps:**
1. Click "Clear" button next to desired table
2. Confirmation modal appears
3. Type `DELETE` (case-sensitive) to confirm
4. Click "Delete Permanently"
5. Success message appears
6. Statistics refresh automatically

**Available Options:**
- **All Data (DANGER)** - Clear everything
- **Invoices** - Clear all invoices & related data
- **Sessions** - Clear picking/packing/delivery sessions only
- **Customers** - Clear customer records
- **Salesmen** - Clear salesman records
- **Couriers** - Clear courier providers
- **Users** - Clear non-SUPERADMIN users (keeps SUPERADMIN)
- **Departments** - Clear departments
- **Job Titles** - Clear job titles

### 5. Reset Sequences (Optional)
- Click "Reset Sequences" button
- Confirms action
- Resets all database auto-increment IDs to 1
- Use after clearing data

---

## 📊 API Endpoints

### Get Table Statistics
```bash
GET /api/developer/table-stats/
Authorization: Bearer YOUR_TOKEN
```

### Clear Data
```bash
POST /api/developer/clear-data/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "table_name": "invoices"
}
```

### Reset Sequences
```bash
POST /api/developer/reset-sequences/
Authorization: Bearer YOUR_TOKEN
```

---

## ⚠️ Safety Rules

1. **Always backup before clearing**
   ```bash
   pg_dump alfa_erp > backup_$(date +%Y%m%d).sql
   ```

2. **Never use in production** (without extreme caution)

3. **Test on development first**

4. **Understand dependencies:**
   - Can't delete Customers if Invoices exist
   - Must clear Invoices first
   - Can't delete all Users (keeps SUPERADMIN)

5. **Use transactions:**
   - All operations are atomic
   - Rollback on any error

---

## 🧪 Testing

### Backend (Python/Django):
```bash
# Start server
cd alfa-erp-backend
python -m uvicorn config.asgi:application --reload

# Test endpoints (using httpie or curl)
http GET http://localhost:8000/api/developer/table-stats/ "Authorization: Bearer YOUR_TOKEN"
http POST http://localhost:8000/api/developer/clear-data/ "Authorization: Bearer YOUR_TOKEN" table_name="sessions"
```

### Frontend (React):
```bash
# Start dev server
cd alfa_agencies_frontend
npm run dev

# Navigate to:
# http://localhost:5173/developer/settings
```

### Test Access Control:
1. Login as non-SUPERADMIN → Menu hidden, route blocked
2. Login as SUPERADMIN → Menu visible, page accessible
3. Try API with non-SUPERADMIN token → 403 Forbidden

---

## 📁 Files Created/Modified

### Backend:
- **NEW:** `apps/common/developer.py` - API views
- **NEW:** `apps/common/urls.py` - URL routing
- **MODIFIED:** `config/urls.py` - Added common URLs

### Frontend:
- **NEW:** `src/pages/DeveloperSettingsPage.jsx` - UI component
- **MODIFIED:** `src/app/router.jsx` - Added route
- **MODIFIED:** `src/layout/Sidebar/menuConfig.js` - Added menu

### Documentation:
- **NEW:** `docs/DEVELOPER_OPTIONS.md` - Full documentation
- **NEW:** `docs/DEVELOPER_OPTIONS_QUICK_START.md` - This file

---

## 🎯 Common Use Cases

### Clear Everything and Start Fresh:
```
1. Click "All Data (DANGER)" → Clear
2. Type "DELETE" → Confirm
3. Click "Reset Sequences"
4. Optional: Seed new data
   python manage.py seed_invoices --count 50
```

### Clear Only Test Invoices:
```
1. Click "Invoices" → Clear
2. Type "DELETE" → Confirm
3. Sessions/Items cleared automatically (cascade)
```

### Reset for New Test Round:
```
1. Clear "Sessions" (keeps invoices)
2. Re-process invoices from start
```

### Remove Test Users:
```
1. Click "Users" → Clear
2. Keeps SUPERADMIN automatically
3. All other users deleted
```

---

## 💡 Pro Tips

1. **Check counts before clearing**
   - Disabled buttons when count = 0
   - No action taken if nothing to clear

2. **Use sessions-only clear for testing workflows**
   - Keeps invoices intact
   - Can re-pick/pack/deliver same invoices

3. **Reset sequences after major clear**
   - IDs restart from 1
   - Cleaner test data

4. **Customer constraint**
   - Can't delete customers with invoices
   - Clear invoices first

5. **SUPERADMIN protection**
   - System always keeps at least one SUPERADMIN
   - Prevents lockout

---

## 🐛 Troubleshooting

### "Cannot delete customers while invoices exist"
**Solution:** Clear invoices first, then customers

### "Permission denied" or 403 error
**Solution:** Login as SUPERADMIN role

### Menu not visible
**Solution:** Check user role is SUPERADMIN

### Counts not updating
**Solution:** Click "Refresh Stats" button

### Foreign key errors
**Solution:** Clear dependent tables first (Invoices → Customers)

---

## 📞 Support

For issues:
1. Check DEVELOPER_OPTIONS.md for detailed docs
2. Verify SUPERADMIN role access
3. Check backend logs for errors
4. Ensure database migrations are up to date

---

**Last Updated:** January 24, 2026
**Status:** ✅ Production Ready
**Access Level:** SUPERADMIN Only
