# apps/sales/admin_views.py
"""
Admin-specific views for privileged operations that bypass normal workflow restrictions
"""

import logging
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Invoice, PickingSession, PackingSession, DeliverySession
from apps.accounts.models import User

logger = logging.getLogger(__name__)


class IsAdminOrSuperadmin(IsAuthenticated):
    """Permission class for admin/superadmin only"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['ADMIN', 'SUPERADMIN']


class AdminCompleteWorkflowView(APIView):
    """
    POST /api/sales/admin/complete-workflow/
    Admin endpoint to force-complete the full workflow for stuck invoices
    Bypasses user email validation and session ownership checks
    
    Body: {
        "invoice_no": "INV-2026-TEST-0001",
        "reason": "Technical issue - customer urgent request",
        "admin_email": "admin@example.com"
    }
    """
    permission_classes = [IsAdminOrSuperadmin]
    
    @transaction.atomic
    def post(self, request):
        invoice_no = request.data.get('invoice_no')
        reason = request.data.get('reason', 'Admin forced completion')
        admin_email = request.data.get('admin_email') or request.user.email
        
        if not invoice_no:
            return Response({
                "success": False,
                "message": "invoice_no is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not reason or not reason.strip():
            return Response({
                "success": False,
                "message": "Reason is required for admin completion"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invoice = Invoice.objects.get(invoice_no=invoice_no)
        except Invoice.DoesNotExist:
            return Response({
                "success": False,
                "message": f"Invoice {invoice_no} not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            admin_user = User.objects.get(email=admin_email)
        except User.DoesNotExist:
            admin_user = request.user
        
        admin_note = f"[ADMIN OVERRIDE] {reason} - by {admin_user.name or admin_user.email}"
        
        steps_completed = []
        errors = []
        
        # Step 1: Complete Picking (if not already PICKED)
        if invoice.status in ['PENDING', 'PICKING', 'PREPARING']:
            try:
                picking_session, created = PickingSession.objects.get_or_create(
                    invoice=invoice,
                    defaults={
                        'picker': admin_user,
                        'start_time': timezone.now(),
                        'picking_status': 'PREPARING'
                    }
                )
                
                if picking_session.picking_status != 'PICKED':
                    picking_session.picker = admin_user
                    if not picking_session.start_time:
                        picking_session.start_time = timezone.now()
                    picking_session.end_time = timezone.now()
                    picking_session.picking_status = 'PICKED'
                    picking_session.notes = (picking_session.notes or '') + f"\n{admin_note}"
                    picking_session.save()
                    
                    invoice.status = 'PICKED'
                    invoice.save(update_fields=['status'])
                    steps_completed.append('picking')
                    logger.info(f"Admin completed picking for {invoice_no}")
                else:
                    steps_completed.append('picking (already completed)')
            except Exception as e:
                error_msg = f"Picking error: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Step 2: Complete Packing (if not already PACKED)
        if invoice.status in ['PICKED', 'PACKING', 'IN_PROGRESS']:
            try:
                packing_session, created = PackingSession.objects.get_or_create(
                    invoice=invoice,
                    defaults={
                        'packer': admin_user,
                        'start_time': timezone.now(),
                        'packing_status': 'IN_PROGRESS'
                    }
                )
                
                if packing_session.packing_status != 'PACKED':
                    packing_session.packer = admin_user
                    if not packing_session.start_time:
                        packing_session.start_time = timezone.now()
                    packing_session.end_time = timezone.now()
                    packing_session.packing_status = 'PACKED'
                    packing_session.notes = (packing_session.notes or '') + f"\n{admin_note}"
                    packing_session.save()
                    
                    invoice.status = 'PACKED'
                    invoice.save(update_fields=['status'])
                    steps_completed.append('packing')
                    logger.info(f"Admin completed packing for {invoice_no}")
                else:
                    steps_completed.append('packing (already completed)')
            except Exception as e:
                error_msg = f"Packing error: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Step 3: Complete Delivery (if not already DELIVERED)
        if invoice.status in ['PACKED', 'DISPATCHED', 'IN_TRANSIT']:
            try:
                delivery_session, created = DeliverySession.objects.get_or_create(
                    invoice=invoice,
                    defaults={
                        'assigned_to': admin_user,
                        'delivery_type': 'DIRECT',
                        'start_time': timezone.now(),
                        'delivery_status': 'IN_TRANSIT'
                    }
                )
                
                if delivery_session.delivery_status != 'DELIVERED':
                    delivery_session.assigned_to = admin_user
                    if not delivery_session.start_time:
                        delivery_session.start_time = timezone.now()
                    delivery_session.end_time = timezone.now()
                    delivery_session.delivery_status = 'DELIVERED'
                    delivery_session.notes = (delivery_session.notes or '') + f"\n{admin_note}"
                    delivery_session.save()
                    
                    invoice.status = 'DELIVERED'
                    invoice.save(update_fields=['status'])
                    steps_completed.append('delivery')
                    logger.info(f"Admin completed delivery for {invoice_no}")
                else:
                    steps_completed.append('delivery (already completed)')
            except Exception as e:
                error_msg = f"Delivery error: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        if not steps_completed:
            return Response({
                "success": False,
                "message": f"Invoice {invoice_no} is already in final status: {invoice.status}",
                "errors": errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True,
            "message": f"Workflow completed for {invoice_no}",
            "data": {
                "invoice_no": invoice_no,
                "final_status": invoice.status,
                "steps_completed": steps_completed,
                "errors": errors if errors else None,
                "admin_note": admin_note
            }
        }, status=status.HTTP_200_OK)
