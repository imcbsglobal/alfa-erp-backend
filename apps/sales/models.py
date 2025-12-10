from django.db import models
from apps.accounts.models import User

class Salesman(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    area = models.CharField(max_length=150, blank=True)
    address1 = models.TextField(blank=True)
    address2 = models.TextField(blank=True)
    phone1 = models.CharField(max_length=20, blank=True)
    phone2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Invoice(models.Model):
    invoice_no = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateField()
    salesman = models.ForeignKey(Salesman, on_delete=models.SET_NULL, null=True)
    created_by = models.CharField(max_length=150, blank=True, null=True, help_text="Username/identifier of person who created invoice")
    created_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_invoices")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_no
    

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255, help_text="Item/product name")
    item_code = models.CharField(max_length=100)
    quantity = models.IntegerField()
    mrp = models.FloatField()
    shelf_location = models.CharField(max_length=50, blank=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.invoice.invoice_no}"
