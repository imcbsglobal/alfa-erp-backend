from django.core.management.base import BaseCommand
from apps.accesscontrol.models import MenuItem, UserMenu

class Command(BaseCommand):
    help = 'Seed menu items for direct user assignment'

    def handle(self, *args, **options):
        self.stdout.write("Starting menu seeding...")

        # Clear data
        UserMenu.objects.all().delete()
        MenuItem.objects.all().delete()
        self.stdout.write("  ✓ Cleared existing menus and assignments")

        # Dashboard
        dashboard = MenuItem.objects.create(
            name="Dashboard",
            code="dashboard",
            icon="dashboard",
            url="/dashboard",
            order=1
        )
        self.stdout.write("  ✓ Dashboard menu created")

        # Delivery Management (parent)
        delivery = MenuItem.objects.create(
            name="Delivery Management",
            code="delivery",
            icon="local_shipping",
            url="/delivery",
            order=2
        )

        MenuItem.objects.create(
            name="Bills",
            code="delivery_bills",
            icon="receipt",
            url="/delivery/bills",
            parent=delivery,
            order=1
        )
        MenuItem.objects.create(
            name="Picking",
            code="delivery_picking",
            icon="inventory",
            url="/delivery/picking",
            parent=delivery,
            order=2
        )
        MenuItem.objects.create(
            name="Packing",
            code="delivery_packing",
            icon="inventory_2",
            url="/delivery/packing",
            parent=delivery,
            order=3
        )
        MenuItem.objects.create(
            name="Delivery Tasks",
            code="delivery_tasks",
            icon="local_shipping",
            url="/delivery/tasks",
            parent=delivery,
            order=4
        )

        self.stdout.write("  ✓ Delivery Management menus created")

        # Purchase Management
        purchase = MenuItem.objects.create(
            name="Purchase Management",
            code="purchase",
            icon="shopping_cart",
            url="/purchase",
            order=3
        )
        MenuItem.objects.create(
            name="Orders",
            code="purchase_orders",
            icon="list_alt",
            url="/purchase/orders",
            parent=purchase,
            order=1
        )
        MenuItem.objects.create(
            name="Vendors",
            code="purchase_vendors",
            icon="business",
            url="/purchase/vendors",
            parent=purchase,
            order=2
        )
        MenuItem.objects.create(
            name="Invoices",
            code="purchase_invoices",
            icon="description",
            url="/purchase/invoices",
            parent=purchase,
            order=3
        )
        self.stdout.write("  ✓ Purchase Management menus created")

        # Payment Follow-up
        payment = MenuItem.objects.create(
            name="Payment Follow-up",
            code="payment",
            icon="payment",
            url="/payment",
            order=4
        )
        MenuItem.objects.create(
            name="Outstanding",
            code="payment_outstanding",
            icon="account_balance",
            url="/payment/outstanding",
            parent=payment,
            order=1
        )
        MenuItem.objects.create(
            name="Follow-ups",
            code="payment_followups",
            icon="event_note",
            url="/payment/followups",
            parent=payment,
            order=2
        )
        self.stdout.write("  ✓ Payment Follow-up menus created")

        # Reports
        MenuItem.objects.create(
            name="Reports",
            code="reports",
            icon="assessment",
            url="/reports",
            order=5
        )
        self.stdout.write("  ✓ Reports menu created")

        # User Management (parent)
        user_mgmt = MenuItem.objects.create(
            name="User Management",
            code="users",
            icon="people",
            url="/user-management",
            order=6
        )
        MenuItem.objects.create(
            name="User List",
            code="user_list",
            icon="people",
            url="/user-management",
            parent=user_mgmt,
            order=1
        )
        MenuItem.objects.create(
            name="User Control",
            code="user_control",
            icon="settings",
            url="/user-control",
            parent=user_mgmt,
            order=2
        )
        MenuItem.objects.create(
            name="Add User",
            code="add_user",
            icon="person_add",
            url="/add-user",
            parent=user_mgmt,
            order=3
        )
        self.stdout.write("  ✓ User Management menu created")

        # Master (parent)
        master = MenuItem.objects.create(
            name="Master",
            code="master",
            icon="folder",
            url="/master/job-title",
            order=7
        )
        MenuItem.objects.create(
            name="Job Title",
            code="job_title",
            icon="work",
            url="/master/job-title",
            parent=master,
            order=1
        )
        self.stdout.write("  ✓ Master menu created")

        # Settings
        MenuItem.objects.create(
            name="Settings",
            code="settings",
            icon="settings",
            url="/settings",
            order=8
        )
        self.stdout.write("  ✓ Settings menu created")

        total = MenuItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\n✔ Menu seeding completed! Created {total} menu items"))
        self.stdout.write("\nNext steps:")
        self.stdout.write("  1. Go to Django Admin: /admin/")
        self.stdout.write("  2. Access Control → User menus")
        self.stdout.write("  3. Assign menus to users directly (no roles)")
