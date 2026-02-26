# apps/sales/update_serializers.py
"""
Serializers for updating existing invoices (typically after review/corrections)
"""

from rest_framework import serializers
from .models import Invoice, InvoiceItem, InvoiceReturn, Customer, Salesman
from django.utils import timezone
from django.db import transaction


class InvoiceItemUpdateSerializer(serializers.Serializer):
    """Serializer for updating invoice items - matches by barcode (preferred) or item_code as fallback"""
    item_code = serializers.CharField(required=False, allow_blank=True, help_text="Item code (optional). Used as fallback when barcode is not provided.")
    name = serializers.CharField(required=False)
    barcode = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Barcode (preferred unique identifier for matching items)")
    quantity = serializers.IntegerField(required=False)
    mrp = serializers.FloatField(required=False)
    batch_no = serializers.CharField(required=False, allow_blank=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    company_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    packing = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shelf_location = serializers.CharField(max_length=50, required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    
    def validate_mrp(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("MRP must be greater than 0")
        return value
    
    def validate_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class InvoiceUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating an existing invoice (typically after review).
    
    Allows updating:
    - Invoice date, priority, remarks
    - Customer details
    - Salesman
    - Items (update existing, add new, or replace all)
    """
    invoice_no = serializers.CharField(help_text="Invoice number to update")
    invoice_date = serializers.DateField(required=False)
    priority = serializers.ChoiceField(
        choices=[('LOW','Low'),('MEDIUM','Medium'),('HIGH','High')], 
        required=False
    )
    remarks = serializers.CharField(required=False, allow_blank=True)
    Total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    
    # Customer updates (optional)
    customer = serializers.DictField(required=False, help_text="Customer data to update")
    
    # Salesman update (optional)
    salesman = serializers.CharField(required=False, help_text="Salesman name")
    
    # Items update
    items = InvoiceItemUpdateSerializer(many=True, required=False)
    replace_items = serializers.BooleanField(
        default=False, 
        help_text="If true, removes items not in the items list. If false, only updates/adds items."
    )
    
    # Resolution notes
    resolution_notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Notes about what was corrected"
    )
    
    def validate(self, data):
        # Validate invoice exists
        invoice_no = data.get('invoice_no')
        try:
            invoice = Invoice.objects.get(invoice_no=invoice_no)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check if invoice is in REVIEW status
        # if invoice.status != 'REVIEW' or invoice.billing_status != 'REVIEW':
        #     raise serializers.ValidationError({
        #         "invoice_no": f"Invoice must be in REVIEW status to be updated. Current status: {invoice.status}"
        #     })
        
        # Check if invoice has an InvoiceReturn record
        # if not invoice.invoice_returns.exists():
        #     raise serializers.ValidationError({
        #         "invoice_no": "Invoice has no return record. Only returned invoices can be updated via this endpoint."
        #     })
        
        data['invoice'] = invoice
        return data
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update the invoice with corrections"""
        invoice = validated_data['invoice']
        # Get the latest unresolved return record
        invoice_return = invoice.invoice_returns.filter(resolved_at__isnull=True).order_by('-returned_at').first()
        if not invoice_return:
            # If no active return, get the latest one
            invoice_return = invoice.invoice_returns.order_by('-returned_at').first()
        
        # Update basic invoice fields
        if 'invoice_date' in validated_data:
            invoice.invoice_date = validated_data['invoice_date']
        
        if 'priority' in validated_data:
            invoice.priority = validated_data['priority']
        
        if 'remarks' in validated_data:
            invoice.remarks = validated_data['remarks']
        
        if 'Total' in validated_data:
            invoice.Total = validated_data['Total']
        
        # Update customer if provided
        if 'customer' in validated_data:
            customer_data = validated_data['customer']
            if 'code' in customer_data:
                customer, _ = Customer.objects.update_or_create(
                    code=customer_data['code'],
                    defaults={
                        k: v for k, v in customer_data.items() 
                        if k in ['name', 'area', 'address1', 'address2', 'pincode', 'phone1', 'phone2', 'email']
                    }
                )
                invoice.customer = customer
        
        # Update salesman if provided
        if 'salesman' in validated_data:
            salesman, _ = Salesman.objects.get_or_create(name=validated_data['salesman'])
            invoice.salesman = salesman
        
        # Update items if provided
        if 'items' in validated_data:
            items_data = validated_data['items']
            replace_items = validated_data.get('replace_items', False)
            
            # Track which items were updated/created
            processed_item_ids = []
            
            for item_data in items_data:
                barcode = item_data.get('barcode')
                item_code = item_data.get('item_code')
                
                # Try to find existing item by barcode first (preferred), then by item_code
                existing_item = None
                if barcode:
                    existing_item = InvoiceItem.objects.filter(invoice=invoice, barcode=barcode).first()
                if not existing_item and item_code:
                    existing_item = InvoiceItem.objects.filter(invoice=invoice, item_code=item_code).first()
                
                if existing_item:
                    # Update existing item - allow updating barcode and item_code fields if provided
                    for field in ['name', 'barcode', 'item_code', 'quantity', 'mrp', 'batch_no', 'expiry_date', 
                                  'company_name', 'packing', 'shelf_location', 'remarks']:
                        if field in item_data:
                            setattr(existing_item, field, item_data[field])
                    existing_item.save()
                    processed_item_ids.append(existing_item.id)
                else:
                    # Create new item
                    new_item = InvoiceItem.objects.create(
                        invoice=invoice,
                        name=item_data.get('name', ''),
                        item_code=item_data.get('item_code', '') or '',
                        quantity=item_data.get('quantity', 1),
                        mrp=item_data.get('mrp', 0.0),
                        batch_no=item_data.get('batch_no', ''),
                        expiry_date=item_data.get('expiry_date'),
                        company_name=item_data.get('company_name', ''),
                        packing=item_data.get('packing', ''),
                        shelf_location=item_data.get('shelf_location', ''),
                        remarks=item_data.get('remarks', ''),
                        barcode=item_data.get('barcode', '') or ''
                    )
                    processed_item_ids.append(new_item.id)
            
            # If replace_items=true, delete items not in the update list
            if replace_items and processed_item_ids:
                InvoiceItem.objects.filter(invoice=invoice).exclude(
                    id__in=processed_item_ids
                ).delete()
        
        # Update InvoiceReturn record with resolution info
        resolution_notes = validated_data.get('resolution_notes', 'Invoice corrected and re-submitted')
        invoice_return.resolution_notes = resolution_notes
        invoice_return.resolved_at = timezone.now()
        if hasattr(self.context.get('request'), 'user') and self.context['request'].user.is_authenticated:
            invoice_return.resolved_by = self.context['request'].user
        invoice_return.save()
        
        # Change status back to where it was returned from
        returned_from = invoice_return.returned_from_section
        if returned_from == 'PICKING':
            invoice.status = 'PICKING'  # Return to picking status
            invoice.billing_status = 'RE_INVOICED'
            
            # Update picking session status if exists
            if hasattr(invoice, 'pickingsession'):
                picking_session = invoice.pickingsession
                if picking_session.picking_status == 'REVIEW':
                    picking_session.picking_status = 'PREPARING'
                    picking_session.notes = f"Resumed after review: {resolution_notes}"
                    picking_session.save()
                    
        elif returned_from == 'PACKING':
            invoice.status = 'PACKING'  # Return to packing status
            invoice.billing_status = 'RE_INVOICED'
            
            # Update packing session status if exists
            if hasattr(invoice, 'packingsession'):
                packing_session = invoice.packingsession
                if packing_session.packing_status == 'REVIEW':
                    packing_session.packing_status = 'IN_PROGRESS'
                    packing_session.notes = f"Resumed after review: {resolution_notes}"
                    packing_session.save()
                    
        elif returned_from == 'DELIVERY':
            invoice.status = 'PACKED'  # Ready for delivery again
            invoice.billing_status = 'RE_INVOICED'
        else:
            invoice.status = 'INVOICED'  # Default fallback
            invoice.billing_status = 'RE_INVOICED'
        
        invoice.save()
        
        return invoice
