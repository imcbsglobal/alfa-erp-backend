from django.core.management.base import BaseCommand
from apps.sales.models import (
    Invoice, InvoiceItem, Customer, Salesman,
    PickingSession, PackingSession, DeliverySession
)


class Command(BaseCommand):
    help = 'Clear all sales data (invoices, customers, salesmen, sessions)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )
        parser.add_argument(
            '--sessions-only',
            action='store_true',
            help='Only clear sessions (picking, packing, delivery)',
        )
        parser.add_argument(
            '--invoices-only',
            action='store_true',
            help='Only clear invoices and items (keep customers and salesmen)',
        )

    def handle(self, *args, **options):
        confirm = options.get('confirm', False)
        sessions_only = options.get('sessions_only', False)
        invoices_only = options.get('invoices_only', False)

        # Get counts before deletion
        sessions_count = PickingSession.objects.count() + PackingSession.objects.count() + DeliverySession.objects.count()
        invoice_items_count = InvoiceItem.objects.count()
        invoices_count = Invoice.objects.count()
        customers_count = Customer.objects.count()
        salesmen_count = Salesman.objects.count()

        # Confirmation prompt
        if not confirm:
            self.stdout.write(self.style.WARNING('⚠️  WARNING: This will delete data!'))
            self.stdout.write('')
            
            if sessions_only:
                self.stdout.write(f"  • Picking/Packing/Delivery Sessions: {sessions_count}")
            elif invoices_only:
                self.stdout.write(f"  • Invoices: {invoices_count}")
                self.stdout.write(f"  • Invoice Items: {invoice_items_count}")
                self.stdout.write(f"  • Sessions: {sessions_count}")
            else:
                self.stdout.write(f"  • Invoices: {invoices_count}")
                self.stdout.write(f"  • Invoice Items: {invoice_items_count}")
                self.stdout.write(f"  • Sessions: {sessions_count}")
                self.stdout.write(f"  • Customers: {customers_count}")
                self.stdout.write(f"  • Salesmen: {salesmen_count}")
            
            self.stdout.write('')
            response = input('Type "yes" to confirm deletion: ')
            if response.lower() != 'yes':
                self.stdout.write(self.style.ERROR('❌ Deletion cancelled'))
                return

        self.stdout.write(self.style.WARNING('🗑️  Starting data deletion...'))

        # Delete data based on options
        deleted_counts = {}

        if sessions_only:
            # Only delete sessions
            deleted_counts['picking_sessions'] = PickingSession.objects.all().delete()[0]
            deleted_counts['packing_sessions'] = PackingSession.objects.all().delete()[0]
            deleted_counts['delivery_sessions'] = DeliverySession.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all sessions")

        elif invoices_only:
            # Delete sessions first (they reference invoices)
            deleted_counts['picking_sessions'] = PickingSession.objects.all().delete()[0]
            deleted_counts['packing_sessions'] = PackingSession.objects.all().delete()[0]
            deleted_counts['delivery_sessions'] = DeliverySession.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all sessions")
            
            # Delete invoice items (will cascade from invoices, but explicit is clearer)
            deleted_counts['invoice_items'] = InvoiceItem.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all invoice items")
            
            # Delete invoices
            deleted_counts['invoices'] = Invoice.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all invoices")

        else:
            # Delete everything
            deleted_counts['picking_sessions'] = PickingSession.objects.all().delete()[0]
            deleted_counts['packing_sessions'] = PackingSession.objects.all().delete()[0]
            deleted_counts['delivery_sessions'] = DeliverySession.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all sessions")
            
            deleted_counts['invoice_items'] = InvoiceItem.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all invoice items")
            
            deleted_counts['invoices'] = Invoice.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all invoices")
            
            deleted_counts['customers'] = Customer.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all customers")
            
            deleted_counts['salesmen'] = Salesman.objects.all().delete()[0]
            self.stdout.write("  ✓ Deleted all salesmen")

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("✔ DATA DELETION COMPLETED!"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        
        total_deleted = sum(deleted_counts.values())
        self.stdout.write(f"  • Total records deleted: {total_deleted}")
        self.stdout.write('')
        
        for key, count in deleted_counts.items():
            label = key.replace('_', ' ').title()
            self.stdout.write(f"  • {label}: {count}")
        
        self.stdout.write(f"{'='*60}\n")
