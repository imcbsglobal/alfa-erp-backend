# Developer Options - Truncate Table Feature

## Overview
Added permanent data deletion (truncate) functionality for SUPERADMIN users in the Developer Options page. This feature allows SUPERADMIN to permanently delete data from database tables with password verification.

**Note**: This feature provides ONLY permanent deletion. For temporary data management or testing, use the Django management command `python manage.py clear_data`. See [seed_and_clear_data.md](alfa-erp-backend/docs/seed_and_clear_data.md).

## Security Features

### 1. **Triple-Layer Protection**
- **Backend Permission Class**: `SuperAdminOnlyPermission` verifies user role
- **Frontend Route Guard**: `SuperAdminRoute` wrapper in router
- **Component-Level Check**: Page renders access denied for non-SUPERADMIN users

### 2. **Password Verification**
- Requires SUPERADMIN password confirmation before truncating
- Backend validates password using Django's `check_password()`
- Prevents accidental or unauthorized deletions

### 3. **Strict Confirmation Flow**
- User must type "DELETE PERMANENTLY" exactly
- Password must be entered
- Both conditions required to enable delete button

## Files Modified

### Backend Changes

#### 1. `alfa-erp-backend/apps/common/developer.py`
**Added**: `TruncateTableView` class
- Handles permanent deletion of data from database
- Validates SUPERADMIN password
- Supports individual table truncation or all tables
- Uses Django transactions for data integrity
- Returns detailed deleted counts

**Key Features**:
```python
class TruncateTableView(APIView):
    permission_classes = [SuperAdminOnlyPermission]
    
    def post(self, request):
        # Password verification
        if not request.user.check_password(confirm_password):
            return Response(403)
        
        # Atomic transaction for data integrity
        with transaction.atomic():
            # Delete operations...
```

**Supported Tables**:
- `all` - Delete all data
- `invoices` - Delete invoices and related data
- `customers` - Delete customer records
- `salesmen` - Delete salesman records
- `couriers` - Delete courier records
- `picking_sessions` - Delete picking sessions
- `packing_sessions` - Delete packing sessions
- `delivery_sessions` - Delete delivery sessions
- `users` - Delete non-SUPERADMIN users
- `departments` - Delete departments
- `job_titles` - Delete job titles

#### 2. `alfa-erp-backend/apps/common/urls.py`
**Added**: New URL endpoint
```python
path('developer/truncate-table/', TruncateTableView.as_view(), name='developer-truncate-table')
```

### Frontend Changes

#### 1. `alfa_agencies_frontend/src/pages/DeveloperSettingsPage.jsx`

**Added State Variables**:
```javascript
const [showTruncateModal, setShowTruncateModal] = useState(false);
const [confirmPassword, setConfirmPassword] = useState('');
const [truncating, setTruncating] = useState(false);
```

**Added Access Control Check**:
```javascript
if (user?.role !== 'SUPERADMIN') {
  return <AccessDeniedView />;
}
```

**Added Functions**:
- `handleTruncateClick(tableName, tableLabel)` - Opens truncate modal
- `handleConfirmTruncate()` - Executes permanent deletion with validation

**UI Changes**:
- Added two-button layout: "Clear View" (temporary) and "Delete" (permanent)
- Added new truncate confirmation modal with:
  - Red danger theme
  - Clear warning messages
  - Text confirmation input ("DELETE PERMANENTLY")
  - Password input field
  - Loading state during deletion

#### 2. `alfa_agencies_frontend/src/app/router.jsx`

**Added Route Protection**:
```javascript
const SuperAdminRoute = ({ children }) => {
  if (user?.role !== 'SUPERADMIN') {
    return <Navigate to="/403" replace />;
  }
  return children;
};

// Usage
<Route 
  path="/developer/settings" 
  element={
    <SuperAdminRoute>
      <DeveloperSettingsPage />
    </SuperAdminRoute>
  } 
/>
```

## User Interface

### Delete Button (Permanent Deletion)

#### "Delete Permanently" Button (Red)
- **Purpose**: Permanently delete data from database
- **Color**: Red
- **Icon**: Trash icon
- **Action**: Executes SQL DELETE statements
- **Database**: Permanently modified
- **Confirmation**: Type "DELETE PERMANENTLY" + password
- **Note**: This is the ONLY deletion option - no temporary "clear view" functionality

### Truncate Modal Features

1. **Visual Warnings**:
   - Red color scheme
   - Warning triangle icon
   - "🚨 IRREVERSIBLE ACTION" header
   - Multiple warning messages

2. **Required Inputs**:
   - Exact text: "DELETE PERMANENTLY"
   - SUPERADMIN password
   - Both required to enable delete button

3. **Feedback**:
   - Success toast with confirmation
   - Warning toast about irreversibility
   - Auto-refresh of statistics
   - Broadcasting event to other components

## API Endpoints

### POST `/api/developer/truncate-table/`

**Authentication**: Required (JWT Token)  
**Permission**: SUPERADMIN only

**Request Body**:
```json
{
  "table_name": "invoices",
  "confirm_password": "admin_password"
}
```

**Success Response** (200):
```json
{
  "success": true,
  "message": "✅ Invoices and related data PERMANENTLY DELETED",
  "deleted_counts": {
    "invoices": 150,
    "invoice_items": 500,
    "invoice_returns": 10,
    "picking_sessions": 100,
    "packing_sessions": 80,
    "delivery_sessions": 75
  },
  "warning": "⚠️ THIS WAS A PERMANENT DELETE OPERATION - DATA CANNOT BE RECOVERED"
}
```

