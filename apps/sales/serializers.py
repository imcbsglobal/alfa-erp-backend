# apps/sales/serializers.py

from rest_framework import serializers
from .models import Invoice, InvoiceItem, InvoiceReturn, Customer, Salesman, PickingSession, PackingSession, DeliverySession, Box, BoxItem
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


def validate_user_has_menu_access(user, menu_code):
    """
    Validate that a user has access to a specific menu.
    
    Args:
        user: User instance
        menu_code: Menu code string (e.g., 'my_assigned_picking', 'my_assigned_packing')
    
    Returns:
        bool: True if user has access, False otherwise
    """
    from apps.accesscontrol.models import UserMenu, MenuItem
    
    try:
        # Check if menu exists and user has access to it
        menu_item = MenuItem.objects.get(code=menu_code, is_active=True)
        has_access = UserMenu.objects.filter(
            user=user,
            menu=menu_item,
            is_active=True
        ).exists()
        return has_access
    except MenuItem.DoesNotExist:
        return False


# ===== Serializers for list/detail views =====

class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items"""
    class Meta:
        model = InvoiceItem
        fields = ['id', 'name', 'item_code', 'barcode', 'quantity', 'mrp', 'company_name', 'packing', 'shelf_location', 'remarks', 'batch_no', 'expiry_date']


class CustomerReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for customer in invoice responses"""
    class Meta:
        model = Customer
        fields = ['code', 'name', 'area', 'address1', 'address2', 'phone1', 'phone2', 'email']


class SalesmanReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for salesman"""
    class Meta:
        model = Salesman
        fields = ['id', 'name', 'phone']


class InvoiceReturnSerializer(serializers.ModelSerializer):
    """Serializer for invoice return information"""
    returned_by_email = serializers.CharField(source='returned_by.email', read_only=True)
    returned_by_name = serializers.CharField(source='returned_by.name', read_only=True)
    resolved_by_email = serializers.CharField(source='resolved_by.email', read_only=True, allow_null=True)
    resolved_by_name = serializers.CharField(source='resolved_by.name', read_only=True, allow_null=True)
    
    class Meta:
        model = InvoiceReturn
        fields = [
            'id', 'return_reason', 'returned_by', 'returned_by_email', 'returned_by_name',
            'returned_at', 'returned_from_section', 'resolution_notes', 
            'resolved_at', 'resolved_by', 'resolved_by_email', 'resolved_by_name'
        ]


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer for invoice list and detail with nested data"""
    customer = CustomerReadSerializer(read_only=True)
    salesman = SalesmanReadSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    Total = serializers.DecimalField(max_digits=10, decimal_places=2)
    return_info = serializers.SerializerMethodField()
    picker_info = serializers.SerializerMethodField()
    packer_info = serializers.SerializerMethodField()
    delivery_info = serializers.SerializerMethodField() 
    current_handler = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_no', 'invoice_date', 'customer','status', 'priority', 'salesman', 
            'created_by', 'items', 'Total', 'temp_name', 'remarks', 'created_at',
            'billing_status', 'return_info',
            'picker_info', 'packer_info', 'delivery_info', 'current_handler' ]
    
    def get_return_info(self, obj):
        """Get return information if invoice has been returned"""
        try:
            return_obj = obj.invoice_returns.first()  # Get latest return
            return InvoiceReturnSerializer(return_obj).data
        except:
            return None
    
    def get_picker_info(self, obj):
        """Get picker information from picking session"""
        try:
            picking_session = obj.pickingsession
            return {
                "email": picking_session.picker.email if picking_session.picker else None,
                "name": picking_session.picker.name if picking_session.picker else None,
                "status": picking_session.picking_status,
                "start_time": picking_session.start_time,
                "end_time": picking_session.end_time
            }
        except:
            return None
    
    def get_packer_info(self, obj):
        """Get packer information from packing session"""
        try:
            packing_session = obj.packingsession
            return {
                "email": packing_session.packer.email if packing_session.packer else None,
                "name": packing_session.packer.name if packing_session.packer else None,
                "status": packing_session.packing_status,
                "start_time": packing_session.start_time,
                "end_time": packing_session.end_time,
                "held_for_consolidation": packing_session.held_for_consolidation,
                "consolidation_customer_name": packing_session.consolidation_customer_name,
                "held_by_email": packing_session.held_by.email if packing_session.held_by else None,
                "held_by_name": packing_session.held_by.get_full_name() or packing_session.held_by.username if packing_session.held_by else None,
            }
        except:
            return None
    
    # ✅ NEW METHOD
    def get_delivery_info(self, obj):
        """Get delivery information from delivery session"""
        try:
            delivery = obj.deliverysession
            
            # ✅ Return delivery info if session exists (regardless of invoice status)
            # This ensures delivery_info is always populated when a delivery session exists
            
            base_info = {
                "delivery_type": delivery.delivery_type,
                "delivery_status": delivery.delivery_status,
                "courier_name": delivery.courier_name,
                "tracking_no": delivery.tracking_no,
                "start_time": delivery.start_time,
                "end_time": delivery.end_time,
            }
            
            # Add counter pickup specific info
            if delivery.delivery_type == 'DIRECT':
                base_info.update({
                    "counter_sub_mode": delivery.counter_sub_mode,
                    "pickup_person_username": delivery.pickup_person_username,
                    "pickup_person_name": delivery.pickup_person_name,
                    "pickup_person_phone": delivery.pickup_person_phone,
                    "pickup_company_name": delivery.pickup_company_name,
                    "pickup_company_id": delivery.pickup_company_id,
                })
            
            # Add person info based on status
            if obj.status == 'DISPATCHED':
                base_info.update({
                    "name": delivery.assigned_to.name if delivery.assigned_to else None,
                    "email": delivery.assigned_to.email if delivery.assigned_to else None,
                    "status": "DISPATCHED",
                    "time": delivery.start_time,
                })
            elif obj.status == 'DELIVERED':
                base_info.update({
                    "name": delivery.delivered_by.name if delivery.delivered_by else None,
                    "email": delivery.delivered_by.email if delivery.delivered_by else None,
                    "status": "DELIVERED",
                    "time": delivery.end_time,
                })
            elif delivery.delivery_status == 'TO_CONSIDER':
                base_info.update({
                    "name": delivery.assigned_to.name if delivery.assigned_to else None,
                    "email": delivery.assigned_to.email if delivery.assigned_to else None,
                    "status": "TO_CONSIDER",
                    "time": delivery.start_time,
                })
            
            return base_info
            
        except DeliverySession.DoesNotExist:
            return None
        except Exception:
            return None
    
    def get_current_handler(self, obj):
        """Get current handler based on invoice status"""
        if obj.status in ['PICKING', 'PICKED']:
            return self.get_picker_info(obj)
        
        elif obj.status in ['PACKING', 'PACKED']:
            return self.get_packer_info(obj)
        
        elif obj.status == 'DISPATCHED':
            try:
                delivery = obj.deliverysession
                return {
                    "name": delivery.assigned_to.name if delivery.assigned_to else None,
                    "email": delivery.assigned_to.email if delivery.assigned_to else None,
                    "status": "DISPATCHED",
                    "mode": delivery.delivery_type,
                    "courier_name": delivery.courier_name,
                    "tracking_no": delivery.tracking_no,
                    "start_time": delivery.start_time,
                    "end_time": None,
                }
            except:
                return None
        
        elif obj.status == 'DELIVERED':
            try:
                delivery = obj.deliverysession
                return {
                    "name": delivery.delivered_by.name if delivery.delivered_by else None,
                    "email": delivery.delivered_by.email if delivery.delivered_by else None,
                    "status": "DELIVERED",
                    "mode": delivery.delivery_type,
                    "courier_name": delivery.courier_name,
                    "tracking_no": delivery.tracking_no,
                    "start_time": delivery.start_time,
                    "end_time": delivery.end_time,
                }
            except:
                return None
        
        elif obj.status == 'REVIEW':
            return_info = self.get_return_info(obj)
            if return_info:
                return {
                    "email": return_info.get('returned_by_email'),
                    "name": return_info.get('returned_by_name'),
                    "status": "REVIEW",
                    "returned_at": return_info.get('returned_at'),
                    "returned_from": return_info.get('returned_from_section')
                }
        
        return None


