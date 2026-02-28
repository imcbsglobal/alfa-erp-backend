from django.core.management.base import BaseCommand
from apps.sales.models import Invoice
from django.utils import timezone

class Command(BaseCommand):
    help = 'Bulk update invoice status to DELIVERED for selected statuses and date range.'

    def add_arguments(self, parser):
        parser.add_argument('--from-date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--to-date', type=str, help='End date (YYYY-MM-DD)')
        parser.add_argument('--all', action='store_true', help='Update all invoices in selected statuses')
        parser.add_argument('--statuses', nargs='+', default=['PICKED', 'INVOICED', 'PACKED'], help='Statuses to update (default: PICKED INVOICED PACKED)')

    def handle(self, *args, **options):
        statuses = [s.upper() for s in options['statuses']]
        qs = Invoice.objects.filter(status__in=statuses)
        if not options['all']:
            from_date = options.get('from_date')
            to_date = options.get('to_date')
            if from_date:
                qs = qs.filter(invoice_date__gte=from_date)
            if to_date:
                qs = qs.filter(invoice_date__lte=to_date)
        count = qs.count()
        qs.update(status='DELIVERED')
        self.stdout.write(self.style.SUCCESS(f'Updated {count} invoices to DELIVERED.'))
