from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sales.models import (
    Invoice, InvoiceItem, Customer, Salesman,
    PickingSession, PackingSession, DeliverySession
)
from apps.accounts.models import User
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Seed fake invoices for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of invoices to create (default: 20)',
        )
        parser.add_argument(
            '--with-sessions',
            action='store_true',
            help='Create picking/packing/delivery sessions for invoices',
        )
        parser.add_argument(
            '--status',
            type=str,
            default=None,
            help='Set all invoices to a specific status (INVOICED, PICKING, PICKED, PACKING, PACKED, DISPATCHED, DELIVERED)',
        )

    def handle(self, *args, **options):
        count = options['count']
        with_sessions = options['with_sessions']
        status = options['status']

        # Validate status if provided
        valid_statuses = ['INVOICED', 'PICKING', 'PICKED', 'PACKING', 'PACKED', 'DISPATCHED', 'DELIVERED']
        if status and status not in valid_statuses:
            self.stdout.write(self.style.ERROR(f"Invalid status: {status}. Must be one of: {', '.join(valid_statuses)}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Creating {count} invoices..."))

        # Create sample salesmen
        salesmen = []
        salesman_names = ["Ahmed Khan", "Fatima Ali", "Hassan Mahmood", "Ayesha Rehman", "Bilal Ahmed"]
        for name in salesman_names:
            salesman, _ = Salesman.objects.get_or_create(
                name=name,
                defaults={'phone': f"0300-{random.randint(1000000, 9999999)}"}
            )
            salesmen.append(salesman)

        # Create sample customers
        customers = []
        customer_data = [
            ("C001", "Star Medical Store", "Gulberg"),
            ("C002", "City Pharmacy", "DHA"),
            ("C003", "Health Plus", "Johar Town"),
            ("C004", "Care Medical", "Model Town"),
            ("C005", "Medix Pharmacy", "Bahria Town"),
            ("C006", "Wellness Store", "Cantt"),
            ("C007", "Life Care Pharmacy", "Garden Town"),
            ("C008", "Medicare Plus", "Allama Iqbal Town"),
        ]
        for code, name, area in customer_data:
            customer, _ = Customer.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'area': area,
                    'phone1': f"042-{random.randint(1000000, 9999999)}",
                    'address1': f"{random.randint(1, 999)} Main Street, {area}"
                }
            )
            customers.append(customer)

        # Get or create sample users for sessions
        users = list(User.objects.all()[:5])
        if not users:
            self.stdout.write(self.style.WARNING("No users found. Sessions will not have assigned users."))

        # Sample items for invoices
        items_data = [
            ("ITEM001", "Panadol Tablets", "GSK", "10x10", 25.00),
            ("ITEM002", "Aspirin 100mg", "Bayer", "100 tabs", 50.00),
            ("ITEM003", "Augmentin 625mg", "GSK", "14 tabs", 450.00),
            ("ITEM004", "Disprin", "Reckitt", "12 tabs", 30.00),
            ("ITEM005", "Brufen 400mg", "Abbott", "20 tabs", 80.00),
            ("ITEM006", "Vitamin C", "PharmEvo", "30 tabs", 120.00),
            ("ITEM007", "Multivitamin", "Pfizer", "30 tabs", 250.00),
            ("ITEM008", "Calcium Tablets", "Martin Dow", "30 tabs", 180.00),
            ("ITEM009", "Cough Syrup", "GlaxoSmithKline", "120ml", 95.00),
            ("ITEM010", "Throat Lozenges", "Halls", "20 pcs", 60.00),
        ]

        priorities = ["LOW", "MEDIUM", "HIGH"]
        statuses = ["INVOICED", "PICKING", "PICKED", "PACKING", "PACKED", "DISPATCHED", "DELIVERED"]

        invoices_created = 0
        items_created = 0
        sessions_created = 0
        
        # Get the highest existing invoice number to avoid duplicates
        current_month = datetime.now().strftime('%Y%m')
        existing_invoices = Invoice.objects.filter(
            invoice_no__startswith=f"INV-{current_month}"
        ).order_by('-invoice_no').first()
        
        if existing_invoices:
            # Extract the number part and increment
            try:
                last_number = int(existing_invoices.invoice_no.split('-')[-1])
                starting_number = last_number + 1
            except (ValueError, IndexError):
                starting_number = 10000
        else:
            starting_number = 10000

        self.stdout.write(self.style.SUCCESS(f"Starting invoice number: INV-{current_month}-{starting_number}"))

        for i in range(count):
            # Create unique invoice number
            invoice_no = f"INV-{current_month}-{starting_number + i}"
            invoice_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Use provided status or random
            invoice_status = status if status else random.choice(statuses)
            
            invoice = Invoice.objects.create(
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                salesman=random.choice(salesmen),
                customer=random.choice(customers),
                status=invoice_status,
                priority=random.choice(priorities),
                remarks=f"Test invoice {i+1}"
            )
            invoices_created += 1

            # Create 2-5 items per invoice
            num_items = random.randint(2, 5)
            selected_items = random.sample(items_data, num_items)
            
            for item_code, name, company, packing, mrp in selected_items:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    item_code=item_code,
                    name=name,
                    barcode=f"BC-{item_code}",
                    company_name=company,
                    packing=packing,
                    quantity=random.randint(1, 10),
                    mrp=mrp,
                    shelf_location=f"A{random.randint(1, 5)}-{random.randint(1, 20)}",
                    batch_no=f"BATCH-{random.randint(1000, 9999)}",
                    expiry_date=datetime.now() + timedelta(days=random.randint(180, 730))
                )
                items_created += 1

            # Create sessions if requested
            if with_sessions and users:
                # Picking session
                if invoice_status in ['PICKING', 'PICKED', 'PACKING', 'PACKED', 'DISPATCHED', 'DELIVERED']:
                    picking_status = "PICKED" if invoice_status != 'PICKING' else "PREPARING"
                    PickingSession.objects.create(
                        invoice=invoice,
                        picker=random.choice(users),
                        start_time=timezone.now() - timedelta(hours=random.randint(1, 48)),
                        end_time=timezone.now() - timedelta(hours=random.randint(0, 24)) if picking_status == "PICKED" else None,
                        picking_status=picking_status
                    )
                    sessions_created += 1

                # Packing session
                if invoice_status in ['PACKING', 'PACKED', 'DISPATCHED', 'DELIVERED']:
                    packing_status = "PACKED" if invoice_status in ['PACKED', 'DISPATCHED', 'DELIVERED'] else "IN_PROGRESS"
                    PackingSession.objects.create(
                        invoice=invoice,
                        packer=random.choice(users),
                        start_time=timezone.now() - timedelta(hours=random.randint(1, 24)),
                        end_time=timezone.now() - timedelta(hours=random.randint(0, 12)) if packing_status == "PACKED" else None,
                        packing_status=packing_status
                    )
                    sessions_created += 1

                # Delivery session
                if invoice_status in ['DISPATCHED', 'DELIVERED']:
                    delivery_status = "DELIVERED" if invoice_status == 'DELIVERED' else "IN_TRANSIT"
                    DeliverySession.objects.create(
                        invoice=invoice,
                        delivery_type=random.choice(['DIRECT', 'COURIER', 'INTERNAL']),
                        assigned_to=random.choice(users),
                        delivered_by=random.choice(users) if delivery_status == 'DELIVERED' else None,
                        start_time=timezone.now() - timedelta(hours=random.randint(1, 12)),
                        end_time=timezone.now() if delivery_status == 'DELIVERED' else None,
                        delivery_status=delivery_status
                    )
                    sessions_created += 1

        self.stdout.write(self.style.SUCCESS(f"\n✓ Created {invoices_created} invoices"))
        self.stdout.write(self.style.SUCCESS(f"✓ Created {items_created} invoice items"))
        if with_sessions:
            self.stdout.write(self.style.SUCCESS(f"✓ Created {sessions_created} sessions"))
        self.stdout.write(self.style.SUCCESS("\nDone!"))