# ===== Serializers for import =====

class CustomerSerializer(serializers.Serializer):
    """Serializer for customer data in invoice import (allows update or create)"""
    code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    area = serializers.CharField(max_length=150, required=False, allow_blank=True)
    address1 = serializers.CharField(required=False, allow_blank=True)
    address2 = serializers.CharField(required=False, allow_blank=True)
    phone1 = serializers.CharField(max_length=20, required=False, allow_blank=True)
    phone2 = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)


class ItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    item_code = serializers.CharField()
    quantity = serializers.IntegerField()
    mrp = serializers.FloatField()
    shelf_location = serializers.CharField(max_length=50, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    batch_no = serializers.CharField(required=False, allow_blank=True)
    expiry_date = serializers.DateField(required=False, allow_null=True)
    company_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    packing = serializers.CharField(max_length=100, required=False, allow_blank=True)
    barcode = serializers.CharField(required=False, allow_blank=True)

class InvoiceImportSerializer(serializers.Serializer):
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    salesman = serializers.CharField()
    created_by = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=[('LOW','Low'),('MEDIUM','Medium'),('HIGH','High')], required=False, default='MEDIUM')
    Total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True   # 👈 MUST BE REQUIRED
    )
    temp_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    customer = CustomerSerializer()
    items = ItemSerializer(many=True)

    def create(self, validated_data):
        customer_data = validated_data.pop("customer")
        items_data = validated_data.pop("items")
        salesman_name = validated_data.pop("salesman")
        Total = validated_data.pop("Total")  # REQUIRED

        salesman, _ = Salesman.objects.get_or_create(name=salesman_name)

        customer, _ = Customer.objects.update_or_create(
            code=customer_data["code"],
            defaults=customer_data
        )

        invoice = Invoice.objects.create(
            customer=customer,
            salesman=salesman,
            Total=Total,
            **validated_data
        )

        for item in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item)

        return invoice

