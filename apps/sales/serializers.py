# apps/sales/serializers.py

from rest_framework import serializers
from .models import Invoice, InvoiceItem, Customer, Salesman

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["code", "name", "area", "address1", "address2", "phone1", "phone2", "email"]


class ItemSerializer(serializers.Serializer):
    item_name = serializers.CharField()
    item_code = serializers.CharField()
    quantity = serializers.IntegerField()
    mrp = serializers.FloatField()
    shelf_location = serializers.CharField(max_length=50, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)


class InvoiceImportSerializer(serializers.Serializer):
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    salesman = serializers.CharField()
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
