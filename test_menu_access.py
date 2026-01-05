#!/usr/bin/env python
"""
Test script to verify menu access control system
Run: python manage.py shell < test_menu_access.py
"""

from django.contrib.auth import get_user_model
from apps.accesscontrol.models import MenuItem, UserMenu
from django.db.models import Count

User = get_user_model()

print("=" * 70)
print("MENU ACCESS CONTROL SYSTEM - TEST REPORT")
print("=" * 70)

# 1. Check Menu Items
print("\n1. MENU ITEMS IN DATABASE")
print("-" * 70)
total_menus = MenuItem.objects.count()
parent_menus = MenuItem.objects.filter(parent__isnull=True).count()
child_menus = MenuItem.objects.filter(parent__isnull=False).count()

print(f"Total menus: {total_menus}")
print(f"Parent menus: {parent_menus}")
print(f"Child menus: {child_menus}")
print(f"Expected: 30 total (8 parent + 22 child)")

if total_menus == 30:
    print("✅ PASS: Correct number of menus")
else:
    print(f"❌ FAIL: Expected 30, got {total_menus}")

# 2. List all parent menus
print("\n2. PARENT MENUS")
print("-" * 70)
for menu in MenuItem.objects.filter(parent__isnull=True).order_by('order'):
    children_count = menu.children.count()
    print(f"  {menu.order}. {menu.name} [{menu.code}] → {menu.url}")
    print(f"     Children: {children_count}")

# 3. Check Users by Role
print("\n3. USERS BY ROLE")
print("-" * 70)
users_by_role = User.objects.values('role').annotate(count=Count('id')).order_by('-count')
for item in users_by_role:
    role = item['role']
    count = item['count']
    print(f"  {role}: {count} user(s)")

# 4. Check User Menu Assignments
print("\n4. MENU ASSIGNMENTS BY ROLE")
print("-" * 70)
assignment_stats = UserMenu.objects.filter(is_active=True).values('user__role').annotate(
    menu_count=Count('id')
).order_by('user__role')

for stat in assignment_stats:
    role = stat['user__role']
    menu_count = stat['menu_count']
    print(f"  {role}: {menu_count} menu assignments")

# 5. Test Specific Role Assignments
print("\n5. ROLE-SPECIFIC MENU TESTS")
print("-" * 70)

test_roles = {
    'SUPERADMIN': {'expected': 0, 'reason': 'Uses frontend menuConfig'},
    'ADMIN': {'expected_min': 15, 'reason': 'Should have most menus'},
    'BILLING': {'expected': 3, 'reason': 'Dashboard + Billing (2 children)'},
    'PACKER': {'expected': 3, 'reason': 'Dashboard + Packing (2 children)'},
    'DELIVERY': {'expected': 5, 'reason': 'Dashboard + Delivery (4 children)'},
    'USER': {'expected': 5, 'reason': 'Dashboard + Picking (2) + History (2)'},
    'PICKER': {'expected': 1, 'reason': 'Dashboard only (excluded from picking)'},
}

for role, info in test_roles.items():
    users = User.objects.filter(role=role, is_active=True)
    
    if not users.exists():
        print(f"\n  {role}: ⚠️  No users with this role")
        continue
    
    user = users.first()
    menu_count = UserMenu.objects.filter(user=user, is_active=True).count()
    
    print(f"\n  {role}: {user.email}")
    print(f"    Assigned menus: {menu_count}")
    
    if 'expected' in info:
        expected = info['expected']
        if menu_count == expected:
            print(f"    ✅ PASS: Expected {expected}, got {menu_count}")
        else:
            print(f"    ❌ FAIL: Expected {expected}, got {menu_count}")
    elif 'expected_min' in info:
        expected_min = info['expected_min']
        if menu_count >= expected_min:
            print(f"    ✅ PASS: Expected {expected_min}+, got {menu_count}")
        else:
            print(f"    ❌ FAIL: Expected {expected_min}+, got {menu_count}")
    
    print(f"    Reason: {info['reason']}")
    
    # Show actual menus
    menus = UserMenu.objects.filter(user=user, is_active=True).select_related('menu')
    parent_menus = [um.menu for um in menus if um.menu.parent is None]
    
    print(f"    Parent menus:")
    for menu in parent_menus:
        print(f"      - {menu.name} ({menu.code})")

# 6. Test Menu Structure
print("\n6. MENU STRUCTURE TEST")
print("-" * 70)

# Test that specific menus exist
required_menus = [
    'dashboard',
    'billing',
    'billing_invoice_list',
    'billing_reviewed',
    'invoices',
    'picking_list',
    'my_assigned_picking',
    'packing',
    'packing_list',
    'my_assigned_packing',
    'delivery',
    'delivery_dispatch',
    'delivery_courier_list',
    'delivery_company_list',
    'my_assigned_delivery',
    'history',
    'history_main',
    'history_consolidate',
    'user-management',
    'user_list',
    'user_control',
    'master',
    'job_title',
    'department',
    'courier',
]

missing_menus = []
for code in required_menus:
    if not MenuItem.objects.filter(code=code).exists():
        missing_menus.append(code)

if missing_menus:
    print(f"❌ FAIL: Missing menus: {', '.join(missing_menus)}")
else:
    print(f"✅ PASS: All {len(required_menus)} required menus exist")

# 7. Test Menu URLs
print("\n7. MENU URL VALIDATION")
print("-" * 70)

url_issues = []
for menu in MenuItem.objects.all():
    if not menu.url:
        url_issues.append(f"{menu.code}: Missing URL")
    elif not menu.url.startswith('/'):
        url_issues.append(f"{menu.code}: URL doesn't start with / ({menu.url})")

if url_issues:
    print("❌ FAIL: URL issues found:")
    for issue in url_issues:
        print(f"  - {issue}")
else:
    print("✅ PASS: All menu URLs are valid")

# 8. Test Parent-Child Relationships
print("\n8. PARENT-CHILD RELATIONSHIP TEST")
print("-" * 70)

orphaned_children = []
for menu in MenuItem.objects.filter(parent__isnull=False):
    if not menu.parent.is_active:
        orphaned_children.append(f"{menu.code} (parent: {menu.parent.code} is inactive)")

if orphaned_children:
    print("❌ FAIL: Found orphaned children:")
    for child in orphaned_children:
        print(f"  - {child}")
else:
    print("✅ PASS: All child menus have active parents")

# 9. Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

issues = []

if total_menus != 30:
    issues.append(f"Incorrect menu count: {total_menus} (expected 30)")

if missing_menus:
    issues.append(f"Missing {len(missing_menus)} required menus")

if url_issues:
    issues.append(f"{len(url_issues)} URL issues")

if orphaned_children:
    issues.append(f"{len(orphaned_children)} orphaned child menus")

# Check if any users have no menus (except SUPERADMIN)
users_without_menus = User.objects.filter(
    is_active=True
).exclude(
    role='SUPERADMIN'
).annotate(
    menu_count=Count('menu_assignments', filter=models.Q(menu_assignments__is_active=True))
).filter(
    menu_count=0
).count()

if users_without_menus > 0:
    issues.append(f"{users_without_menus} active users without menus")

if issues:
    print("\n❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    print("\nRECOMMENDED ACTION:")
    print("  Run: python manage.py seed_menus --clear --assign")
else:
    print("\n✅ ALL TESTS PASSED!")
    print("  Menu access control system is properly configured")

print("\n" + "=" * 70)
print("END OF REPORT")
print("=" * 70)
