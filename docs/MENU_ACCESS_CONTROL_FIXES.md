# Menu Access Control - Issues & Fixes

## 🔍 Issues Found

### 1. **Role Mismatch: BILLER vs BILLING**
- **Frontend** (`menuConfig.js`): Uses `BILLER`
- **Backend** (`User.Role`): Uses `BILLING`
- **Impact**: Users with role "BILLING" won't match frontend access checks

### 2. **Missing Menus in Seed Script**
The original `seed_menus.py` was missing:
- ✗ Billing/Invoice menu (separate from Picking)
- ✗ Delivery menu with 4 submenus
- ✗ History Consolidate submenu
- ✗ Courier submenu under Master

### 3. **No Role-Based Auto-Assignment**
- Original script created menus but didn't assign them to users
- Required manual assignment via Django admin for each user
- No automatic role-based menu distribution

### 4. **Incorrect Menu Structure**
- Some parent menus had wrong URLs
- Missing parent-child relationships
- Icon names didn't match frontend

### 5. **Frontend Uses Two Different Path Patterns**
```javascript
// Regular roles
path: "/billing/invoices"

// Operational roles (BILLER, PACKER, DELIVERY)
path: (user) => user?.role === "BILLER" ? "/ops/billing/invoices" : "/billing/invoices"
```
**Note**: Backend should handle `/ops/*` paths or frontend should normalize them.

---

## ✅ Solutions Implemented

### 1. **Updated seed_menus.py**
✓ Complete menu structure matching `menuConfig.js` exactly
✓ All 8 parent menus with 22 child menus
✓ Role-based auto-assignment with `--assign` flag
✓ Proper parent-child relationships

### 2. **Role-Based Menu Assignment**

```python
# Usage:
python manage.py seed_menus --clear --assign
```

**Auto-assignment rules:**

| Role | Menus Assigned |
|------|---------------|
| **SUPERADMIN** | Empty array (frontend uses menuConfig.js) |
| **ADMIN** | Picking, Delivery, History, User Mgmt, Master |
| **USER** | Dashboard, Picking, History |
| **STORE** | Dashboard, Picking, History |
| **PICKER** | Dashboard only (excluded from Picking per menuConfig) |
| **PACKER** | Dashboard, Packing |
| **BILLING/BILLER** | Dashboard, Billing (Invoice List, Reviewed Bills) |
| **DELIVERY** | Dashboard, Delivery (all submenus) |
| **DRIVER** | Dashboard, Delivery (Dispatch, My Assigned) |

### 3. **Complete Menu Structure**

```
1. Dashboard → /dashboard [ALL ROLES]

2. Invoice/Billing [BILLER/BILLING, SUPERADMIN]
   ├─ Invoice List → /billing/invoices
   └─ Reviewed Bills → /billing/reviewed

3. Picking [ADMIN, USER, STORE, NOT: PICKER/PACKER/BILLER/DELIVERY]
   ├─ Picking List → /invoices
   └─ My Assigned Picking → /invoices/my

4. Packing [PACKER, SUPERADMIN]
   ├─ Packing List → /packing/invoices
   └─ My Assigned Packing → /packing/my

5. Delivery [SUPERADMIN, ADMIN, DELIVERY]
   ├─ Dispatch Orders → /delivery/dispatch
   ├─ Courier List → /delivery/courier-list
   ├─ Company Delivery List → /delivery/company-list
   └─ My Assigned Delivery → /delivery/my

6. History [SUPERADMIN, ADMIN, STORE, USER]
   ├─ History → /history
   └─ Consolidate → /history/consolidate

7. User Management [SUPERADMIN, ADMIN]
   ├─ User List → /user-management
   └─ User Control → /user-control

8. Master [SUPERADMIN, ADMIN]
   ├─ Job Title → /master/job-title
   ├─ Department → /master/department
   └─ Courier → /master/courier
```

---

## 🚨 Critical Issues to Fix

### Issue #1: Role Name Inconsistency

**Problem**: Frontend expects `BILLER`, Backend has `BILLING`

**Option A - Frontend Fix** (Recommended):
```javascript
// menuConfig.js - Line 60
hasAccess: (user) => 
  user?.role === "BILLING" || user?.role === "SUPERADMIN",  // Change BILLER → BILLING
```

**Option B - Backend Fix**:
```python
# apps/accounts/models.py
class Role(models.TextChoices):
    # Change this:
    BILLING = 'BILLING', 'Billing'
    # To this:
    BILLER = 'BILLER', 'Biller'
```

