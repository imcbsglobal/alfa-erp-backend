from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.sales.models import Invoice, Customer, Salesman
from datetime import date


class InvoicePriorityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.salesman = Salesman.objects.create(name="S1")
        self.customer = Customer.objects.create(code="C1", name="Cust")
        # default import API key used by ImportInvoiceView when not authenticated
        self.import_api_key = 'WEDFBNPOIUFSDFTY'

    def test_import_invoice_with_priority_sets_field_and_returns_priority(self):
        payload = {
            "invoice_no": "INV-PRIO-1",
            "invoice_date": date.today().isoformat(),
            "salesman": "S1",
            "created_by": "admin",
            "priority": "HIGH",
            "customer": {"code": self.customer.code, "name": self.customer.name},
            "items": [{"name": "Item", "item_code": "I1", "quantity": 1, "mrp": 10.0}]
        }

        resp = self.client.post(
            "/api/sales/import/invoice/",
            payload,
            format='json',
            HTTP_X_API_KEY=self.import_api_key,
        )

        self.assertEqual(resp.status_code, 201)
        inv = Invoice.objects.get(invoice_no="INV-PRIO-1")
        self.assertEqual(inv.priority, "HIGH")
        # Response includes priority now
        self.assertIn('data', resp.data)
        self.assertEqual(resp.data['data']['priority'], 'HIGH')

    def test_list_filter_by_priority_returns_matching_invoices(self):
        Invoice.objects.create(invoice_no="INV-LOW", invoice_date=date.today(), salesman=self.salesman, customer=self.customer, priority='LOW')
        Invoice.objects.create(invoice_no="INV-HIGH", invoice_date=date.today(), salesman=self.salesman, customer=self.customer, priority='HIGH')

        resp = self.client.get("/api/sales/invoices/?priority=HIGH")
        self.assertEqual(resp.status_code, 200)
        results = resp.data.get('results', [])
        self.assertTrue(any(r['invoice_no'] == "INV-HIGH" for r in results))
        self.assertFalse(any(r['invoice_no'] == "INV-LOW" for r in results))
