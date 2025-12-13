# apps/sales/serializers.py

from rest_framework import serializers
from .models import Invoice, InvoiceItem, Customer, Salesman,PickingSession,PackingSession
from django.utils import timezone


# ===== Serializers for list/detail views =====

class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice line items"""
    class Meta:
        model = InvoiceItem
        fields = ['id', 'name', 'item_code', 'quantity', 'mrp', 'shelf_location', 'remarks']


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


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer for invoice list and detail with nested data"""
    customer = CustomerReadSerializer(read_only=True)
    salesman = SalesmanReadSerializer(read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_no', 'invoice_date', 'customer', 'salesman', 
            'created_by', 'items', 'total_amount', 'remarks', 'created_at'
        ]
    
    def get_total_amount(self, obj):
        """Calculate total from items"""
        return sum(item.quantity * item.mrp for item in obj.items.all())


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


class InvoiceImportSerializer(serializers.Serializer):
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    salesman = serializers.CharField()
    created_by = serializers.CharField(required=False, allow_blank=True)
    customer = CustomerSerializer()
    items = ItemSerializer(many=True)

    def create(self, validated_data):
        customer_data = validated_data.pop("customer")
        items_data = validated_data.pop("items")
        salesman_name = validated_data.pop("salesman")

        salesman, _ = Salesman.objects.get_or_create(name=salesman_name)

        customer, _ = Customer.objects.update_or_create(
            code=customer_data["code"],
            defaults=customer_data
        )

        invoice = Invoice.objects.create(
            customer=customer,
            salesman=salesman,
            **validated_data
        )

        for item in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item)

        return invoice


#Picking
class PickingSessionCreateSerializer(serializers.ModelSerializer):
    invoice_no = serializers.CharField(write_only=True)

    class Meta :
        model =PickingSession
        fields =[
            'invoice_no',
            'notes'
        ]

    def validate_invoice_no(self,value):
        try :
            invoice = Invoice.objects.get(invoice_no=value)
        except Invoice.DoesNotExist:
            raise serializers.ValidationError("Invoice no found!")
        
        if invoice.status not in ['CREATED','IN_PROCESS']:
            raise serializers.ValidationError(
                f"Invoice cannot be picked in '{invoice.status}' state."
            )
        # Prevent duplicate picking session
        if hasattr(invoice, "pickingsession"):
            raise serializers.ValidationError(
                "Picking session already exists for this invoice."
            )

        return value
    
    def create(self, validated_data):
        invoice_no = validated_data.pop("invoice_no")
        invoice = Invoice.objects.get(invoice_no=invoice_no)

        user = self.context["request"].user

        picking_session = PickingSession.objects.create(
            invoice=invoice,
            picker=user,
            start_time=timezone.now(),
            picking_status="PREPARING",
            **validated_data
        )

        # Update invoice status
        invoice.status = "IN_PROCESS"
        invoice.save(update_fields=["status"])

        return picking_session


