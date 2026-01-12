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
            ("INVOICED", "Invoiced"),          # invoice/order created; waiting to be processed
            ("PICKING", "Picking"),            # picking in progress
            ("PICKED", "Picked"),              # all items picked; ready for packing
            ("PACKING", "Packing"),            # packing in progress (bag/box preparation)
            ("PACKED", "Packed"),              # packing completed; ready for dispatch
            ("DISPATCHED", "Dispatched"),      # left the store / handed to delivery person
            ("DELIVERED", "Delivered"),        # delivered to customer / order completed
            ("REVIEW", "Under Review"),        # needs billing/admin review for corrections
        ],
        default="INVOICED"
    )

    # Priority for ordering / processing urgency
    priority = models.CharField(
        max_length=10,
        choices=[
            ("LOW", "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH", "High"),
        ],
        default="MEDIUM",
        help_text="Priority of the invoice (LOW, MEDIUM, HIGH)"
    )
    
    # Billing fields
    billing_status = models.CharField(
        max_length=20,
        choices=[
            ("BILLED", "Billed"),              # invoice has been billed
            ("REVIEW", "Under Review"),        # invoice needs review for corrections
            ("RE_INVOICED", "Re-invoiced"),    # invoice has been corrected and re-submitted
        ],
        default="BILLED",
        help_text="Billing status of the invoice"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_no


class InvoiceReturn(models.Model):
    """
    Separate model to track invoice returns for review/corrections.
    This keeps the Invoice model clean and allows for detailed return tracking.
    Multiple returns allowed - tracks full history of invoice reviews.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="invoice_returns")
    return_reason = models.TextField(help_text="Reason for sending invoice to review")
    returned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="returned_invoices", help_text="User who sent the invoice for review")
    returned_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when invoice was sent for review")
    returned_from_section = models.CharField(
        max_length=20,
        choices=[
            ("PICKING", "Picking Section"),
            ("PACKING", "Packing Section"),
            ("DELIVERY", "Delivery Section"),
        ],
        help_text="Section from which the invoice was returned for review"
    )
    resolution_notes = models.TextField(blank=True, null=True, help_text="Notes about how the issue was resolved")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the invoice was corrected and re-invoiced")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_invoices", help_text="User who resolved the issue")
    
    class Meta:
        ordering = ['-returned_at']
    
    def __str__(self):
        return f"Return: {self.invoice.invoice_no} from {self.returned_from_section}"

    
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255, help_text="Item/product name")
    item_code = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, blank=True, null=True, help_text="Item barcode")
    quantity = models.IntegerField()
    mrp = models.FloatField()
    company_name = models.CharField(max_length=100, blank=True)
    packing = models.CharField(max_length=50, blank=True)
    shelf_location = models.CharField(max_length=50, blank=True)
    batch_no = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
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
            ("CANCELLED", "Cancelled"),      # picking cancelled (e.g., sent for review)
            ("REVIEW", "Under Review"),      # picking sent for review/corrections
        ],
        default="PREPARING"
    )
    notes = models.TextField(null=True, blank=True)
    selected_items = models.JSONField(blank=True, default=list, help_text='List of item IDs that have been selected/picked so far')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Picking - {self.invoice.invoice_no}"
    

# apps/sales/models.py

class PackingSession(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    packer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    packing_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),          # waiting to pack
            ("IN_PROGRESS", "In Progress"),  # packing started
            ("PACKED", "Packed"),            # packing completed
            ("CANCELLED", "Cancelled"),      # packing cancelled (e.g., sent for review)
            ("REVIEW", "Under Review"),      # packing sent for review/corrections
        ],
        default="PENDING"
    )
    notes = models.TextField(blank=True, null=True)
    selected_items = models.JSONField(blank=True, default=list, help_text='List of item IDs that have been selected/packed so far')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Packing - {self.invoice.invoice_no}"

# Add these fields to your DeliverySession model in models.py

# Add these fields to your DeliverySession model in models.py

class DeliverySession(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    delivery_type = models.CharField(
        max_length=20,
        choices=[
            ("DIRECT", "Direct Delivery"),
            ("COURIER", "Courier Service"),
            ("INTERNAL", "Internal Staff"),
        ],
        default="DIRECT"
    )
    
    # Existing fields
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="assigned_deliveries",
        help_text="Person who dispatched/started delivery"
    )
    delivered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delivered_invoices",
        help_text="Person who completed the delivery"
    )
    courier_name = models.CharField(max_length=150, blank=True, null=True)
    tracking_no = models.CharField(max_length=150, blank=True, null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("TO_CONSIDER", "To Consider"),  # ✅ NEW: Waiting for staff assignment
            ("IN_TRANSIT", "In Transit"),
            ("DELIVERED", "Delivered"),
        ],
        default="PENDING"
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ✅ NEW FIELDS FOR COUNTER PICKUP
    counter_sub_mode = models.CharField(
        max_length=20,
        choices=[
            ("patient", "Direct Patient"),
            ("company", "Direct Company"),
        ],
        blank=True,
        null=True,
        help_text="Sub-mode for counter pickup: patient or company"
    )
    courier_slip = models.FileField(upload_to='courier_slips/', blank=True, null=True)
    pickup_person_username = models.CharField(max_length=150, blank=True, null=True)
    pickup_person_name = models.CharField(max_length=150, blank=True, null=True)
    pickup_person_phone = models.CharField(max_length=20, blank=True, null=True)
    pickup_company_name = models.CharField(max_length=255, blank=True, null=True)
    pickup_company_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"Delivery - {self.invoice.invoice_no}"

