from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from apps.accounts.models import User
from apps.sales.models import Invoice, Customer, Salesman, PickingSession
from datetime import date


class PickingStartTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.salesman = Salesman.objects.create(name="S1")
        self.customer = Customer.objects.create(code="C1", name="Cust")
        self.invoice = Invoice.objects.create(
            invoice_no="INV-100",
            invoice_date=date.today(),
            salesman=self.salesman,
            customer=self.customer
        )

    def test_start_picking_with_user_id_creates_session(self):
        picker = User.objects.create_user(email="picker@example.com", password="pass")
        actor = User.objects.create_user(email="actor@example.com", password="pass")

        self.client.force_authenticate(user=actor)

        resp = self.client.post(
            "/api/sales/picking/start/",
            {"invoice_no": self.invoice.invoice_no, "user_id": str(picker.id), "notes": "Start"},
            format='json'
        )

        self.assertEqual(resp.status_code, 201)
        ps = PickingSession.objects.get(invoice=self.invoice)
        self.assertEqual(ps.picker.id, picker.id)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, "PENDING")

    def test_start_picking_invalid_user_returns_400(self):
        actor = User.objects.create_user(email="actor2@example.com", password="pass")
        self.client.force_authenticate(user=actor)

        resp = self.client.post(
            "/api/sales/picking/start/",
            {"invoice_no": self.invoice.invoice_no, "user_id": "00000000-0000-0000-0000-000000000000"},
            format='json'
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn('user_id', resp.data.get('errors', resp.data))

    def test_start_packing_creates_session_and_sets_selected_items(self):
        packer = User.objects.create_user(email="packer@example.com", password="pass")
        actor = User.objects.create_user(email="actor2@example.com", password="pass")

        self.client.force_authenticate(user=actor)

        resp = self.client.post(
            "/api/sales/packing/start/",
            {"invoice_no": self.invoice.invoice_no, "user_email": packer.email, "notes": "Start"},
            format='json'
        )

        self.assertEqual(resp.status_code, 201)
        ps = PackingSession.objects.get(invoice=self.invoice)
        self.assertEqual(ps.packer.id, packer.id)
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, "PACKING")
        # selected_items should be defaulted to an empty list
        self.assertEqual(ps.selected_items, [])