#Picking
class PickingSessionCreateSerializer(serializers.Serializer):
    """Start picking session - requires user email scan"""
    invoice_no = serializers.CharField()
    user_email = serializers.EmailField(help_text="Scanned user email to start picking")
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})

        # Check invoice status
        if invoice.status not in ['CREATED', 'INVOICED']:
            raise serializers.ValidationError({
                "invoice_no": f"Invoice cannot be picked in '{invoice.status}' state."
            })

        # Prevent duplicate picking session
        if hasattr(invoice, 'pickingsession'):
            raise serializers.ValidationError({"invoice_no": "Picking session already exists for this invoice."})

        # Verify user
        try:
            user = User.objects.get(email=data['user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_email": "User not found. Please scan a valid email."})
        
        # Validate menu access - user must have 'my_assigned_picking' menu access
        if not validate_user_has_menu_access(user, 'my_assigned_picking'):
            raise serializers.ValidationError({
                "user_email": f"User {user.email} does not have access to picking functionality. Please contact admin to assign the 'My Assigned Picking' menu."
            })

        data['invoice'] = invoice
        data['user'] = user
        return data

    def create(self, validated_data):
        invoice = validated_data['invoice']
        user = validated_data['user']
        notes = validated_data.get('notes', '')

        picking_session = PickingSession.objects.create(
            invoice=invoice,
            picker=user,
            start_time=timezone.now(),
            picking_status="PREPARING",
            notes=notes,
            selected_items=[]
        )

        # Update invoice status
        invoice.status = "PICKING"
        invoice.save(update_fields=["status"])

        return picking_session


class PickingSessionReadSerializer(serializers.ModelSerializer):
    """Read serializer for picking session details"""
    picker_name = serializers.CharField(source='picker.name', read_only=True)
    picker_email = serializers.CharField(source='picker.email', read_only=True)
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = PickingSession
        fields = [
            'id', 'invoice', 'invoice_no', 'picker', 'picker_name', 'picker_email',
            'start_time', 'end_time', 'picking_status', 'notes', 
            'duration_minutes', 'created_at'
        ]
    
    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)
        return None


class CompletePickingSerializer(serializers.Serializer):
    """Serializer to complete picking - requires user email scan"""
    invoice_no = serializers.CharField()
    user_email = serializers.EmailField(help_text="Scanned user email for verification")
    notes = serializers.CharField(required=False, allow_blank=True)
    is_repick = serializers.BooleanField(required=False, default=False)  # ✅ NEW FLAG
    
    def validate(self, data):
        # Validate invoice exists
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        is_repick = data.get('is_repick', False)
        
        # Verify user email
        try:
            user = User.objects.get(email=data['user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_email": "User not found. Please scan a valid email."})
        
        # ✅ For re-invoiced bills, create or reset picking session automatically
        if is_repick and invoice.billing_status == 'RE_INVOICED':
            # Check if picking session exists
            if hasattr(invoice, 'pickingsession'):
                picking_session = invoice.pickingsession
                # Reset the existing session for re-pick
                picking_session.picker = user
                picking_session.start_time = timezone.now()
                picking_session.end_time = None
                picking_session.picking_status = "PREPARING"
                picking_session.notes = (picking_session.notes or '') + "\nRe-started for re-invoiced bill"
                picking_session.save()
            else:
                # Create new picking session
                picking_session = PickingSession.objects.create(
                    invoice=invoice,
                    picker=user,
                    start_time=timezone.now(),
                    picking_status="PREPARING",
                    notes="Auto-started for re-invoiced bill",
                    selected_items=[]
                )
            
            # Update invoice status
            invoice.status = "PICKING"
            invoice.save(update_fields=["status"])
        
        # Check if picking session exists
        try:
            picking_session = PickingSession.objects.get(invoice=invoice)
        except PickingSession.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "No picking session found for this invoice."})
        
        # Verify it's the same user who started picking (or re-pick user)
        if picking_session.picker and picking_session.picker.email != user.email:
            raise serializers.ValidationError({
                "user_email": f"Email mismatch. This invoice was started by {picking_session.picker.name} ({picking_session.picker.email}). Please scan the correct email."
            })
        
        # ✅ Only check if already completed for non-repick cases
        if not is_repick and picking_session.picking_status == "PICKED":
            raise serializers.ValidationError({"invoice_no": "Picking already completed for this invoice."})
        
        data['invoice'] = invoice
        data['picking_session'] = picking_session
        data['user'] = user
        return data

# ===== PACKING SERIALIZERS =====

class PackingSessionCreateSerializer(serializers.Serializer):
    """Start packing session - requires user email scan"""
    invoice_no = serializers.CharField()
    user_email = serializers.EmailField(help_text="Scanned user email to start packing")
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check invoice status
        if invoice.status != 'PICKED':
            raise serializers.ValidationError({
                "invoice_no": f"Invoice must be in PICKED status. Current status: {invoice.status}"
            })
        
        # Prevent duplicate packing session
        if hasattr(invoice, 'packingsession'):
            raise serializers.ValidationError({"invoice_no": "Packing session already exists for this invoice."})
        
        # Verify user
        try:
            user = User.objects.get(email=data['user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_email": "User not found. Please scan a valid email."})
        
        # Validate menu access - user must have 'my_assigned_packing' menu access
        if not validate_user_has_menu_access(user, 'my_assigned_packing'):
            raise serializers.ValidationError({
                "user_email": f"User {user.email} does not have access to packing functionality. Please contact admin to assign the 'My Assigned Packing' menu."
            })
        
        data['invoice'] = invoice
        data['user'] = user
        return data


class PackingSessionReadSerializer(serializers.ModelSerializer):
    """Read serializer for packing session details"""
    packer_name = serializers.CharField(source='packer.name', read_only=True)
    packer_email = serializers.CharField(source='packer.email', read_only=True)
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = PackingSession
        fields = [
            'id', 'invoice', 'invoice_no', 'packer', 'packer_name', 'packer_email',
            'start_time', 'end_time', 'packing_status', 'notes',
            'duration_minutes', 'created_at'
        ]
    
    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)
        return None


class CompletePackingSerializer(serializers.Serializer):
    """Complete packing - requires user email scan"""
    invoice_no = serializers.CharField()
    user_email = serializers.EmailField(help_text="Scanned user email for verification")
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check packing session
        try:
            packing_session = PackingSession.objects.get(invoice=invoice)
        except PackingSession.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "No packing session found for this invoice."})
        
        # Verify user
        try:
            user = User.objects.get(email=data['user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_email": "User not found. Please scan a valid email."})
        
        # Verify same user
        if packing_session.packer and packing_session.packer.email != user.email:
            raise serializers.ValidationError({
                "user_email": f"Email mismatch. This invoice was started by {packing_session.packer.name} ({packing_session.packer.email})."
            })
        
        # Check status
        if packing_session.packing_status == "PACKED":
            raise serializers.ValidationError({"invoice_no": "Packing already completed."})
        
        data['invoice'] = invoice
        data['packing_session'] = packing_session
        data['user'] = user
        return data


# ===== DELIVERY SERIALIZERS =====

# Update these serializers in serializers.py

# Update these serializers in serializers.py

class DeliverySessionCreateSerializer(serializers.Serializer):
    """Start delivery session - handles counter pickup and delivery modes"""
    invoice_no = serializers.CharField()
    delivery_type = serializers.ChoiceField(choices=['DIRECT', 'COURIER', 'INTERNAL'])
    
    # For courier delivery
    courier_id = serializers.UUIDField(required=False, allow_null=True)
    courier_name = serializers.CharField(required=False, allow_blank=True)
    tracking_no = serializers.CharField(required=False, allow_blank=True)
    
    # For internal delivery
    user_email = serializers.EmailField(required=False, allow_null=True)
    user_name = serializers.CharField(required=False, allow_blank=True)
    
    # For counter pickup (DIRECT)
    counter_sub_mode = serializers.ChoiceField(
        choices=['patient', 'company'], 
        required=False, 
        allow_blank=True
    )
    pickup_person_username = serializers.CharField(required=False, allow_blank=True)
    pickup_person_name = serializers.CharField(required=False, allow_blank=True)
    pickup_person_phone = serializers.CharField(required=False, allow_blank=True)
    pickup_company_name = serializers.CharField(required=False, allow_blank=True)
    pickup_company_id = serializers.CharField(required=False, allow_blank=True)
    
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check invoice status
        if invoice.status != 'PACKED':
            raise serializers.ValidationError({
                "invoice_no": f"Invoice must be in PACKED status. Current status: {invoice.status}"
            })
        
        # Prevent duplicate delivery session
        if hasattr(invoice, 'deliverysession'):
            raise serializers.ValidationError({
                "invoice_no": "Delivery session already exists for this invoice."
            })
        
        delivery_type = data.get('delivery_type')
        
        # For DIRECT (counter pickup), validate required fields
        if delivery_type == 'DIRECT':
            counter_sub_mode = data.get('counter_sub_mode')
            if not counter_sub_mode:
                raise serializers.ValidationError({
                    "counter_sub_mode": "Counter sub-mode (patient/company) is required for counter pickup."
                })
            
            # Validate required fields for counter pickup
            if not data.get('pickup_person_username'):
                raise serializers.ValidationError({
                    "pickup_person_username": "Username is required for counter pickup."
                })
            if not data.get('pickup_person_name'):
                raise serializers.ValidationError({
                    "pickup_person_name": "Person name is required for counter pickup."
                })
            if not data.get('pickup_person_phone'):
                raise serializers.ValidationError({
                    "pickup_person_phone": "Phone number is required for counter pickup."
                })
            
            # For company pickup, validate company details
            if counter_sub_mode == 'company':
                if not data.get('pickup_company_name'):
                    raise serializers.ValidationError({
                        "pickup_company_name": "Company name is required for company pickup."
                    })
                if not data.get('pickup_company_id'):
                    raise serializers.ValidationError({
                        "pickup_company_id": "Company ID is required for company pickup."
                    })
        
        # For COURIER, courier_name is optional (will be added when staff completes delivery)
        # No additional validation needed here
        
        data['invoice'] = invoice
        return data


class DeliverySessionReadSerializer(serializers.ModelSerializer):
    """Read serializer for delivery session details"""
    assigned_to_name = serializers.CharField(source='assigned_to.name', read_only=True)
    assigned_to_email = serializers.CharField(source='assigned_to.email', read_only=True)
    delivered_by_name = serializers.CharField(source='delivered_by.name', read_only=True)
    delivered_by_email = serializers.CharField(source='delivered_by.email', read_only=True)
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = DeliverySession
        fields = [
            'id', 'invoice', 'invoice_no', 'delivery_type', 
            'assigned_to', 'assigned_to_name', 'assigned_to_email',
            'delivered_by', 'delivered_by_name', 'delivered_by_email',
            'courier_name', 'tracking_no',
            'start_time', 'end_time', 'delivery_status', 'notes',
            'duration_minutes', 'created_at',
            # Counter pickup fields
            'counter_sub_mode', 'pickup_person_username', 'pickup_person_name',
            'pickup_person_phone', 'pickup_company_name', 'pickup_company_id'
        ]
    
    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)
        return None

class CompleteDeliverySerializer(serializers.Serializer):
    """Complete delivery - requires user email scan for verification"""
    invoice_no = serializers.CharField()
    user_email = serializers.EmailField(required=False, allow_blank=True, help_text="Scanned user email for verification")
    delivery_status = serializers.ChoiceField(choices=['DELIVERED', 'IN_TRANSIT'], default='DELIVERED')
    notes = serializers.CharField(required=False, allow_blank=True)
    
    # Courier-specific fields
    courier_name = serializers.CharField(required=False, allow_blank=True, help_text="Courier name for COURIER delivery type")
    tracking_no = serializers.CharField(required=False, allow_blank=True, help_text="Tracking number for COURIER delivery")
    delivery_latitude = serializers.DecimalField(max_digits=10, decimal_places=8, required=False, allow_null=True)
    delivery_longitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=False, allow_null=True)
    delivery_location_address = serializers.CharField(required=False, allow_blank=True)
    delivery_location_accuracy = serializers.FloatField(required=False, allow_null=True)
    
    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check delivery session
        try:
            delivery_session = DeliverySession.objects.get(invoice=invoice)
        except DeliverySession.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "No delivery session found for this invoice."})
        
        # Validate courier details for COURIER type deliveries
        if delivery_session.delivery_type == 'COURIER' and data.get('delivery_status') == 'DELIVERED':
            courier_name = data.get('courier_name', '').strip()
            if not courier_name:
                raise serializers.ValidationError({
                    "courier_name": "Courier name is required for completing courier deliveries."
                })
        
        # If user_email provided, verify
        user_email = data.get('user_email')
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                # Verify same user for DIRECT/INTERNAL delivery
                if delivery_session.delivery_type in ['DIRECT', 'INTERNAL']:
                    if delivery_session.assigned_to and delivery_session.assigned_to.email != user.email:
                        raise serializers.ValidationError({
                            "user_email": f"Email mismatch. This delivery was assigned to {delivery_session.assigned_to.name} ({delivery_session.assigned_to.email})."
                        })
                data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({"user_email": "User not found. Please scan a valid email."})
        
        # Check status
        if delivery_session.delivery_status == "DELIVERED":
            raise serializers.ValidationError({"invoice_no": "Delivery already completed."})
        
        data['invoice'] = invoice
        data['delivery_session'] = delivery_session
        return data

