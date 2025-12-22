from django.contrib import admin
from .models import Invoice, InvoiceItem, InvoiceReturn, Customer, Salesman, PickingSession, PackingSession, DeliverySession


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ['name', 'item_code', 'quantity', 'mrp', 'batch_no', 'expiry_date', 'shelf_location']


class InvoiceReturnInline(admin.StackedInline):
    model = InvoiceReturn
    extra = 0
    fields = ['return_reason', 'returned_by', 'returned_from_section', 'returned_at', 'resolution_notes', 'resolved_by', 'resolved_at']
    readonly_fields = ['returned_at']
    can_delete = False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_no', 'invoice_date', 'customer', 'status', 'priority', 'billing_status', 'created_at']
    list_filter = ['status', 'priority', 'billing_status', 'invoice_date']
    search_fields = ['invoice_no', 'customer__name', 'customer__code']
    inlines = [InvoiceItemInline, InvoiceReturnInline]
    readonly_fields = ['created_at']


@admin.register(InvoiceReturn)
class InvoiceReturnAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'returned_from_section', 'returned_by', 'returned_at', 'resolved_at']
    list_filter = ['returned_from_section', 'returned_at', 'resolved_at']
    search_fields = ['invoice__invoice_no', 'return_reason', 'resolution_notes']
    readonly_fields = ['returned_at']
    raw_id_fields = ['invoice', 'returned_by', 'resolved_by']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'area', 'phone1', 'email']
    search_fields = ['code', 'name', 'area', 'email']


@admin.register(Salesman)
class SalesmanAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    search_fields = ['name']


@admin.register(PickingSession)
class PickingSessionAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'picker', 'picking_status', 'start_time', 'end_time']
    list_filter = ['picking_status', 'start_time']
    search_fields = ['invoice__invoice_no', 'picker__email']
    raw_id_fields = ['invoice', 'picker']


@admin.register(PackingSession)
class PackingSessionAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'packer', 'packing_status', 'start_time', 'end_time']
    list_filter = ['packing_status', 'start_time']
    search_fields = ['invoice__invoice_no', 'packer__email']
    raw_id_fields = ['invoice', 'packer']


@admin.register(DeliverySession)
class DeliverySessionAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'delivery_type', 'assigned_to', 'delivery_status', 'start_time', 'end_time']
    list_filter = ['delivery_type', 'delivery_status', 'start_time']
    search_fields = ['invoice__invoice_no', 'assigned_to__email', 'tracking_no']
    raw_id_fields = ['invoice', 'assigned_to']