**Error Responses**:
- `400`: Invalid table name
- `403`: Invalid password
- `401`: Not authenticated or not SUPERADMIN
- `500`: Server error

## Data Integrity

### Cascade Deletion
When deleting invoices, automatically deletes:
- Invoice items
- Invoice returns
- Related picking sessions
- Related packing sessions
- Related delivery sessions

### Protected Data
- SUPERADMIN users are never deleted (even with "all" or "users" table)
- Cache is cleared after truncation to ensure consistency

### Transaction Safety
All deletions wrapped in Django's `transaction.atomic()`:
- Either all deletions succeed or none do
- Prevents partial data corruption
- Maintains referential integrity

## Testing Checklist

### Access Control
- [ ] Non-SUPERADMIN users redirected to /403
- [ ] Backend API returns 401 for non-SUPERADMIN
- [ ] Frontend shows access denied message

### Truncate Functionality
- [ ] Modal opens with correct table name
- [ ] Delete button disabled without text confirmation
- [ ] Delete button disabled without password
- [ ] Invalid password shows error message
- [ ] Valid password + confirmation executes deletion
- [ ] Statistics refresh after deletion
- [ ] Success and warning toasts appear

### Data Integrity
- [ ] CASCADE deletion works correctly
- [ ] SUPERADMIN users not deleted
- [ ] Transaction rollback on error
- [ ] Cache cleared after operation

### UI/UX
- [ ] Two buttons clearly labeled
- [ ] Color coding (blue vs red) clear
- [ ] Modal warnings prominent
- [ ] Loading states work correctly
- [ ] Cancel button works in modal

## Security Considerations

### What's Protected
✅ Multiple authorization checks (backend + frontend)  
✅ Password verification required  
✅ Explicit text confirmation required  
✅ SUPERADMIN role validation  
✅ Transaction-based operations  
✅ Audit trail in console logs

### What to Monitor
⚠️ All truncate operations should be logged  
⚠️ Consider adding database audit trail  
⚠️ Monitor for unusual patterns of deletion  
⚠️ Consider adding email notifications for truncate operations

## Future Enhancements

1. **Audit Logging**: Log all truncate operations to database
2. **Email Notifications**: Alert other admins when truncate occurs
3. **Backup Reminder**: Prompt for backup before truncation
4. **Soft Delete Option**: Add option to soft-delete instead of hard-delete
5. **Restore Capability**: Implement backup/restore functionality
6. **Scheduled Deletions**: Allow scheduling of truncate operations

## Usage Instructions

### For SUPERADMIN Users

1. **Navigate to Developer Options**:
   - Login as SUPERADMIN
   - Go to `/developer/settings`

2. **View Current Statistics**:
   - Page shows record counts for all tables
   - Click "Refresh Status" to update

3. **Permanent Delete (Truncate)**:
   - Click red "Delete Permanently" button
   - Read all warnings carefully
   - Type "DELETE PERMANENTLY" exactly
   - Enter your SUPERADMIN password
   - Click "🗑️ DELETE FOREVER" button
   - Confirm success messages
   - Verify data is gone

### Alternative: Management Command

For command-line operations, use the Django management command:
```bash
# Clear all data with confirmation prompt
python manage.py clear_data

# Clear without prompt
python manage.py clear_data --confirm

# Clear only sessions
python manage.py clear_data --sessions-only --confirm

# Clear only invoices
python manage.py clear_data --invoices-only --confirm
```

See [seed_and_clear_data.md](alfa-erp-backend/docs/seed_and_clear_data.md) for more details.

### Best Practices

1. **Always backup before deleting**
2. **Verify the table name before confirming**
3. **Use management command `clear_data` for routine operations**
4. **Communicate with team before major deletions**
5. **Check cascade effects (e.g., deleting invoices affects sessions)**
6. **For testing purposes, use `seed_invoices` to recreate data**

## Troubleshooting

### "Invalid password" Error
- Ensure you're entering YOUR SUPERADMIN password
- Password is case-sensitive
- Check for extra spaces

### "Access Denied" Message
- Verify you're logged in as SUPERADMIN
- Check user role in profile
- Logout and login again if needed

### Deletion Not Working
- Check browser console for errors
- Verify backend server is running
- Check API endpoint connectivity
- Ensure database is not locked

### Statistics Not Updating
- Click "Refresh Status" button
- Check if backend API is responding
- Clear browser cache if needed

## API Integration Example

```javascript
// Frontend API call
const truncateTable = async (tableName, password) => {
  try {
    const response = await api.post('/developer/truncate-table/', {
      table_name: tableName,
      confirm_password: password
    });
    
    if (response.data.success) {
      console.log('Deleted:', response.data.deleted_counts);
      return true;
    }
  } catch (error) {
    console.error('Truncate failed:', error.response?.data?.message);
    return false;
  }
};
```

## Conclusion

This feature provides SUPERADMIN users with powerful data management capabilities while maintaining strong security controls. The multi-layer protection, password verification, and explicit confirmations help prevent accidental data loss while enabling legitimate administrative operations.

**Remember**: With great power comes great responsibility. Always backup before truncating!