# ===== History Serializers =====

class PickingHistorySerializer(serializers.ModelSerializer):
    """Serializer for picking session history with invoice and timing details"""
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    invoice_date = serializers.DateField(source='invoice.invoice_date', read_only=True)
    invoice_status = serializers.CharField(source='invoice.status', read_only=True)
    invoice_remarks = serializers.CharField(source='invoice.remarks', read_only=True)
    customer_name = serializers.CharField(source='invoice.customer.name', read_only=True)
    customer_email = serializers.CharField(source='invoice.customer.email', read_only=True)
    customer_phone = serializers.CharField(source='invoice.customer.phone1', read_only=True)
    customer_address = serializers.CharField(source='invoice.customer.address1', read_only=True)
    salesman_name = serializers.CharField(source='invoice.salesman.name', read_only=True)
    picker_email = serializers.CharField(source='picker.email', read_only=True)
    picker_name = serializers.CharField(source='picker.name', read_only=True)
    temp_name = serializers.CharField(source='invoice.temp_name', read_only=True)
    items = InvoiceItemSerializer(source='invoice.items', many=True, read_only=True)
    Total = serializers.DecimalField(
        source='invoice.Total',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = PickingSession
        fields = [
            'id', 'invoice_no', 'invoice_date', 'invoice_status', 'invoice_remarks',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'salesman_name', 'picker_email', 'picker_name', 'temp_name', 'picking_status',
            'items', 'Total', 'start_time', 'end_time', 'duration', 'notes', 'created_at'
        ]
    
    # def get_total_amount(self, obj):
    #     """Calculate total amount from invoice items"""
    #     return sum(item.quantity * item.mrp for item in obj.invoice.items.all())
    
    def get_duration(self, obj):
        """Calculate duration in minutes"""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)  # minutes
        return None


