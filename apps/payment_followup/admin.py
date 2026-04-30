from django.contrib import admin
from .models import FollowUp, PaymentAlert


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_code', 'client_name', 'outcome', 'outstanding_amount', 'created_at', 'created_by')
    list_filter = ('outcome', 'created_at', 'agent', 'area')
    search_fields = ('client_code', 'client_name', 'agent', 'area', 'notes')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_code', 'client_name', 'agent', 'area')
        }),
        ('Financial', {
            'fields': ('outstanding_amount',)
        }),
        ('Follow-up Details', {
            'fields': ('outcome', 'notes', 'next_followup_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PaymentAlert)
class PaymentAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_code', 'client_name', 'alert_type', 'severity', 'outstanding_amount', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_resolved', 'created_at')
    search_fields = ('client_code', 'client_name', 'agent', 'area')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'resolved_at')
    
    fieldsets = (
        ('Client Information', {
            'fields': ('client_code', 'client_name', 'agent', 'area')
        }),
        ('Financial', {
            'fields': ('outstanding_amount', 'oldest_due_days')
        }),
        ('Alert Details', {
            'fields': ('alert_type', 'severity')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

