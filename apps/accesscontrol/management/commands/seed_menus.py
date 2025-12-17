from django.core.management.base import BaseCommand
from apps.accesscontrol.models import MenuItem, UserMenu


class Command(BaseCommand):
    help = 'Seed menu items matching frontend menuConfig.js exactly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing menus before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🚀 Starting menu seeding...'))

        # Clear existing data if requested
        if options.get('clear'):
            UserMenu.objects.all().delete()
            MenuItem.objects.all().delete()
            self.stdout.write(self.style.WARNING('  ✓ Cleared existing menus and assignments'))

        # ========================================
        # 1. DASHBOARD (Single)
        # ========================================
        dashboard, _ = MenuItem.objects.update_or_create(
            code="dashboard",
            defaults={
                'name': "Dashboard",
                'icon': "HomeIcon",
                'url': "/dashboard",
                'order': 1,
                'is_active': True,
                'parent': None,
            }
        )
        self.stdout.write("  ✓ Dashboard menu created")

        # ========================================
        # 2. HISTORY (Single)
        # ========================================
        history, _ = MenuItem.objects.update_or_create(
            code="history",
            defaults={
                'name': "History",
                'icon': "ListIcon",
                'url': "/history",
                'order': 2,
                'is_active': True,
                'parent': None,
            }
        )
        self.stdout.write("  ✓ History menu created")

        # ========================================
        # 3. INVOICE (Dropdown with 1 child)
        # ========================================
        # Parent dropdown - use first submenu path as default
        invoice, _ = MenuItem.objects.update_or_create(
            code="invoice",
            defaults={
                'name': "Invoice",
                'icon': "InvoiceIcon",
                'url': "/invoices",  # Use submenu path since parent has no direct path
                'order': 3,
                'is_active': True,
                'parent': None,
            }
        )

        invoice_list, _ = MenuItem.objects.update_or_create(
            code="invoice_list",
            defaults={
                'name': "Invoice List",
                'icon': "ListIcon",
                'url': "/invoices",
                'parent': invoice,
                'order': 1,
                'is_active': True,
            }
        )
        invoice_list, _ = MenuItem.objects.update_or_create(
            code="my_assigned_bills",
            defaults={
                'name': "My Assigned Bills",
                'icon': "ListIcon",
                'url': "/invoices/my",
                'parent': invoice,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Invoice menus created")

        # ========================================
        # 4. USER MANAGEMENT (Dropdown with 2 children)
        # ========================================
        user_mgmt, _ = MenuItem.objects.update_or_create(
            code="user-management",
            defaults={
                'name': "User Management",
                'icon': "UsersIcon",
                'url': "/user-management",  # Use first submenu path
                'order': 4,
                'is_active': True,
                'parent': None,
            }
        )

        user_list, _ = MenuItem.objects.update_or_create(
            code="user_list",
            defaults={
                'name': "User List",
                'icon': "UsersIcon",
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
                'icon': "CogIcon",
                'url': "/user-control",
                'parent': user_mgmt,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ User Management menus created")

        # ========================================
        # 5. MASTER (Dropdown with 2 children)
        # ========================================
        master, _ = MenuItem.objects.update_or_create(
            code="master",
            defaults={
                'name': "Master",
                'icon': "TuneOutlinedIcon",
                'url': "/master/job-title",  # Use first submenu path
                'order': 5,
                'is_active': True,
                'parent': None,
            }
        )

        job_title, _ = MenuItem.objects.update_or_create(
            code="job_title",
            defaults={
                'name': "Job Title",
                'icon': "BriefcaseIcon",
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
                'icon': "BuildingIcon",
                'url': "/master/department",
                'parent': master,
                'order': 2,
                'is_active': True,
            }
        )
        self.stdout.write("  ✓ Master menus created")

        # ========================================
        # Summary
        # ========================================
        total = MenuItem.objects.count()
        parent_menus = MenuItem.objects.filter(parent__isnull=True).count()
        child_menus = MenuItem.objects.filter(parent__isnull=False).count()
        
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("✔ MENU SEEDING COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(f"  • Total menu items: {total}")
        self.stdout.write(f"  • Parent menus: {parent_menus}")
        self.stdout.write(f"  • Child menus: {child_menus}")
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("MENU STRUCTURE (matches menuConfig.js):")
        self.stdout.write(f"{'='*60}")
        self.stdout.write("1. Dashboard (single) → /dashboard")
        self.stdout.write("2. History (single) → /history")
        self.stdout.write("3. Invoice (dropdown)")
        self.stdout.write("   └─ Invoice List → /invoices")
        self.stdout.write("4. User Management (dropdown)")
        self.stdout.write("   ├─ User List → /user-management")
        self.stdout.write("   └─ User Control → /user-control")
        self.stdout.write("5. Master (dropdown)")
        self.stdout.write("   ├─ Job Title → /master/job-title")
        self.stdout.write("   └─ Department → /master/department")
        self.stdout.write(f"{'='*60}")
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("NEXT STEPS:")
        self.stdout.write(f"{'='*60}")
        self.stdout.write("1. SUPERADMIN/ADMIN: Get all menus automatically")
        self.stdout.write("2. Other roles: Assign menus via Django Admin")
        self.stdout.write("   • Access: /admin/accesscontrol/usermenu/")
        self.stdout.write("   • Assign specific menus to users")
        self.stdout.write("3. Login response includes 'menus' array")
        self.stdout.write("4. Frontend renders menus from login data")
        self.stdout.write(f"{'='*60}\n")