### Issue #2: Missing /ops/* Path Handling

Frontend uses different paths for operational roles:
```javascript
path: (user) => user?.role === "BILLER" ? "/ops/billing/invoices" : "/billing/invoices"
```

**Backend Solution**: Ensure URL routing handles both patterns:
```python
# config/urls.py
urlpatterns = [
    path('billing/', include('apps.billing.urls')),
    path('ops/billing/', include('apps.billing.urls')),  # Add this
    # Same for packing, delivery
]
```

### Issue #3: Frontend Permission Checks

Some menus check custom permissions:
```javascript
hasAccess: (user, permissions) =>
  permissions["my-invoices"]?.view === true
```

**Solution**: Backend needs to return permissions in login response:
```python
# apps/accounts/serializers.py - CustomTokenObtainPairSerializer
data['user']['permissions'] = {
    'my-invoices': {'view': True},
    'my-packing': {'view': True},
    'user-management': {'view': user.role in ['SUPERADMIN', 'ADMIN']},
}
```

---

## 📋 Step-by-Step Migration

### Step 1: Update Backend Role Name (If choosing Option B)
```bash
# If you decide to change BILLING → BILLER
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Clear and Reseed Menus
```bash
cd alfa-erp-backend
python manage.py seed_menus --clear --assign
```

### Step 3: Verify Menu Assignment
```python
# Django shell
python manage.py shell

from apps.accesscontrol.models import UserMenu
from django.contrib.auth import get_user_model

User = get_user_model()

# Check a BILLER user
biller = User.objects.filter(role='BILLING').first()
if biller:
    menus = UserMenu.get_user_menu_structure(biller)
    print(f"BILLER has {len(menus)} parent menus")
    for menu in menus:
        print(f"  - {menu['name']}")
```

### Step 4: Test Login Response
```bash
# Test login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"biller@example.com","password":"password"}'

# Check response includes:
# - user.role
# - menus array with correct structure
```

### Step 5: Frontend Testing
1. Login as different role users
2. Verify menus appear correctly
3. Check navigation works for all paths
4. Test `/ops/*` paths for operational roles

---

## 🧪 Testing Checklist

- [ ] SUPERADMIN sees all menus (via menuConfig.js)
- [ ] ADMIN sees assigned menus from DB
- [ ] BILLING/BILLER sees only Billing menus
- [ ] PACKER sees only Packing menus
- [ ] DELIVERY sees only Delivery menus
- [ ] PICKER sees only Dashboard (no Picking access)
- [ ] USER/STORE sees Dashboard, Picking, History
- [ ] All menu URLs navigate correctly
- [ ] `/ops/*` paths work for operational roles
- [ ] Permission-based submenus work (my-invoices, my-packing)

---

## 📚 Additional Recommendations

### 1. **Add Menu Validation Endpoint**
```python
# apps/accesscontrol/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_menu_access(request, menu_code):
    """Check if user has access to a specific menu"""
    has_access = UserMenu.objects.filter(
        user=request.user,
        menu__code=menu_code,
        is_active=True
    ).exists()
    return Response({'has_access': has_access})
```

### 2. **Add Audit Logging**
Track when users access menus they shouldn't have access to.

### 3. **Create Admin Action**
```python
# apps/accesscontrol/admin.py
@admin.action(description='Reassign menus based on role')
def reassign_menus_by_role(modeladmin, request, queryset):
    # Bulk reassign menus for selected users
    pass
```

### 4. **Add Migration Script**
If you have existing users, create a migration to fix role names:
```python
# apps/accounts/migrations/XXXX_fix_biller_role.py
def forward(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(role='BILLING').update(role='BILLER')
```

---

## 🎯 Summary

**Critical Action Items:**
1. ✅ Updated `seed_menus.py` with complete menu structure
2. ⚠️ Fix BILLER vs BILLING role mismatch (choose Option A or B)
3. ⚠️ Add `/ops/*` URL routing in backend
4. ⚠️ Add permissions to login response
5. ✅ Run `python manage.py seed_menus --clear --assign`
6. 🧪 Test all roles thoroughly

**Quick Fix Command:**
```bash
# Complete setup
python manage.py seed_menus --clear --assign
```

**Need Help?**
- Check logs: `tail -f logs/django.log`
- Debug in shell: `python manage.py shell`
- Admin interface: `http://localhost:8000/admin/accesscontrol/`
