# Quick Reference: Frontend vs Backend Menu Mapping

## Role Access Comparison

| Menu | Frontend Role Check | Backend Auto-Assign |
|------|-------------------|-------------------|
| **Dashboard** | All users | ✅ All roles |
| **Billing/Invoice** | `BILLER \|\| SUPERADMIN` | ✅ BILLING, BILLER, SUPERADMIN |
| **Picking** | `NOT [PICKER, PACKER, BILLER, DELIVERY]` | ✅ ADMIN, USER, STORE |
| **Packing** | `PACKER \|\| SUPERADMIN` | ✅ PACKER, SUPERADMIN |
| **Delivery** | `SUPERADMIN \|\| ADMIN \|\| DELIVERY` | ✅ SUPERADMIN, ADMIN, DELIVERY, DRIVER |
| **History** | `SUPERADMIN \|\| ADMIN \|\| STORE \|\| USER` | ✅ SUPERADMIN, ADMIN, STORE, USER |
| **User Management** | `SUPERADMIN \|\| ADMIN \|\| permissions` | ✅ SUPERADMIN, ADMIN |
| **Master** | `SUPERADMIN \|\| ADMIN` | ✅ SUPERADMIN, ADMIN |

## Path Mapping

| Frontend Path | Role-Specific Paths | Backend Route Needed |
|--------------|--------------------|--------------------|
| `/dashboard` | Same for all | `/dashboard` |
| `/billing/invoices` | `/ops/billing/invoices` (BILLER) | Both paths |
| `/billing/reviewed` | `/ops/billing/reviewed` (BILLER) | Both paths |
| `/invoices` | Same for all | `/invoices` |
| `/invoices/my` | Same for all | `/invoices/my` |
| `/packing/invoices` | `/ops/packing/invoices` (PACKER) | Both paths |
| `/packing/my` | `/ops/packing/my` (PACKER) | Both paths |
| `/delivery/*` | `/ops/delivery/*` (DELIVERY) | Both paths |

## Backend Roles vs Frontend Roles

| Backend Role | Frontend Expected | Status | Action Needed |
|-------------|------------------|--------|--------------|
| `SUPERADMIN` | `SUPERADMIN` | ✅ Match | None |
| `ADMIN` | `ADMIN` | ✅ Match | None |
| `USER` | `USER` | ✅ Match | None |
| `STORE` | `STORE` | ⚠️ Not in backend | Add to backend or remove from frontend |
| `PICKER` | `PICKER` | ✅ Match | None |
| `PACKER` | `PACKER` | ✅ Match | None |
| `BILLING` | `BILLER` | ❌ Mismatch | **Fix Required** |
| `DELIVERY` | `DELIVERY` | ✅ Match | None |
| `DRIVER` | `DRIVER` | ✅ Match | None |

## Menu Code Reference

| Display Name | Code | Parent Code | URL |
|-------------|------|------------|-----|
| Dashboard | `dashboard` | - | `/dashboard` |
| Invoice (Billing) | `billing` | - | `/billing/invoices` |
| ├─ Invoice List | `billing_invoice_list` | `billing` | `/billing/invoices` |
| └─ Reviewed Bills | `billing_reviewed` | `billing` | `/billing/reviewed` |
| Picking | `invoices` | - | `/invoices` |
| ├─ Picking List | `picking_list` | `invoices` | `/invoices` |
| └─ My Assigned Picking | `my_assigned_picking` | `invoices` | `/invoices/my` |
| Packing | `packing` | - | `/packing/invoices` |
| ├─ Packing List | `packing_list` | `packing` | `/packing/invoices` |
| └─ My Assigned Packing | `my_assigned_packing` | `packing` | `/packing/my` |
| Delivery | `delivery` | - | `/delivery/dispatch` |
| ├─ Dispatch Orders | `delivery_dispatch` | `delivery` | `/delivery/dispatch` |
| ├─ Courier List | `delivery_courier_list` | `delivery` | `/delivery/courier-list` |
| ├─ Company Delivery List | `delivery_company_list` | `delivery` | `/delivery/company-list` |
| └─ My Assigned Delivery | `my_assigned_delivery` | `delivery` | `/delivery/my` |
| History | `history` | - | `/history` |
| ├─ History | `history_main` | `history` | `/history` |
| └─ Consolidate | `history_consolidate` | `history` | `/history/consolidate` |
| User Management | `user-management` | - | `/user-management` |
| ├─ User List | `user_list` | `user-management` | `/user-management` |
| └─ User Control | `user_control` | `user-management` | `/user-control` |
| Master | `master` | - | `/master/job-title` |
| ├─ Job Title | `job_title` | `master` | `/master/job-title` |
| ├─ Department | `department` | `master` | `/master/department` |
| └─ Courier | `courier` | `master` | `/master/courier` |

## Commands Quick Reference

```bash
# View current menus
python manage.py dbshell
SELECT code, name, url FROM menu_items WHERE parent_id IS NULL;

# Clear and reseed
python manage.py seed_menus --clear

# Seed with auto-assignment
python manage.py seed_menus --clear --assign

# Check user menus
python manage.py shell
>>> from apps.accesscontrol.models import UserMenu
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='test@example.com')
>>> menus = UserMenu.get_user_menu_structure(user)
>>> print(menus)

# Count menus by role
>>> from django.db.models import Count
>>> UserMenu.objects.values('user__role').annotate(count=Count('id'))
```

## Expected Login Response

```json
{
  "status": "success",
  "data": {
    "access": "jwt_token...",
    "refresh": "refresh_token...",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "User Name",
      "role": "ADMIN",
      "groups": [],
      "is_staff": false,
      "is_superuser": false
    },
    "menus": [
      {
        "id": "uuid",
        "name": "Dashboard",
        "code": "dashboard",
        "icon": "LayoutDashboard",
        "url": "/dashboard",
        "order": 1,
        "children": []
      },
      {
        "id": "uuid",
        "name": "Picking",
        "code": "invoices",
        "icon": "ClipboardCheck",
        "url": "/invoices",
        "order": 3,
        "children": [
          {
            "id": "uuid",
            "name": "Picking List",
            "code": "picking_list",
            "icon": "ClipboardCheck",
            "url": "/invoices",
            "order": 1
          }
        ]
      }
    ]
  },
  "message": "Login successful"
}
```

## Testing Matrix

| Role | Expected Menus Count | Parent Menus | Test User |
|------|---------------------|--------------|-----------|
| SUPERADMIN | 0 (uses menuConfig) | 0 | admin@example.com |
| ADMIN | ~20 | 6 | manager@example.com |
| BILLING | 3 | 2 (Dashboard + Billing) | biller@example.com |
| PACKER | 3 | 2 (Dashboard + Packing) | packer@example.com |
| DELIVERY | 5 | 2 (Dashboard + Delivery) | delivery@example.com |
| USER | 5 | 3 (Dashboard + Picking + History) | user@example.com |
| PICKER | 1 | 1 (Dashboard only) | picker@example.com |

---

**Last Updated**: 2026-01-06
**Version**: 2.0