class PackingHistorySerializer(serializers.ModelSerializer):
    """Serializer for packing session history with invoice and timing details"""
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    invoice_date = serializers.DateField(source='invoice.invoice_date', read_only=True)
    invoice_status = serializers.CharField(source='invoice.status', read_only=True)
    invoice_remarks = serializers.CharField(source='invoice.remarks', read_only=True)
    customer_name = serializers.CharField(source='invoice.customer.name', read_only=True)
    customer_email = serializers.CharField(source='invoice.customer.email', read_only=True)
    customer_phone = serializers.CharField(source='invoice.customer.phone1', read_only=True)
    customer_address = serializers.CharField(source='invoice.customer.address1', read_only=True)
    salesman_name = serializers.CharField(source='invoice.salesman.name', read_only=True)
    packer_email = serializers.CharField(source='packer.email', read_only=True)
    packer_name = serializers.CharField(source='packer.name', read_only=True)
    temp_name = serializers.CharField(source='invoice.temp_name', read_only=True)
    items = InvoiceItemSerializer(source='invoice.items', many=True, read_only=True)
    Total = serializers.DecimalField(
        source='invoice.Total',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = PackingSession
        fields = [
            'id', 'invoice_no', 'invoice_date', 'invoice_status', 'invoice_remarks',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'salesman_name', 'packer_email', 'packer_name', 'temp_name', 'packing_status',
            'items', 'Total', 'start_time', 'end_time', 'duration', 'notes', 'created_at'
        ]
    
    # def get_total_amount(self, obj):
    #     """Calculate total amount from invoice items"""
    #     return sum(item.quantity * item.mrp for item in obj.invoice.items.all())
    
    def get_duration(self, obj):
        """Calculate duration in minutes"""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)  # minutes
        return None


