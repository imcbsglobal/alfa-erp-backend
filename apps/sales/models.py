from django.db import models
from apps.accounts.models import User


#INVOICE
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
    status = models.CharField(
        max_length=20,
        choices=[
            ("CREATED", "Created"),            # invoice/order created; waiting to be processed
            ("IN_PROCESS", "In Process"),      # items being prepared/picked for the invoice
            ("PICKED", "Picked"),              # all items picked; ready for packing
            ("PACKING", "Packing"),            # packing in progress (bag/box preparation)
            ("PACKED", "Packed"),              # packing completed; ready for dispatch
            ("DISPATCHED", "Dispatched"),      # left the store / handed to delivery person
            ("DELIVERED", "Delivered"),        # delivered to customer / order completed
        ],
        default="CREATED"
    )

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


#PICKING 
class PickingSession(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    picker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    picking_status = models.CharField(
        max_length=20,
        choices=[
            ("PREPARING", "Preparing"),      # picking in progress
            ("PICKED", "Picked"),            # finished picking
            ("VERIFIED", "Verified"),        # pharmacist check
        ],
        default="PREPARING"
    )
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Packing - {self.invoice.invoice_no}"
    

# apps/sales/models.py

class PackingSession(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    packer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    packing_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),      # waiting to pack
            ("IN_PROGRESS", "In Progress"), # packing started
            ("PACKED", "Packed"),        # packing completed
        ],
        default="PENDING"
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Packing - {self.invoice.invoice_no}"

class DeliverySession(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    delivery_type = models.CharField(
        max_length=20,
        choices=[
            ("DIRECT", "Direct Delivery"),     # staff delivers to customer
            ("COURIER", "Courier Service"),    # external courier
            ("INTERNAL", "Internal Staff"),    # internal transport
        ],
        default="DIRECT"
    )
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    courier_name = models.CharField(max_length=150, blank=True, null=True)
    tracking_no = models.CharField(max_length=150, blank=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("IN_TRANSIT", "In Transit"),
            ("DELIVERED", "Delivered"),
        ],
        default="PENDING"
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Delivery - {self.invoice.invoice_no}"

