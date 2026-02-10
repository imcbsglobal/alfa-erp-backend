from django.contrib import admin
from .models import Invoice, InvoiceItem, InvoiceReturn, Customer, Salesman, PickingSession, PackingSession, DeliverySession, Box, BoxItem


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
    list_display = ['invoice', 'packer', 'checking_by', 'packing_status', 'start_time', 'end_time']
    list_filter = ['packing_status', 'start_time']
    search_fields = ['invoice__invoice_no', 'packer__email', 'checking_by__email']
    raw_id_fields = ['invoice', 'packer', 'checking_by']


class BoxItemInline(admin.TabularInline):
    model = BoxItem
    extra = 0
    fields = ['invoice_item', 'quantity']
    raw_id_fields = ['invoice_item']


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['box_id', 'invoice', 'is_sealed', 'created_by', 'created_at', 'sealed_at']
    list_filter = ['is_sealed', 'created_at']
    search_fields = ['box_id', 'invoice__invoice_no']
    raw_id_fields = ['invoice', 'packing_session', 'created_by']
    inlines = [BoxItemInline]
    readonly_fields = ['created_at']


@admin.register(BoxItem)
class BoxItemAdmin(admin.ModelAdmin):
    list_display = ['box', 'invoice_item', 'quantity']
    search_fields = ['box__box_id', 'invoice_item__name']
    raw_id_fields = ['box', 'invoice_item']


@admin.register(DeliverySession)
class DeliverySessionAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'delivery_type', 'assigned_to', 'delivery_status', 'start_time', 'end_time']
    list_filter = ['delivery_type', 'delivery_status', 'start_time']
    search_fields = ['invoice__invoice_no', 'assigned_to__email', 'tracking_no']
    raw_id_fields = ['invoice', 'assigned_to']