class DeliveryHistorySerializer(serializers.ModelSerializer):
    """Serializer for delivery session history with invoice and timing details"""
    invoice_no = serializers.CharField(source='invoice.invoice_no', read_only=True)
    invoice_date = serializers.DateField(source='invoice.invoice_date', read_only=True)
    invoice_status = serializers.CharField(source='invoice.status', read_only=True)
    invoice_remarks = serializers.CharField(source='invoice.remarks', read_only=True)
    customer_name = serializers.CharField(source='invoice.customer.name', read_only=True)
    customer_email = serializers.CharField(source='invoice.customer.email', read_only=True)
    customer_phone = serializers.CharField(source='invoice.customer.phone1', read_only=True)
    temp_name = serializers.CharField(source='invoice.temp_name', read_only=True)
    customer_address = serializers.CharField(source='invoice.customer.address1', read_only=True)
    salesman_name = serializers.CharField(source='invoice.salesman.name', read_only=True)
    delivery_user_email = serializers.CharField(source='assigned_to.email', read_only=True)
    delivery_user_name = serializers.CharField(source='assigned_to.name', read_only=True)
    items = InvoiceItemSerializer(source='invoice.items', many=True, read_only=True)
    Total = serializers.DecimalField(
        source='invoice.Total',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    duration = serializers.SerializerMethodField()
    courier_slip_url = serializers.SerializerMethodField()  # ✅ NEW FIELD
    
    class Meta:
        model = DeliverySession
        fields = [
            'id', 'invoice_no', 'invoice_date', 'invoice_status', 'invoice_remarks',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'salesman_name', 'temp_name', 'delivery_type', 'delivery_user_email', 'delivery_user_name',
            'courier_name', 'tracking_no', 'delivery_status', 'items', 'Total',
            'start_time', 'end_time', 'duration', 'notes', 'created_at',
            'courier_slip_url','delivery_latitude', 'delivery_longitude', 
            'delivery_location_address', 'delivery_location_accuracy'
        ]
    
    # def get_total_amount(self, obj):
    #     """Calculate total amount from invoice items"""
    #     return sum(item.quantity * item.mrp for item in obj.invoice.items.all())
    
    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() // 60)  # duration in minutes
        return None
    
    def get_courier_slip_url(self, obj):
        """Return the full URL of the courier slip if it exists"""
        if obj.courier_slip:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.courier_slip.url)
            return obj.courier_slip.url
        return None

# ===== Billing Serializers =====

class BillingHistorySerializer(serializers.ModelSerializer):
    """Serializer for billing history with invoice creation details"""
    invoice_no = serializers.CharField(read_only=True)
    invoice_date = serializers.DateField(read_only=True)
    invoice_status = serializers.CharField(source='status', read_only=True)
    invoice_remarks = serializers.CharField(source='remarks', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone1', read_only=True)
    customer_address = serializers.CharField(source='customer.address1', read_only=True)
    salesman_name = serializers.CharField(source='salesman.name', read_only=True)
    biller_email = serializers.CharField(source='created_user.email', read_only=True)
    biller_name = serializers.CharField(source='created_user.name', read_only=True)
    temp_name = serializers.CharField(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    Total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    start_time = serializers.DateTimeField(source='created_at', read_only=True)
    end_time = serializers.DateTimeField(source='created_at', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_no', 'invoice_date', 'invoice_status', 'invoice_remarks',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'salesman_name', 'biller_email', 'biller_name', 'temp_name', 'billing_status',
            'items', 'Total', 'start_time', 'end_time', 'duration', 'created_at'
        ]
    
    def get_duration(self, obj):
        """For billing, duration is instant (0 minutes)"""
        return 0


class ReturnToBillingSerializer(serializers.Serializer):
    """Serializer for returning an invoice to billing for corrections"""
    invoice_no = serializers.CharField(help_text="Invoice number to return")
    return_reason = serializers.CharField(
        help_text="Reason for returning: missing items, wrong batch number, out of stock, etc."
    )
    user_email = serializers.EmailField(
        required=False,
        help_text="Email of user returning the invoice (optional, defaults to authenticated user)"
    )

    def validate(self, data):
        # Validate invoice exists
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})

        # Check if invoice can be returned (should be in picking, packing, or picked state)
        allowed_statuses = ['PICKING', 'PICKED', 'PACKING', 'PACKED', 'DISPATCHED']
        if invoice.status not in allowed_statuses:
            raise serializers.ValidationError({
                "invoice_no": f"Invoice in '{invoice.status}' state cannot be returned to billing. Only invoices in PICKING, PICKED, PACKING, PACKED, or DISPATCHED state can be returned."
            })

        # Check if already in review (has InvoiceReturn record)
        if invoice.billing_status == 'REVIEW' or invoice.invoice_returns.filter(resolved_at__isnull=True).exists():
            raise serializers.ValidationError({
                "invoice_no": "Invoice has already been sent for review."
            })

        data['invoice'] = invoice
        return data
    
    def get_duration(self, obj):
        """Calculate duration in minutes"""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 2)  # minutes
        return None


