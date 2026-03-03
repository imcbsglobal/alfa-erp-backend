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

from .models import Invoice, PickingSession, PackingSession, DeliverySession, BulkStatusUpdateLog
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


class AdminBulkStatusUpdateView(APIView):
    """
    GET  /api/sales/admin/bulk-status-update/?from_status=INVOICED&from_date=2026-02-05&to_date=2026-02-06
         Preview invoices that match the filter (no DB changes).

    POST /api/sales/admin/bulk-status-update/
         Body: { "from_status": "INVOICED", "to_status": "PICKED",
                 "from_date": "2026-02-05", "to_date": "2026-02-06" }
         Bulk-moves invoice statuses and returns affected invoices with timestamp.

    Valid transitions: INVOICED→PICKED, PICKED→PACKED, PACKED→DELIVERED
    """

    VALID_TRANSITIONS = {
        "INVOICED": "PICKED",
        "PICKED": "PACKED",
        "PACKED": "DELIVERED",
    }

    permission_classes = [IsAdminOrSuperadmin]

    def _build_queryset(self, from_status, from_date, to_date):
        qs = Invoice.objects.filter(status=from_status)
        if from_date:
            qs = qs.filter(invoice_date__gte=from_date)
        if to_date:
            qs = qs.filter(invoice_date__lte=to_date)
        return qs

    def get(self, request):
        from_status = request.query_params.get("from_status", "").upper()
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        if from_status not in self.VALID_TRANSITIONS:
            return Response(
                {"success": False,
                 "message": f"Invalid from_status '{from_status}'. Must be one of: {', '.join(self.VALID_TRANSITIONS.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        to_status = self.VALID_TRANSITIONS[from_status]
        qs = self._build_queryset(from_status, from_date, to_date)
        invoices = list(
            qs.select_related("customer").values(
                "invoice_no", "invoice_date", "customer__name", "Total", "status"
            )
        )

        return Response({
            "success": True,
            "from_status": from_status,
            "to_status": to_status,
            "count": len(invoices),
            "invoices": [
                {
                    "invoice_no": inv["invoice_no"],
                    "invoice_date": str(inv["invoice_date"]),
                    "customer_name": inv["customer__name"],
                    "total": float(inv["Total"]),
                    "current_status": inv["status"],
                }
                for inv in invoices
            ],
        })

    @transaction.atomic
    def post(self, request):
        from_status = (request.data.get("from_status") or "").upper()
        to_status = (request.data.get("to_status") or "").upper()
        from_date = request.data.get("from_date")
        to_date = request.data.get("to_date")

        if from_status not in self.VALID_TRANSITIONS:
            return Response(
                {"success": False,
                 "message": f"Invalid from_status '{from_status}'. Must be one of: {', '.join(self.VALID_TRANSITIONS.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expected_to = self.VALID_TRANSITIONS[from_status]
        if to_status != expected_to:
            return Response(
                {"success": False,
                 "message": f"Invalid transition {from_status}→{to_status}. Expected target: {expected_to}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self._build_queryset(from_status, from_date, to_date)
        affected = list(
            qs.select_related("customer").values(
                "invoice_no", "invoice_date", "customer__name", "Total", "status"
            )
        )
        count = qs.count()
        update_time = timezone.now()

        qs.update(status=to_status)

        # Persist audit log to DB
        snapshot = [
            {
                "invoice_no": inv["invoice_no"],
                "invoice_date": str(inv["invoice_date"]),
                "customer_name": inv["customer__name"],
                "total": float(inv["Total"]),
                "new_status": to_status,
            }
            for inv in affected
        ]
        BulkStatusUpdateLog.objects.create(
            performed_by=request.user,
            from_status=from_status,
            to_status=to_status,
            from_date=from_date or None,
            to_date=to_date or None,
            count=count,
            invoices_snapshot=snapshot,
        )

        logger.info(
            f"Admin {request.user.email} bulk-updated {count} invoices "
            f"{from_status}→{to_status} (dates {from_date}–{to_date})"
        )

        return Response({
            "success": True,
            "message": f"Updated {count} invoice(s) from {from_status} to {to_status}.",
            "from_status": from_status,
            "to_status": to_status,
            "count": count,
            "updated_at": update_time.isoformat(),
            "invoices": [
                {
                    "invoice_no": inv["invoice_no"],
                    "invoice_date": str(inv["invoice_date"]),
                    "customer_name": inv["customer__name"],
                    "total": float(inv["Total"]),
                    "previous_status": inv["status"],
                    "new_status": to_status,
                }
                for inv in affected
            ],
        })


class AdminBulkStatusHistoryView(APIView):
    """
    GET /api/sales/admin/bulk-status-history/
    Returns the last 200 bulk-status-update audit log entries.
    Optional query params: ?limit=50
    """
    permission_classes = [IsAdminOrSuperadmin]

    def get(self, request):
        limit = min(int(request.query_params.get('limit', 200)), 500)
        logs = BulkStatusUpdateLog.objects.select_related('performed_by')[:limit]
        data = [
            {
                "id":          log.id,
                "from_status": log.from_status,
                "to_status":   log.to_status,
                "from_date":   str(log.from_date) if log.from_date else None,
                "to_date":     str(log.to_date)   if log.to_date   else None,
                "count":       log.count,
                "executed_at": log.executed_at.isoformat(),
                "performed_by": (
                    log.performed_by.name or log.performed_by.email
                    if log.performed_by else "Unknown"
                ),
                "invoices":    log.invoices_snapshot,
            }
            for log in logs
        ]
        return Response({"success": True, "results": data})
