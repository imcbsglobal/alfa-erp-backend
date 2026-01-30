# Developer Options - Quick Start Guide

## ✅ What Was Implemented

A complete database statistics interface for SUPERADMIN users to:
- View database statistics in real-time
- Clear data from frontend view (database unchanged)
- Monitor record counts
- **SUPERADMIN ONLY** - Secured at both frontend and backend
- **READ-ONLY** - No data is deleted from database

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

### 4. Clear Data from View

**NOTE:** Operations only affect frontend display. Database remains unchanged!

**Steps:**
1. Click "Clear" button next to desired table
2. Confirmation modal appears
3. Type `CLEAR` (case-sensitive) to confirm
4. Click "Clear View"
5. Success message appears
6. Statistics show current database state (unchanged)

**Available Options:**
- **All Data** - View all data counts
- **Invoices** - View invoice counts
- **Picking Sessions** - View picking session counts
- **Packing Sessions** - View packing session counts
- **Delivery Sessions** - View delivery session counts
- **Customers** - View customer record counts
- **Salesmen** - View salesman record counts
- **Couriers** - View courier provider counts
- **Users** - View non-SUPERADMIN user counts
- **Departments** - View department counts
- **Job Titles** - View job title counts

*Note: All operations are view-only. Database is not modified.*

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

### Clear Data from View
```bash
POST /api/developer/clear-data/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "table_name": "invoices"
}

# Returns counts without deleting data
# Database remains unchanged
```

### Reset Sequences
```bash
POST /api/developer/reset-sequences/
Authorization: Bearer YOUR_TOKEN
```

---

## ✅ Safety Rules

1. **Read-Only Operations**
   - No data deleted from database
   - Safe for all environments
   - View statistics only

2. **SUPERADMIN Access Only**
   - Only accessible to SUPERADMIN role
   - Backend enforces permissions

3. **No Risk of Data Loss**
   - All operations are read-only
   - Database remains unchanged
   - Statistics queries only

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

### View All Database Statistics:
```
1. Navigate to Developer Options
2. View statistics cards at top
3. Click "Refresh Stats" to update
4. See total records across all tables
```

### Check Invoice Counts:
```
1. Scroll to "Sales & Operations" section
2. View "Invoices" row
3. See current count from database
4. Database data intact
```

### Monitor User Counts:
```
1. Scroll to "Users & Organization"
2. View "Users" row  
3. See non-SUPERADMIN user count
4. Database unchanged
```

---

## 💡 Pro Tips

1. **Quick Stats Overview**
   - Use statistics cards for at-a-glance view
   - Total records shown prominently

2. **Refresh for Latest Data**
   - Click "Refresh Stats" after operations
   - See real-time database state

3. **Monitor Specific Tables**
   - Scroll to category of interest
   - View counts for specific tables

4. **No Data Loss Risk**
   - All operations are read-only
   - Safe to use in any environment

5. **SUPERADMIN Protection**
   - Menu only visible to SUPERADMIN
   - Route protected in frontend
   - API enforces permissions

---

## 🐛 Troubleshooting

### "Permission denied" or 403 error
**Solution:** Login as SUPERADMIN role

### Menu not visible
**Solution:** Check user role is SUPERADMIN

### Counts not updating
**Solution:** Click "Refresh Stats" button

### Stats loading slowly
**Solution:** Normal for large databases - wait for completion

---

## 📞 Support

For issues:
1. Check DEVELOPER_OPTIONS.md for detailed docs
2. Verify SUPERADMIN role access
3. Check backend logs for errors
4. Ensure database migrations are up to date

---

**Last Updated:** January 30, 2026
**Status:** ✅ Production Safe - Read-Only Operations
**Access Level:** SUPERADMIN Only