class CourierSerializer(serializers.ModelSerializer):
    """Serializer for Courier model"""
    
    class Meta:
        from apps.accounts.models import Courier
        model = Courier
        fields = [
            'courier_id',
            'courier_code',
            'courier_name',
            'type',
            'contact_person',
            'phone',
            'alt_phone',
            'email',
            'address',
            'service_area',
            'rate_type',
            'base_rate',
            'vehicle_type',
            'max_weight',
            'cod_supported',
            'status',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['courier_id', 'created_at', 'updated_at']
    
    def validate_courier_code(self, value):
        """Validate courier code is unique on create"""
        from apps.accounts.models import Courier
        
        if self.instance is None:  # Creating new courier
            if Courier.objects.filter(courier_code=value).exists():
                raise serializers.ValidationError("Courier code already exists.")
        else:  # Updating existing courier
            if Courier.objects.filter(courier_code=value).exclude(courier_id=self.instance.courier_id).exists():
                raise serializers.ValidationError("Courier code already exists.")
        return value
    
    def validate_email(self, value):
        """Validate email format if provided"""
        if value and value.strip():
            return value.strip()
        return value
    
    def validate_phone(self, value):
        """Validate phone is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Phone number is required.")
        return value.strip()
    
    def validate_base_rate(self, value):
        """Validate base rate is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Base rate cannot be negative.")
        return value
    
    def validate_max_weight(self, value):
        """Validate max weight is non-negative if provided"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Max weight cannot be negative.")
        return value


# ===== BOX-BASED PACKING WORKFLOW SERIALIZERS =====

class StartCheckingSerializer(serializers.Serializer):
    """Start checking/verification of a picked bill"""
    invoice_no = serializers.CharField()
    user_email = serializers.EmailField(help_text="User email who is checking the bill")
    
    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check invoice status - must be PICKED or PACKING
        if invoice.status not in ['PICKED', 'PACKING']:
            raise serializers.ValidationError({
                "invoice_no": f"Invoice must be in PICKED or PACKING status. Current status: {invoice.status}"
            })
        
        # Get or create packing session
        packing_session, _ = PackingSession.objects.get_or_create(
            invoice=invoice,
            defaults={'packing_status': 'PENDING'}
        )
        
        # Verify user
        try:
            user = User.objects.get(email=data['user_email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_email": "User not found."})
        
        # Validate menu access
        if not validate_user_has_menu_access(user, 'my_assigned_packing'):
            raise serializers.ValidationError({
                "user_email": f"User {user.email} does not have access to packing functionality."
            })
        
        data['invoice'] = invoice
        data['packing_session'] = packing_session
        data['user'] = user
        return data


class CompleteCheckingSerializer(serializers.Serializer):
    """Complete checking/verification phase"""
    invoice_no = serializers.CharField()
    hold_for_consolidation = serializers.BooleanField(default=False, required=False, help_text="Whether to hold this bill for consolidation with future bills")
    customer_name = serializers.CharField(required=False, allow_blank=True, help_text="Customer name for grouping held bills")
    assign_to_user_email = serializers.EmailField(required=False, allow_blank=True, help_text="Email of user to assign this held bill to")
    
    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})
        
        # Check packing session
        try:
            packing_session = PackingSession.objects.get(invoice=invoice)
        except PackingSession.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "No packing session found for this invoice."})
        
        # Check status - allow CHECKING, PENDING, or already CHECKING_DONE (idempotent)
        if packing_session.packing_status not in ['CHECKING', 'PENDING', 'CHECKING_DONE']:
            raise serializers.ValidationError({
                "invoice_no": f"Cannot complete checking. Current status: {packing_session.packing_status}. Expected CHECKING, PENDING, or CHECKING_DONE."
            })
        
        data['invoice'] = invoice
        data['packing_session'] = packing_session
        data['already_done'] = (packing_session.packing_status == 'CHECKING_DONE')
        return data


class BoxItemInputSerializer(serializers.Serializer):
    """Serializer for box item input"""
    item_id = serializers.IntegerField()
    item_name = serializers.CharField(read_only=True)
    item_code = serializers.CharField(required=False, allow_blank=True)
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)


class BoxInputSerializer(serializers.Serializer):
    """Serializer for box input during packing completion"""
    box_id = serializers.CharField(max_length=100)
    items = BoxItemInputSerializer(many=True)
    
    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Box must contain at least one item.")
        return items



class CompletePackingWithBoxesSerializer(serializers.Serializer):
    """Complete packing with box assignments"""
    invoice_no = serializers.CharField()
    boxes = BoxInputSerializer(many=True)
    has_same_address_bills = serializers.BooleanField(default=False)

    def validate(self, data):
        # Validate invoice
        try:
            invoice = Invoice.objects.get(invoice_no=data['invoice_no'])
        except Invoice.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "Invoice not found."})

        # Check packing session
        try:
            packing_session = PackingSession.objects.get(invoice=invoice)
        except PackingSession.DoesNotExist:
            raise serializers.ValidationError({"invoice_no": "No packing session found for this invoice."})

        # Check status - allow CHECKING_DONE, PACKING, IN_PROGRESS, or CHECKING
        if packing_session.packing_status not in ['CHECKING_DONE', 'PACKING', 'IN_PROGRESS', 'CHECKING']:
            raise serializers.ValidationError({
                "invoice_no": f"Cannot complete packing. Current status: {packing_session.packing_status}"
            })

        # Validate boxes
        boxes = data.get('boxes', [])
        if not boxes:
            raise serializers.ValidationError({"boxes": "At least one box is required."})

        # Get all invoice items
        invoice_items = {item.id: item for item in invoice.items.all()}

        # Track quantities per item
        item_quantities = {item_id: 0 for item_id in invoice_items.keys()}
        required_quantities = {item.id: item.quantity for item in invoice_items.values()}

        # Validate each box and aggregate quantities
        for box_idx, box_data in enumerate(boxes):
            box_id = box_data.get('box_id')
            box_items = box_data.get('items', [])

            if not box_items:
                raise serializers.ValidationError({
                    "boxes": f"Box {box_id} is empty. All boxes must contain items."
                })

            for item_data in box_items:
                item_id = item_data.get('item_id')
                quantity = item_data.get('quantity')

                # Validate item exists in invoice
                if item_id not in invoice_items:
                    raise serializers.ValidationError({
                        "boxes": f"Item ID {item_id} in box {box_id} not found in invoice."
                    })

                # Aggregate quantity
                item_quantities[item_id] += quantity

        # Validate all items are fully assigned and quantities match
        errors = []
        for item_id, required_qty in required_quantities.items():
            assigned_qty = item_quantities[item_id]
            item_name = invoice_items[item_id].name

            if assigned_qty == 0:
                errors.append(f"Item '{item_name}' is not assigned to any box.")
            elif assigned_qty < required_qty:
                errors.append(f"Item '{item_name}': {assigned_qty} assigned, {required_qty} required. Missing {required_qty - assigned_qty}.")
            elif assigned_qty > required_qty:
                errors.append(f"Item '{item_name}': {assigned_qty} assigned, {required_qty} required. Over-assigned by {assigned_qty - required_qty}.")

        if errors:
            raise serializers.ValidationError({"boxes": errors})

        data['invoice'] = invoice
        data['packing_session'] = packing_session
        data['invoice_items'] = invoice_items
        return data

    def create(self, validated_data):
        """
        On packing completion, create/update boxes and mark them as sealed (completed).
        """
        from django.utils import timezone
        invoice = validated_data['invoice']
        packing_session = validated_data['packing_session']
        boxes_data = validated_data['boxes']
        has_same_address_bills = validated_data.get('has_same_address_bills', False)

        # Mark packing session as packed
        packing_session.packing_status = 'PACKED'
        packing_session.end_time = timezone.now()
        packing_session.save()

        # Mark invoice as packed
        invoice.status = 'PACKED'
        invoice.save(update_fields=['status'])

        # Create/update boxes and mark as sealed
        for box_data in boxes_data:
            box_id = box_data['box_id']
            box, _ = Box.objects.get_or_create(box_id=box_id, invoice=invoice, packing_session=packing_session)
            box.is_sealed = True
            box.sealed_at = timezone.now()
            box.save()
            # Remove existing items and add new ones
            box.items.all().delete()
            for item in box_data['items']:
                BoxItem.objects.create(
                    box=box,
                    invoice_item_id=item['item_id'],
                    quantity=item['quantity']
                )

        # Set has_same_address_bills if needed
        packing_session.has_same_address_bills = has_same_address_bills
        packing_session.save()

        return {'success': True, 'invoice_no': invoice.invoice_no}



# --- These should be top-level classes ---
class BoxItemReadSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='invoice_item.name', read_only=True)
    item_code = serializers.CharField(source='invoice_item.item_code', read_only=True)
    invoice_item_id = serializers.IntegerField(source='invoice_item.id', read_only=True)  # ADD THIS

    class Meta:
        model = BoxItem
        fields = ['id', 'invoice_item_id', 'item_name', 'item_code', 'quantity']


class BoxReadSerializer(serializers.ModelSerializer):
    """Serializer for reading box details"""
    items = BoxItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Box
        fields = ['id', 'box_id', 'is_sealed', 'items', 'created_at', 'sealed_at', 'notes']


class CompletedPackingDataSerializer(serializers.Serializer):
    """Serializer for completed packing data (for label printing)"""
    invoice_no = serializers.CharField()
    customer_name = serializers.CharField()
    customer_phone = serializers.CharField(allow_blank=True, allow_null=True)
    delivery_address = serializers.CharField(allow_blank=True)
    related_bills = serializers.ListField(child=serializers.CharField())
    boxes = BoxReadSerializer(many=True)
