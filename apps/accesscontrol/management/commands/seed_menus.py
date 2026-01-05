from django.core.management.base import BaseCommand
from apps.accesscontrol.models import MenuItem, UserMenu
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed menu items matching frontend menuConfig.js exactly with role-based auto-assignment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing menus before seeding',
        )
        parser.add_argument(
            '--assign',
            action='store_true',
            help='Auto-assign menus to existing users based on their roles',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Starting menu seeding...'))

        # Clear existing data if requested
        if options.get('clear'):
            UserMenu.objects.all().delete()
            MenuItem.objects.all().delete()
            self.stdout.write(self.style.WARNING('  ✓ Cleared existing menus and assignments'))

        # ========================================
        # 1. DASHBOARD (Single - All Roles)
        # ========================================
        dashboard, _ = MenuItem.objects.update_or_create(
            code="dashboard",
            defaults={
                'name': "Dashboard",
                'icon': "LayoutDashboard",
                'url': "/dashboard",
                'order': 1,
                'is_active': True,
                'parent': None,
            }
        )
        self.stdout.write("  ✓ Dashboard menu created")

        # ========================================
        # 2. BILLING (Dropdown - BILLER/BILLING & SUPERADMIN)
        # ========================================
        billing, _ = MenuItem.objects.update_or_create(
            code="billing",
            defaults={
                'name': "Invoice",  # Display name "Invoice" as per menuConfig
                'icon': "FileText",
                'url': "/billing/invoices",
                'order': 2,
                'is_active': True,
                'parent': None,
            }
        )

        billing_invoice_list, _ = MenuItem.objects.update_or_create(
            code="billing_invoice_list",
            defaults={
                'name': "Invoice List",
                'icon': "ListChecks",
                'url': "/billing/invoices",
                'parent': billing,
                'order': 1,
                'is_active': True,
            }
        )
        
        billing_reviewed, _ = MenuItem.objects.update_or_create(
            code="billing_reviewed",
            defaults={
                'name': "Reviewed Bills",
                'icon': "AlertCircle",
                'url': "/billing/reviewed",
                'parent': billing,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Billing menus created")

        # ========================================
        # 3. PICKING/INVOICES (Dropdown - NOT PICKER, PACKER, BILLER, DELIVERY)
        # ========================================
        invoices, _ = MenuItem.objects.update_or_create(
            code="invoices",
            defaults={
                'name': "Picking",
                'icon': "ClipboardCheck",
                'url': "/invoices",
                'order': 3,
                'is_active': True,
                'parent': None,
            }
        )

        picking_list, _ = MenuItem.objects.update_or_create(
            code="picking_list",
            defaults={
                'name': "Picking List",
                'icon': "ClipboardCheck",
                'url': "/invoices",
                'parent': invoices,
                'order': 1,
                'is_active': True,
            }
        )
        
        my_assigned_picking, _ = MenuItem.objects.update_or_create(
            code="my_assigned_picking",
            defaults={
                'name': "My Assigned Picking",
                'icon': "PlusCircle",
                'url': "/invoices/my",
                'parent': invoices,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Picking menus created")

        # ========================================
        # 4. PACKING (Dropdown - PACKER & SUPERADMIN)
        # ========================================
        packing, _ = MenuItem.objects.update_or_create(
            code="packing",
            defaults={
                'name': "Packing",
                'icon': "Box",
                'url': "/packing/invoices",
                'order': 4,
                'is_active': True,
                'parent': None,
            }
        )

        packing_list, _ = MenuItem.objects.update_or_create(
            code="packing_list",
            defaults={
                'name': "Packing List",
                'icon': "Box",
                'url': "/packing/invoices",
                'parent': packing,
                'order': 1,
                'is_active': True,
            }
        )
        
        my_assigned_packing, _ = MenuItem.objects.update_or_create(
            code="my_assigned_packing",
            defaults={
                'name': "My Assigned Packing",
                'icon': "PlusCircle",
                'url': "/packing/my",
                'parent': packing,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Packing menus created")

        # ========================================
        # 5. DELIVERY (Dropdown - SUPERADMIN, ADMIN, DELIVERY)
        # ========================================
        delivery, _ = MenuItem.objects.update_or_create(
            code="delivery",
            defaults={
                'name': "Delivery",
                'icon': "Truck",
                'url': "/delivery/dispatch",
                'order': 5,
                'is_active': True,
                'parent': None,
            }
        )

        delivery_dispatch, _ = MenuItem.objects.update_or_create(
            code="delivery_dispatch",
            defaults={
                'name': "Dispatch Orders",
                'icon': "Truck",
                'url': "/delivery/dispatch",
                'parent': delivery,
                'order': 1,
                'is_active': True,
            }
        )
        
        delivery_courier, _ = MenuItem.objects.update_or_create(
            code="delivery_courier_list",
            defaults={
                'name': "Courier List",
                'icon': "Package",
                'url': "/delivery/courier-list",
                'parent': delivery,
                'order': 2,
                'is_active': True,
            }
        )
        
        delivery_company, _ = MenuItem.objects.update_or_create(
            code="delivery_company_list",
            defaults={
                'name': "Company Delivery List",
                'icon': "Warehouse",
                'url': "/delivery/company-list",
                'parent': delivery,
                'order': 3,
                'is_active': True,
            }
        )
        
        my_assigned_delivery, _ = MenuItem.objects.update_or_create(
            code="my_assigned_delivery",
            defaults={
                'name': "My Assigned Delivery",
                'icon': "PlusCircle",
                'url': "/delivery/my",
                'parent': delivery,
                'order': 4,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Delivery menus created")

        # ========================================
        # 6. HISTORY (Dropdown - SUPERADMIN, ADMIN, STORE, USER)
        # ========================================
        history, _ = MenuItem.objects.update_or_create(
            code="history",
            defaults={
                'name': "History",
                'icon': "Clock",
                'url': "/history",
                'order': 6,
                'is_active': True,
                'parent': None,
            }
        )

        history_main, _ = MenuItem.objects.update_or_create(
            code="history_main",
            defaults={
                'name': "History",
                'icon': "History",
                'url': "/history",
                'parent': history,
                'order': 1,
                'is_active': True,
            }
        )
        
        history_consolidate, _ = MenuItem.objects.update_or_create(
            code="history_consolidate",
            defaults={
                'name': "Consolidate",
                'icon': "Layers",
                'url': "/history/consolidate",
                'parent': history,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ History menus created")

        # ========================================
        # 7. USER MANAGEMENT (Dropdown - SUPERADMIN, ADMIN)
        # ========================================
        user_mgmt, _ = MenuItem.objects.update_or_create(
            code="user-management",
            defaults={
                'name': "User Management",
                'icon': "Users",
                'url': "/user-management",
                'order': 7,
                'is_active': True,
                'parent': None,
            }
        )

        user_list, _ = MenuItem.objects.update_or_create(
            code="user_list",
            defaults={
                'name': "User List",
                'icon': "Users",
                'url': "/user-management",
                'parent': user_mgmt,
                'order': 1,
                'is_active': True,
            }
        )
        
        user_control, _ = MenuItem.objects.update_or_create(
            code="user_control",
            defaults={
                'name': "User Control",
                'icon': "UserCog",
                'url': "/user-control",
                'parent': user_mgmt,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ User Management menus created")

        # ========================================
        # 8. MASTER (Dropdown - SUPERADMIN, ADMIN)
        # ========================================
        master, _ = MenuItem.objects.update_or_create(
            code="master",
            defaults={
                'name': "Master",
                'icon': "TuneOutlinedIcon",
                'url': "/master/job-title",
                'order': 8,
                'is_active': True,
                'parent': None,
            }
        )

        job_title, _ = MenuItem.objects.update_or_create(
            code="job_title",
            defaults={
                'name': "Job Title",
                'icon': "Briefcase",
                'url': "/master/job-title",
                'parent': master,
                'order': 1,
                'is_active': True,
            }
        )
        
        department, _ = MenuItem.objects.update_or_create(
            code="department",
            defaults={
                'name': "Department",
                'icon': "Building",
                'url': "/master/department",
                'parent': master,
                'order': 2,
                'is_active': True,
            }
        )
        
        courier, _ = MenuItem.objects.update_or_create(
            code="courier",
            defaults={
                'name': "Courier",
                'icon': "Send",
                'url': "/master/courier",
                'parent': master,
                'order': 3,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Master menus created")

        # ========================================
        # Auto-assign menus based on roles
        # ========================================
        if options.get('assign'):
            self.stdout.write(self.style.WARNING('\n🔄 Auto-assigning menus to users...'))
            self._assign_menus_by_role()

        # ========================================
        # Summary
        # ========================================
        total = MenuItem.objects.count()
        parent_menus = MenuItem.objects.filter(parent__isnull=True).count()
        child_menus = MenuItem.objects.filter(parent__isnull=False).count()
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*70}"))
        self.stdout.write(self.style.SUCCESS("✔ MENU SEEDING COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS(f"{'='*70}"))
        self.stdout.write(f"  • Total menu items: {total}")
        self.stdout.write(f"  • Parent menus: {parent_menus}")
        self.stdout.write(f"  • Child menus: {child_menus}")
        
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write("COMPLETE MENU STRUCTURE (matches menuConfig.js):")
        self.stdout.write(f"{'='*70}")
        self.stdout.write("1. Dashboard (single) → /dashboard [ALL ROLES]")
        self.stdout.write("2. Invoice/Billing (dropdown) [BILLER/BILLING, SUPERADMIN]")
        self.stdout.write("   ├─ Invoice List → /billing/invoices")
        self.stdout.write("   └─ Reviewed Bills → /billing/reviewed")
        self.stdout.write("3. Picking (dropdown) [NOT: PICKER, PACKER, BILLER, DELIVERY]")
        self.stdout.write("   ├─ Picking List → /invoices")
        self.stdout.write("   └─ My Assigned Picking → /invoices/my")
        self.stdout.write("4. Packing (dropdown) [PACKER, SUPERADMIN]")
        self.stdout.write("   ├─ Packing List → /packing/invoices")
        self.stdout.write("   └─ My Assigned Packing → /packing/my")
        self.stdout.write("5. Delivery (dropdown) [SUPERADMIN, ADMIN, DELIVERY]")
        self.stdout.write("   ├─ Dispatch Orders → /delivery/dispatch")
        self.stdout.write("   ├─ Courier List → /delivery/courier-list")
        self.stdout.write("   ├─ Company Delivery List → /delivery/company-list")
        self.stdout.write("   └─ My Assigned Delivery → /delivery/my")
        self.stdout.write("6. History (dropdown) [SUPERADMIN, ADMIN, STORE, USER]")
        self.stdout.write("   ├─ History → /history")
        self.stdout.write("   └─ Consolidate → /history/consolidate")
        self.stdout.write("7. User Management (dropdown) [SUPERADMIN, ADMIN]")
        self.stdout.write("   ├─ User List → /user-management")
        self.stdout.write("   └─ User Control → /user-control")
        self.stdout.write("8. Master (dropdown) [SUPERADMIN, ADMIN]")
        self.stdout.write("   ├─ Job Title → /master/job-title")
        self.stdout.write("   ├─ Department → /master/department")
        self.stdout.write("   └─ Courier → /master/courier")
        self.stdout.write(f"{'='*70}")
        
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write("USAGE:")
        self.stdout.write(f"{'='*70}")
        self.stdout.write("• Run with --assign to auto-assign menus to existing users:")
        self.stdout.write("  python manage.py seed_menus --assign")
        self.stdout.write("\n• SUPERADMIN: Gets empty menus[] (uses frontend menuConfig.js)")
        self.stdout.write("• Other roles: Get assigned menus from database")
        self.stdout.write("• Login response includes 'menus' array for frontend rendering")
        self.stdout.write(f"{'='*70}\n")

    def _assign_menus_by_role(self):
        """Auto-assign menus to users based on their roles"""
        
        # Get all menu items
        menus = {
            'dashboard': MenuItem.objects.get(code='dashboard'),
            'billing': MenuItem.objects.get(code='billing'),
            'billing_invoice_list': MenuItem.objects.get(code='billing_invoice_list'),
            'billing_reviewed': MenuItem.objects.get(code='billing_reviewed'),
            'invoices': MenuItem.objects.get(code='invoices'),
            'picking_list': MenuItem.objects.get(code='picking_list'),
            'my_assigned_picking': MenuItem.objects.get(code='my_assigned_picking'),
            'packing': MenuItem.objects.get(code='packing'),
            'packing_list': MenuItem.objects.get(code='packing_list'),
            'my_assigned_packing': MenuItem.objects.get(code='my_assigned_packing'),
            'delivery': MenuItem.objects.get(code='delivery'),
            'delivery_dispatch': MenuItem.objects.get(code='delivery_dispatch'),
            'delivery_courier_list': MenuItem.objects.get(code='delivery_courier_list'),
            'delivery_company_list': MenuItem.objects.get(code='delivery_company_list'),
            'my_assigned_delivery': MenuItem.objects.get(code='my_assigned_delivery'),
            'history': MenuItem.objects.get(code='history'),
            'history_main': MenuItem.objects.get(code='history_main'),
            'history_consolidate': MenuItem.objects.get(code='history_consolidate'),
            'user_mgmt': MenuItem.objects.get(code='user-management'),
            'user_list': MenuItem.objects.get(code='user_list'),
            'user_control': MenuItem.objects.get(code='user_control'),
            'master': MenuItem.objects.get(code='master'),
            'job_title': MenuItem.objects.get(code='job_title'),
            'department': MenuItem.objects.get(code='department'),
            'courier': MenuItem.objects.get(code='courier'),
        }

        role_menu_map = {
            'SUPERADMIN': [],  # SUPERADMIN gets empty array (uses menuConfig.js)
            'ADMIN': [
                menus['dashboard'],
                menus['invoices'], menus['picking_list'], menus['my_assigned_picking'],
                menus['delivery'], menus['delivery_dispatch'], menus['delivery_courier_list'], 
                menus['delivery_company_list'], menus['my_assigned_delivery'],
                menus['history'], menus['history_main'], menus['history_consolidate'],
                menus['user_mgmt'], menus['user_list'], menus['user_control'],
                menus['master'], menus['job_title'], menus['department'], menus['courier'],
            ],
            'USER': [
                menus['dashboard'],
                menus['invoices'], menus['picking_list'], menus['my_assigned_picking'],
                menus['history'], menus['history_main'], menus['history_consolidate'],
            ],
            'STORE': [
                menus['dashboard'],
                menus['invoices'], menus['picking_list'], menus['my_assigned_picking'],
                menus['history'], menus['history_main'], menus['history_consolidate'],
            ],
            'PICKER': [
                menus['dashboard'],
                # PICKER doesn't get invoices menu (as per menuConfig: NOT includes PICKER)
            ],
            'PACKER': [
                menus['dashboard'],
                menus['packing'], menus['packing_list'], menus['my_assigned_packing'],
            ],
            'BILLING': [  # Backend role
                menus['dashboard'],
                menus['billing'], menus['billing_invoice_list'], menus['billing_reviewed'],
            ],
            'BILLER': [  # If frontend sends this
                menus['dashboard'],
                menus['billing'], menus['billing_invoice_list'], menus['billing_reviewed'],
            ],
            'DELIVERY': [
                menus['dashboard'],
                menus['delivery'], menus['delivery_dispatch'], menus['delivery_courier_list'],
                menus['delivery_company_list'], menus['my_assigned_delivery'],
            ],
            'DRIVER': [
                menus['dashboard'],
                menus['delivery'], menus['delivery_dispatch'], menus['my_assigned_delivery'],
            ],
        }

        users = User.objects.filter(is_active=True).exclude(role='SUPERADMIN')
        assigned_count = 0

        for user in users:
            role = user.role
            assigned_menus = role_menu_map.get(role, [menus['dashboard']])
            
            for menu in assigned_menus:
                _, created = UserMenu.objects.get_or_create(
                    user=user,
                    menu=menu,
                    defaults={'is_active': True}
                )
                if created:
                    assigned_count += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ Assigned {assigned_count} menus to {users.count()} users"))