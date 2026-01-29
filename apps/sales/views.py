# apps/sales/views.py

import time
import json
import logging
from django.db import IntegrityError, transaction
from django.utils import timezone

from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import django_eventstream

from .serializers import (
    InvoiceImportSerializer, 
    InvoiceListSerializer,
    PickingSessionCreateSerializer,
    PickingSessionReadSerializer,
    CompletePickingSerializer,
    PackingSessionCreateSerializer,
    PackingSessionReadSerializer,
    CompletePackingSerializer,
    DeliverySessionCreateSerializer,
    DeliverySessionReadSerializer,
    CompleteDeliverySerializer,
)
from .update_serializers import InvoiceUpdateSerializer
from .events import INVOICE_CHANNEL
from .models import Invoice, PickingSession, PackingSession, DeliverySession
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated


logger = logging.getLogger(__name__)


# ===== Pagination =====
class InvoiceListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== List Invoices API =====
class InvoiceListView(generics.ListAPIView):
    """
    GET /api/sales/invoices/
    List all invoices with pagination, includes customer, salesman, items
    
    Query Parameters:
    - status: Filter by invoice status (INVOICED, PICKING, PICKED, PACKING, PACKED, DISPATCHED, DELIVERED, REVIEW)
    - user: Filter by created_user ID (invoices created by specific user)
    - created_by: Filter by created_by string field (username/identifier)
    - worker: Filter by worker email (picker/packer/delivery person who worked on the invoice)
    
    Examples:
    - /api/sales/invoices/?status=INVOICED
    - /api/sales/invoices/?status=PICKING&status=PACKING (multiple values)
    - /api/sales/invoices/?user=5
    - /api/sales/invoices/?created_by=admin
    - /api/sales/invoices/?worker=zain@gmail.com (invoices worked on by this user)
    - /api/sales/invoices/?status=PICKED&worker=zain@gmail.com (invoices picked by this user)
    """
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = InvoiceListPagination
    
    def get_queryset(self):
        # ✅ PERFORMANCE FIX: Prefetch all related session data to avoid N+1 queries
        # Use prefetch_related for OneToOne fields that might not exist
        queryset = Invoice.objects.select_related(
            'customer', 
            'salesman', 
            'created_user'
        ).prefetch_related(
            'items',
            'pickingsession',
            'pickingsession__picker',
            'packingsession',
            'packingsession__packer',
            'deliverysession',
            'deliverysession__assigned_to',
            'deliverysession__delivered_by',
            'invoice_returns',
            'invoice_returns__returned_by',
            'invoice_returns__resolved_by'
        ).order_by('created_at')
        
        # Filter by status (supports multiple values: ?status=PENDING&status=PICKING)
        status_list = self.request.query_params.getlist('status')
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        
        # Filter by priority (e.g., ?priority=HIGH)
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by created_user ID
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(created_user_id=user_id)
        
        # Filter by created_by string field
        created_by = self.request.query_params.get('created_by')
        if created_by:
            queryset = queryset.filter(created_by__icontains=created_by)
        
        # Filter by worker email (picker/packer/delivery person)
        worker_email = self.request.query_params.get('worker')
        if worker_email:
            from django.db.models import Q
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Find user by email
            worker = User.objects.filter(email=worker_email).first()
            if worker:
                # Filter invoices where this user is picker, packer, or delivery person
                queryset = queryset.filter(
                    Q(pickingsession__picker=worker) |
                    Q(packingsession__packer=worker) |
                    Q(deliverysession__delivery_user=worker)
                ).distinct()
        
        return queryset


# ===== Retrieve Invoice API =====
class InvoiceDetailView(generics.RetrieveAPIView):
    """
    GET /api/sales/invoices/{id}/
    Retrieve a single invoice by primary key with nested customer, salesman and items.
    """
    queryset = Invoice.objects.select_related('customer', 'salesman', 'created_user').prefetch_related('items')
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# ===== My Active Picking Task API =====
class MyActivePickingView(APIView):
    """
    GET /api/sales/picking/active/
    Returns the current active picking task for the authenticated user.
    Since a user can only work on one task at a time, this returns their current picking invoice (if any).
    
    Authentication: Required (Bearer token)
    
    Query Parameters:
    - user: User ID (UUID) or email to check (admin/staff only)
    - user_email: Alias for user parameter
    
    Response:
    - If user has an active picking task: Returns invoice details with session info
    - If no active task: Returns {"success": true, "message": "No active picking task", "data": null}
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        target_user = request.user
        user_param = request.query_params.get('user')
        user_email_param = request.query_params.get('user_email')

        requested = None
        if user_email_param:
            requested = User.objects.filter(email=user_email_param).first()
        elif user_param:
            if '@' in user_param:
                requested = User.objects.filter(email=user_param).first()
            else:
                requested = User.objects.filter(id=user_param).first()

        if requested and requested != request.user:
            if not (request.user and request.user.is_authenticated and request.user.is_admin_or_superadmin()):
                return Response({
                    "success": False,
                    "message": "Permission denied to view other user's task."
                }, status=status.HTTP_403_FORBIDDEN)
            target_user = requested

        # Check for active picking session (PREPARING or REVIEW)
        picking_session = PickingSession.objects.filter(
            picker=target_user,
            picking_status__in=['PREPARING', 'REVIEW']
        ).select_related('invoice__customer', 'invoice__salesman').prefetch_related('invoice__items').first()

        if picking_session:
            invoice_data = InvoiceListSerializer(picking_session.invoice).data
            return Response({
                "success": True,
                "message": f"Active picking task found for {target_user.email}",
                "data": {
                    "task_type": "PICKING",
                    "session_id": picking_session.id,
                    "start_time": picking_session.start_time,
                    "invoice": invoice_data
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "success": True,
            "message": "No active picking task",
            "data": None
        }, status=status.HTTP_200_OK)


# ===== My Active Packing Task API =====
class MyActivePackingView(APIView):
    """
    GET /api/sales/packing/active/
    Returns the current active packing task for the authenticated user.
    Since a user can only work on one task at a time, this returns their current packing invoice (if any).
    
    Authentication: Required (Bearer token)
    
    Query Parameters:
    - user: User ID (UUID) or email to check (admin/staff only)
    - user_email: Alias for user parameter
    
    Response:
    - If user has an active packing task: Returns invoice details with session info
    - If no active task: Returns {"success": true, "message": "No active packing task", "data": null}
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        target_user = request.user
        user_param = request.query_params.get('user')
        user_email_param = request.query_params.get('user_email')

        requested = None
        if user_email_param:
            requested = User.objects.filter(email=user_email_param).first()
        elif user_param:
            if '@' in user_param:
                requested = User.objects.filter(email=user_param).first()
            else:
                requested = User.objects.filter(id=user_param).first()

        if requested and requested != request.user:
            if not (request.user and request.user.is_authenticated and request.user.is_admin_or_superadmin()):
                return Response({
                    "success": False,
                    "message": "Permission denied to view other user's task."
                }, status=status.HTTP_403_FORBIDDEN)
            target_user = requested

        # Check for active packing session (IN_PROGRESS or REVIEW)
        packing_session = PackingSession.objects.filter(
            packer=target_user,
            packing_status__in=['IN_PROGRESS', 'REVIEW']
        ).select_related('invoice__customer', 'invoice__salesman').prefetch_related('invoice__items').first()

        if packing_session:
            invoice_data = InvoiceListSerializer(packing_session.invoice).data
            return Response({
                "success": True,
                "message": f"Active packing task found for {target_user.email}",
                "data": {
                    "task_type": "PACKING",
                    "session_id": packing_session.id,
                    "start_time": packing_session.start_time,
                    "invoice": invoice_data
                }
            }, status=status.HTTP_200_OK)

        return Response({
            "success": True,
            "message": "No active packing task",
            "data": None
        }, status=status.HTTP_200_OK)

# -----------------------------------
# DRF API View: Import Invoice
# -----------------------------------
class HasAPIKeyOrAuthenticated(BasePermission):
    """Permission that allows access if the request has a valid API key OR the user is authenticated via regular auth."""
    def has_permission(self, request, view):
        # If user is authenticated, allow
        if getattr(request, 'user', None) and request.user.is_authenticated:
            return True
        # Otherwise, check X-API-KEY header
        api_key = request.headers.get('X-API-KEY') or request.META.get('HTTP_X_API_KEY')
        expected = getattr(settings, 'SALES_IMPORT_API_KEY', 'WEDFBNPOIUFSDFTY')
        return api_key == expected


class ImportInvoiceView(APIView):
    """
    API endpoint to import a new invoice.
    After saving, it pushes an event to the SSE queue for live updates.
    """
    permission_classes = [HasAPIKeyOrAuthenticated]
    def post(self, request):
        serializer = InvoiceImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice_no = serializer.validated_data.get("invoice_no")

        # If invoice exists, update it (replace items, update customer/salesman/fields)
        existing = Invoice.objects.filter(invoice_no=invoice_no).first()
        if existing:
            return Response({
                "success": False,
                "message": "Invoice with this invoice_no already exists. Import endpoint does not update existing invoices.",
                "data": {"id": existing.id, "invoice_no": existing.invoice_no}
            }, status=status.HTTP_409_CONFLICT)

        try:
            invoice = serializer.save()
        except IntegrityError:
            # Race condition: another request created the invoice concurrently
            existing = Invoice.objects.filter(invoice_no=invoice_no).first()
            if existing:
                return Response(
                    {
                        "success": False,
                        "message": "Invoice with this invoice_no already exists (race).",
                        "data": {"id": existing.id, "invoice_no": existing.invoice_no},
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            # unexpected DB error — re-raise or return generic 500
            logger.exception("IntegrityError on invoice save (unexpected)")
            return Response(
                {"success": False, "message": "Failed to save invoice due to DB error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Set created_user to the authenticated user
        if request.user and request.user.is_authenticated:
            invoice.created_user = request.user
            invoice.save()

        total_amount = sum(item.quantity * item.mrp for item in invoice.items.all())

        # Push full invoice payload to SSE using django-eventstream
        try:
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            serializer = InvoiceListSerializer(invoice_refreshed)
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                serializer.data
            )
            logger.debug("Invoice event sent: %s", invoice.invoice_no)
        except Exception:
            logger.exception("Failed to send invoice event")

        return Response(
            {
                "success": True,
                "message": "Invoice imported successfully",
                "data": {
                    "id": invoice.id,
                    "invoice_no": invoice.invoice_no,
                    "total_amount": total_amount,
                    "priority": invoice.priority,
                    "status": invoice.status,
                    "billing_status": invoice.billing_status,
                    "created_at": invoice.created_at
                }
            },
            status=status.HTTP_201_CREATED
        )

# SSE endpoint is now handled by django-eventstream
# See urls.py for the eventstream path configuration


# ===== Update Invoice (After Review) =====

class UpdateInvoiceView(APIView):
    """
    PATCH /api/sales/update/invoice/
    
    Update an invoice that was sent for review. This endpoint allows correcting
    invoice data (items, batch numbers, dates, MRP, etc.) after issues were found
    during picking/packing/delivery.
    
    Authentication: API Key (X-API-KEY) or Bearer Token
    
    Request Body:
    {
        "invoice_no": "INV-001",
        "invoice_date": "2025-12-23",  // optional
        "priority": "HIGH",  // optional
        "items": [
            {
                "barcode": "BC-MED001",  // preferred - used to match existing items; item_code used as fallback
                "item_code": "MED001",   // optional fallback
                "quantity": 50,
                "mrp": 145.50,
                "batch_no": "BATCH456",
                "expiry_date": "2026-06-30"
            }
        ],
        "replace_items": false,  // if true, deletes items not in list
        "resolution_notes": "Fixed batch number and updated MRP"
    }
    
    Only invoices in REVIEW status can be updated.
    After update, invoice status returns to the section it was returned from.
    """
    permission_classes = [HasAPIKeyOrAuthenticated]
    
    def patch(self, request):
        serializer = InvoiceUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Perform the update
            invoice = serializer.update(None, serializer.validated_data)
        except Exception as e:
            logger.exception("Failed to update invoice")
            return Response({
                "success": False,
                "message": f"Failed to update invoice: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Calculate new total
        total_amount = sum(item.quantity * item.mrp for item in invoice.items.all())
        
        # Send SSE event with updated invoice
        try:
            invoice_refreshed = Invoice.objects.select_related(
                'customer', 'salesman'
            ).prefetch_related('items', 'invoice_returns', 'invoice_returns__returned_by').get(id=invoice.id)
            
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
            
            # Also send update notification
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                {
                    'type': 'invoice_updated',
                    'invoice_no': invoice.invoice_no,
                    'status': invoice.status,
                    'billing_status': invoice.billing_status,
                    'timestamp': timezone.now().isoformat()
                }
            )
            logger.debug("Invoice update event sent: %s", invoice.invoice_no)
        except Exception:
            logger.exception("Failed to send invoice update event")
        
        return Response({
            "success": True,
            "message": f"Invoice {invoice.invoice_no} updated successfully",
            "data": {
                "invoice": invoice_data,
                "summary": {
                    "id": invoice.id,
                    "invoice_no": invoice.invoice_no,
                    "status": invoice.status,
                    "billing_status": invoice.billing_status,
                    "total_amount": total_amount,
                    "items_count": invoice.items.count(),
                    "returned_from_section": invoice.invoice_returns.order_by('-returned_at').first().returned_from_section if invoice.invoice_returns.exists() else None,
                    "resolution_notes": invoice.invoice_returns.order_by('-returned_at').first().resolution_notes if invoice.invoice_returns.exists() else None
                }
            }
        }, status=status.HTTP_200_OK)


# ===== PICKING WORKFLOW =====

class StartPickingView(APIView):
    """
    POST /api/sales/picking/start/
    Start picking session - User scans their email to begin picking
    Body: {
        "invoice_no": "INV-001",
        "user_email": "john.doe@company.com",
        "notes": "Starting picking"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PickingSessionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Privilege Not Given",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if this user already has any active picking session
        user_email = request.data.get('user_email')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(email=user_email).first()
        
        if user:
            existing_session = PickingSession.objects.filter(
                picker=user,
                picking_status__in=['PREPARING', 'REVIEW']
            ).select_related('invoice').first()
            
            if existing_session:
                return Response({
                    "success": False,
                    "message": f"You already have an active picking session for {existing_session.invoice.invoice_no}",
                    "data": {
                        "invoice_no": existing_session.invoice.invoice_no,
                        "started_at": existing_session.start_time
                    }
                }, status=status.HTTP_409_CONFLICT)
        
        picking_session = serializer.save()

                # Update invoice status
        invoice = picking_session.invoice
        invoice.status = "PICKING"
        invoice.save(update_fields=['status'])

        # Emit SSE event for invoice status change
        try:
            invoice = picking_session.invoice
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit picking start event")
        
        response_serializer = PickingSessionReadSerializer(picking_session)
        return Response({
            "success": True,
            "message": f"Picking started by {request.user.name}",
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)


class CompletePickingView(APIView):
    """
    POST /api/sales/picking/complete/
    Complete picking - User scans their email to confirm completion
    Body: {
        "invoice_no": "INV-001",
        "user_email": "john.doe@company.com",
        "notes": "Picking completed",
        "is_repick": false  // Set to true for re-invoiced bills
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CompletePickingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        picking_session = validated_data['picking_session']
        invoice = validated_data['invoice']
        notes = validated_data.get('notes', '')
        is_repick = validated_data.get('is_repick', False)
        
        # Update picking session
        picking_session.end_time = timezone.now()
        picking_session.picking_status = "PICKED"
        if notes:
            picking_session.notes = (picking_session.notes or '') + f"\n{notes}"
        picking_session.save()
        
        # Update invoice status
        invoice.status = "PICKED"
        
        # Update billing status if this was a re-pick
        if is_repick and invoice.billing_status == 'RE_INVOICED':
            invoice.billing_status = 'BILLED'
            
            # Update the InvoiceReturn record
            if hasattr(invoice, 'invoice_return'):
                invoice_return = invoice.invoice_return
                invoice_return.resolved_at = timezone.now()
                invoice_return.resolved_by = request.user
                invoice_return.save()
        
        invoice.save(update_fields=['status', 'billing_status'])
        
        
        # Emit SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit picking complete event")
        
        response_serializer = PickingSessionReadSerializer(picking_session)
        return Response({
            "success": True,
            "message": f"Picking completed for {invoice.invoice_no}" + (" (Re-pick completed)" if is_repick else ""),
            "data": response_serializer.data
        }, status=status.HTTP_200_OK)


# ===== PACKING WORKFLOW =====

class StartPackingView(APIView):
    """
    POST /api/sales/packing/start/
    Start packing session - User scans their email to begin packing
    Body: {
        "invoice_no": "INV-001",
        "user_email": "jane.smith@company.com",
        "notes": "Starting packing"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PackingSessionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        invoice = validated_data['invoice']
        user = validated_data['user']
        notes = validated_data.get('notes', '')
        
        # Check if this user already has any active packing session
        existing_session = PackingSession.objects.filter(
            packer=user,
            packing_status__in=['IN_PROGRESS', 'REVIEW']
        ).select_related('invoice').first()
        
        if existing_session:
            return Response({
                "success": False,
                "message": f"You already have an active packing session for {existing_session.invoice.invoice_no}",
                "data": {
                    "invoice_no": existing_session.invoice.invoice_no,
                    "started_at": existing_session.start_time
                }
            }, status=status.HTTP_409_CONFLICT)
        
        # Create packing session
        packing_session = PackingSession.objects.create(
            invoice=invoice,
            packer=user,
            start_time=timezone.now(),
            packing_status="IN_PROGRESS",
            notes=notes,
            selected_items=[]
        )
        
        # Update invoice status
        invoice.status = "PACKING"
        invoice.save(update_fields=['status'])
        
        # Emit SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit packing start event")
        
        response_serializer = PackingSessionReadSerializer(packing_session)
        return Response({
            "success": True,
            "message": f"Packing started by {user.name}",
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)

class CompletePackingView(APIView):
    """
    POST /api/sales/packing/complete/
    Complete packing - User scans their email to confirm completion
    Body: {
        "invoice_no": "INV-001",
        "user_email": "jane.smith@company.com",
        "notes": "Packing completed"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CompletePackingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        packing_session = validated_data['packing_session']
        invoice = validated_data['invoice']
        notes = validated_data.get('notes', '')
        
        # Update packing session
        packing_session.end_time = timezone.now()
        packing_session.packing_status = "PACKED"
        if notes:
            packing_session.notes = (packing_session.notes or '') + f"\n{notes}"
        packing_session.save()
        
        # Update invoice status
        invoice.status = "PACKED"
        invoice.save(update_fields=['status'])
        
        # Emit SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit packing complete event")
        
        response_serializer = PackingSessionReadSerializer(packing_session)
        return Response({
            "success": True,
            "message": f"Packing completed for {invoice.invoice_no}",
            "data": response_serializer.data
        }, status=status.HTTP_200_OK)


# ===== DELIVERY WORKFLOW =====

# Update this view in views.py

# Add these views to your views.py

class StartDeliveryView(APIView):
    """
    POST /api/sales/delivery/start/
    Start delivery session
    
    For Counter Pickup (DIRECT) - Completes immediately:
    {
        "invoice_no": "INV-001",
        "delivery_type": "DIRECT",
        "counter_sub_mode": "patient" or "company",
        "pickup_person_username": "scan_or_entered_username",
        "pickup_person_name": "John Doe",
        "pickup_person_phone": "1234567890",
        "pickup_company_name": "ABC Corp",  // only for company mode
        "pickup_company_id": "COMP123",     // only for company mode
        "notes": "Optional notes"
    }
    
    For Courier (COURIER) - Moves to consider list:
    {
        "invoice_no": "INV-001",
        "delivery_type": "COURIER",
        "courier_id": "uuid-of-courier",
        "notes": "Optional notes"
    }
    
    For Internal Delivery (INTERNAL) - Moves to consider list:
    {
        "invoice_no": "INV-001",
        "delivery_type": "INTERNAL",
        "user_email": "staff@example.com",
        "user_name": "Staff Name (optional)",
        "notes": "Optional notes"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = DeliverySessionCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        invoice = validated_data['invoice']
        delivery_type = validated_data['delivery_type']
        
        # Prepare delivery session data
        delivery_data = {
            'invoice': invoice,
            'delivery_type': delivery_type,
            'notes': validated_data.get('notes', ''),
            'assigned_to': request.user,  # Person who initiated delivery
        }
        
        # For Counter Pickup (DIRECT) - Complete immediately
        if delivery_type == 'DIRECT':
            delivery_data.update({
                'counter_sub_mode': validated_data.get('counter_sub_mode'),
                'pickup_person_username': validated_data.get('pickup_person_username'),
                'pickup_person_name': validated_data.get('pickup_person_name'),
                'pickup_person_phone': validated_data.get('pickup_person_phone'),
                'pickup_company_name': validated_data.get('pickup_company_name', ''),
                'pickup_company_id': validated_data.get('pickup_company_id', ''),
                'start_time': timezone.now(),
                'end_time': timezone.now(),  # Counter pickup completes immediately
                'delivery_status': 'DELIVERED',  # Mark as delivered immediately
                'delivered_by': request.user,  # Same person who processed it
            })
            
            # Update invoice status to DELIVERED for counter pickup
            invoice.status = "DELIVERED"
            message = f"Counter pickup completed - {validated_data.get('counter_sub_mode')}"
            
        # For Courier Delivery - Assign courier and move to consider list
        elif delivery_type == 'COURIER':
            from apps.accounts.models import Courier
            
            courier_id = validated_data.get('courier_id')
            if not courier_id:
                return Response({
                    "success": False,
                    "message": "Courier ID is required for courier delivery"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                courier = Courier.objects.get(courier_id=courier_id)
            except Courier.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Invalid courier ID"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            delivery_data.update({
                'courier': courier,
                'courier_name': courier.courier_name,
                'start_time': timezone.now(),
                'delivery_status': 'TO_CONSIDER',
            })
            
            invoice.status = "PACKED"
            message = f"Invoice assigned to {courier.courier_name}. Moved to Courier Delivery list."
            
        # For Internal Delivery - Assign user and move to consider list
        elif delivery_type == 'INTERNAL':
            from apps.accounts.models import User
            
            user_email = validated_data.get('user_email')
            if not user_email:
                return Response({
                    "success": False,
                    "message": "User email is required for internal delivery"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                assigned_user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "User not found with provided email"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            delivery_data['assigned_to'] = assigned_user
            delivery_data.update({
                'start_time': timezone.now(),
                'delivery_status': 'TO_CONSIDER',
            })
            
            invoice.status = "PACKED"
            message = f"Invoice assigned to {assigned_user.get_full_name() or assigned_user.email}. Moved to Company Delivery list."
        
        # Create delivery session
        delivery_session = DeliverySession.objects.create(**delivery_data)
        
        # Save invoice status
        invoice.save(update_fields=['status'])
        
        # Emit SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related(
                'customer', 'salesman'
            ).prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit delivery start event")
        
        response_serializer = DeliverySessionReadSerializer(delivery_session)
        
        return Response({
            "success": True,
            "message": message,
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)


class DeliveryConsiderListView(generics.ListAPIView):
    """
    GET /api/sales/delivery/consider-list/
    
    List invoices in the delivery consider list (waiting for staff assignment)
    
    Query Parameters:
    - delivery_type: Filter by delivery type (COURIER, INTERNAL)
    - search: Search by invoice number or customer name
    - page: Page number
    - page_size: Items per page
    """
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InvoiceListPagination
    
    def get_queryset(self):
        # Get invoices that have delivery sessions with TO_CONSIDER status
        # ✅ PERFORMANCE FIX: Prefetch all related data
        queryset = Invoice.objects.filter(
            deliverysession__delivery_status='TO_CONSIDER'
        ).select_related(
            'customer', 
            'salesman', 
            'created_user',
            'deliverysession',
            'pickingsession',
            'packingsession'
        ).prefetch_related(
            'items',
            'pickingsession__picker',
            'packingsession__packer',
            'deliverysession__assigned_to',
            'deliverysession__delivered_by',
            'invoice_returns'
        ).order_by('deliverysession__created_at')
        
        # Filter by delivery type
        delivery_type = self.request.query_params.get('delivery_type', '').upper()
        if delivery_type and delivery_type in ['COURIER', 'INTERNAL']:
            queryset = queryset.filter(deliverysession__delivery_type=delivery_type)
        
        # Search filter
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(invoice_no__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__phone1__icontains=search) |
                Q(deliverysession__assigned_to__email__icontains=search) |
                Q(deliverysession__assigned_to__name__icontains=search)
            )
        
        return queryset


from apps.accounts.models import Courier
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

# In views.py - Update AssignDeliveryStaffView

class AssignDeliveryStaffView(APIView):
    """
    POST /api/sales/delivery/assign/
    
    Assign a staff member or courier to handle a delivery
    
    Body:
    {
        "invoice_no": "INV-001",
        "user_email": "staff@company.com",  # For INTERNAL
        "courier_id": "courier_uuid",        # For COURIER
        "delivery_type": "INTERNAL" or "COURIER"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        invoice_no = request.data.get('invoice_no')
        user_email = request.data.get('user_email')
        courier_id = request.data.get('courier_id')
        delivery_type = request.data.get('delivery_type', 'INTERNAL')
        
        # Validation
        if not invoice_no:
            return Response({
                "success": False,
                "message": "invoice_no is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get invoice
        try:
            invoice = Invoice.objects.get(invoice_no=invoice_no)
        except Invoice.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invoice not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get delivery session
        try:
            delivery = DeliverySession.objects.get(invoice=invoice)
        except DeliverySession.DoesNotExist:
            return Response({
                "success": False,
                "message": "Delivery session not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validate delivery type matches
        if delivery.delivery_type != delivery_type:
            return Response({
                "success": False,
                "message": f"Delivery type mismatch. Expected {delivery.delivery_type}, got {delivery_type}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if delivery is in TO_CONSIDER status
        if delivery.delivery_status != 'TO_CONSIDER':
            return Response({
                "success": False,
                "message": f"Delivery is not in consider list. Current status: {delivery.delivery_status}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # HANDLE INTERNAL (COMPANY DELIVERY)
        if delivery.delivery_type == 'INTERNAL':
            if not user_email:
                return Response({
                    "success": False,
                    "message": "user_email is required for company delivery"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                assigned_user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "User not found with this email"
                }, status=status.HTTP_404_NOT_FOUND)
            
            delivery.assigned_to = assigned_user
            delivery.delivery_status = 'IN_TRANSIT'
            delivery.start_time = timezone.now()
            delivery.save()
            
            invoice.status = 'DISPATCHED'
            invoice.save(update_fields=['status'])
            
            message = f"Company delivery assigned to {assigned_user.name}. Delivery moved to their active tasks."
        
        # HANDLE COURIER
        elif delivery.delivery_type == 'COURIER':
            if not courier_id:
                return Response({
                    "success": False,
                    "message": "courier_id is required for courier delivery"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                courier = Courier.objects.get(courier_id=courier_id)
            except Courier.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Courier not found"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Record courier assignment, keep in TO_CONSIDER
            delivery.courier_name = courier.courier_name
            delivery.assigned_to = request.user
            # Keep status as TO_CONSIDER - waiting for slip upload
            delivery.save()
            
            message = f"Courier '{courier.courier_name}' assigned. Please upload courier slip to complete delivery."
        
        else:
            return Response({
                "success": False,
                "message": f"Invalid delivery type: {delivery.delivery_type}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related(
                'customer', 'salesman'
            ).prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit delivery assignment event")
        
        return Response({
            "success": True,
            "message": message,
            "data": {
                "invoice_no": invoice.invoice_no,
                "delivery_status": delivery.delivery_status,
                "delivery_type": delivery.delivery_type,
                "invoice_status": invoice.status,
                "courier_name": delivery.courier_name if delivery.delivery_type == 'COURIER' else None
            }
        }, status=status.HTTP_200_OK)

class UploadCourierSlipView(APIView):
    """
    POST /api/sales/delivery/upload-slip/
    
    Upload courier slip and COMPLETE courier delivery
    This moves the delivery directly to DELIVERED status and history
    
    Body (FormData):
    - invoice_no: Invoice number
    - courier_slip: File (image or PDF)
    - tracking_no: Tracking number (optional)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        invoice_no = request.data.get("invoice_no")
        slip = request.FILES.get("courier_slip")
        tracking_no = request.data.get("tracking_no", "")

        if not invoice_no or not slip:
            return Response({
                "success": False,
                "message": "invoice_no and courier_slip are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            invoice = Invoice.objects.get(invoice_no=invoice_no)
        except Invoice.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invoice not found"
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            delivery = DeliverySession.objects.get(invoice=invoice)
        except DeliverySession.DoesNotExist:
            return Response({
                "success": False,
                "message": "Delivery session not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # ✅ Validate this is a COURIER delivery
        if delivery.delivery_type != 'COURIER':
            return Response({
                "success": False,
                "message": "This endpoint is only for courier deliveries"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Check if courier was assigned
        if not delivery.courier_name:
            return Response({
                "success": False,
                "message": "Please assign a courier first before uploading slip"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Complete the courier delivery
        delivery.courier_slip = slip
        if tracking_no:
            delivery.tracking_no = tracking_no
        
        # ✅ Mark as DELIVERED - goes directly to history
        delivery.delivery_status = "DELIVERED"
        delivery.start_time = delivery.start_time or timezone.now()
        delivery.end_time = timezone.now()
        delivery.delivered_by = request.user
        delivery.save()

        # ✅ Update invoice to DELIVERED
        invoice.status = "DELIVERED"
        invoice.save(update_fields=["status"])

        # Send SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related(
                'customer', 'salesman'
            ).prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit courier delivery complete event")

        return Response({
            "success": True,
            "message": "Courier slip uploaded. Delivery completed and moved to history.",
            "data": {
                "invoice_no": invoice.invoice_no,
                "invoice_status": invoice.status,
                "delivery_status": delivery.delivery_status,
                "courier_name": delivery.courier_name,
                "tracking_no": delivery.tracking_no
            }
        }, status=status.HTTP_200_OK)
        
class CompleteDeliveryView(APIView):
    """
    POST /api/sales/delivery/complete/
    Complete delivery - User scans their email to confirm delivery
    Body: {
        "invoice_no": "INV-001",
        "user_email": "driver@company.com",  # Optional for COURIER
        "delivery_status": "DELIVERED",  # DELIVERED or IN_TRANSIT
        "courier_name": "DHL",  # Required for COURIER type
        "tracking_no": "ABC123",  # Optional for COURIER type
        "notes": "Delivered to customer"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CompleteDeliverySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        delivery_session = validated_data['delivery_session']
        invoice = validated_data['invoice']
        delivery_status = validated_data.get('delivery_status', 'DELIVERED')
        notes = validated_data.get('notes', '')
        
        # Update courier information if provided (for COURIER deliveries)
        if delivery_session.delivery_type == 'COURIER':
            courier_name = validated_data.get('courier_name', '').strip()
            tracking_no = validated_data.get('tracking_no', '').strip()
            
            if courier_name:
                delivery_session.courier_name = courier_name
            if tracking_no:
                delivery_session.tracking_no = tracking_no
                
        if delivery_session.delivery_type == 'INTERNAL':
            delivery_session.delivery_latitude = validated_data.get('delivery_latitude')
            delivery_session.delivery_longitude = validated_data.get('delivery_longitude')
            delivery_session.delivery_location_address = validated_data.get('delivery_location_address', '')
            delivery_session.delivery_location_accuracy = validated_data.get('delivery_location_accuracy')
        # Set delivered_by to the user who completed delivery
        delivery_session.delivered_by = request.user
        delivery_session.end_time = timezone.now()
        delivery_session.delivery_status = delivery_status
        
        if notes:
            delivery_session.notes = (delivery_session.notes or '') + f"\n{notes}"
        
        delivery_session.save()
        
        # Update invoice status
        invoice.status = "DELIVERED" if delivery_status == "DELIVERED" else "DISPATCHED"
        invoice.save(update_fields=['status'])
        
        # Emit SSE event
        try:
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
        except Exception:
            logger.exception("Failed to emit delivery complete event")
        
        response_serializer = DeliverySessionReadSerializer(delivery_session)
        return Response({
            "success": True,
            "message": f"Delivery {delivery_status.lower()} for {invoice.invoice_no}",
            "data": response_serializer.data
        }, status=status.HTTP_200_OK)

class CancelSessionView(APIView):
    """
    POST /api/sales/cancel-session/
    Cancel a session and DELETE it so invoice can be picked up by anyone
    
    Body:
    {
        "invoice_no": "INV-001",
        "user_email": "user@example.com",
        "session_type": "PICKING" or "PACKING" or "DELIVERY",
        "cancel_reason": "Optional reason for cancellation"
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        invoice_no = request.data.get('invoice_no')
        user_email = request.data.get('user_email')
        session_type = request.data.get('session_type')
        cancel_reason = request.data.get('cancel_reason', '')
        
        # Validate inputs
        if not invoice_no or not session_type:
            return Response({
                "success": False,
                "message": "invoice_no and session_type are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get invoice
        try:
            invoice = Invoice.objects.get(invoice_no=invoice_no)
        except Invoice.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invoice not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            with transaction.atomic():
                if session_type == 'PICKING':
                    # Delete picking session so it can be picked by anyone
                    try:
                        picking_session = PickingSession.objects.get(invoice=invoice)
                        
                        # Store info for logging before deletion
                        picker_email = picking_session.picker.email if picking_session.picker else "Unknown"
                        
                        # Delete the session completely
                        picking_session.delete()
                        
                        # Return invoice to INVOICED status
                        invoice.status = 'INVOICED'
                        invoice.save(update_fields=['status'])
                        
                        message = f"Picking cancelled for {invoice_no}. Invoice returned to picking list and can be picked by anyone."
                        logger.info(f"Picking session deleted for {invoice_no} by {picker_email}. Reason: {cancel_reason}")
                        
                    except PickingSession.DoesNotExist:
                        return Response({
                            "success": False,
                            "message": "No picking session found for this invoice"
                        }, status=status.HTTP_404_NOT_FOUND)
                
                elif session_type == 'PACKING':
                    # Delete packing session so it can be packed by anyone
                    try:
                        packing_session = PackingSession.objects.get(invoice=invoice)
                        
                        # Store info for logging before deletion
                        packer_email = packing_session.packer.email if packing_session.packer else "Unknown"
                        
                        # Delete the session completely
                        packing_session.delete()
                        
                        # Return invoice to PICKED status (back to packing list)
                        invoice.status = 'PICKED'
                        invoice.save(update_fields=['status'])
                        
                        message = f"Packing cancelled for {invoice_no}. Invoice returned to packing list and can be packed by anyone."
                        logger.info(f"Packing session deleted for {invoice_no} by {packer_email}. Reason: {cancel_reason}")
                        
                    except PackingSession.DoesNotExist:
                        return Response({
                            "success": False,
                            "message": "No packing session found for this invoice"
                        }, status=status.HTTP_404_NOT_FOUND)
                
                elif session_type == 'DELIVERY':
                    # Delete delivery session so it can be delivered by anyone
                    try:
                        delivery_session = DeliverySession.objects.get(invoice=invoice)
                        
                        # Only allow cancellation if not yet delivered
                        if delivery_session.delivery_status == 'DELIVERED':
                            return Response({
                                "success": False,
                                "message": "Cannot cancel a completed delivery"
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        # Store info for logging before deletion
                        assigned_email = delivery_session.assigned_to.email if delivery_session.assigned_to else "Unknown"
                        
                        # Delete the session completely
                        delivery_session.delete()
                        
                        # Return invoice to PACKED status (back to delivery list)
                        invoice.status = 'PACKED'
                        invoice.save(update_fields=['status'])
                        
                        message = f"Delivery cancelled for {invoice_no}. Invoice returned to delivery list and can be delivered by anyone."
                        logger.info(f"Delivery session deleted for {invoice_no} by {assigned_email}. Reason: {cancel_reason}")
                        
                    except DeliverySession.DoesNotExist:
                        return Response({
                            "success": False,
                            "message": "No delivery session found for this invoice"
                        }, status=status.HTTP_404_NOT_FOUND)
                
                else:
                    return Response({
                        "success": False,
                        "message": "Invalid session_type. Must be PICKING, PACKING, or DELIVERY"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Send SSE event
                try:
                    invoice_refreshed = Invoice.objects.select_related(
                        'customer', 'salesman'
                    ).prefetch_related('items').get(id=invoice.id)
                    invoice_data = InvoiceListSerializer(invoice_refreshed).data
                    django_eventstream.send_event(
                        INVOICE_CHANNEL,
                        'message',
                        invoice_data
                    )
                except Exception:
                    logger.exception("Failed to emit cancel event")
                
                return Response({
                    "success": True,
                    "message": message,
                    "data": {
                        "invoice_no": invoice.invoice_no,
                        "status": invoice.status,
                        "session_type": session_type
                    }
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.exception("Failed to cancel session")
            return Response({
                "success": False,
                "message": f"Failed to cancel session: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== History Views =====

class HistoryPagination(PageNumberPagination):
    """Pagination for history endpoints"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PickingHistoryView(generics.ListAPIView):
    """
    GET /api/sales/picking/history/
    
    List picking session history with filtering and search.
    
    Query Parameters:
    - search: Search by invoice number or customer details
    - status: Filter by picking_status (PREPARING, PICKED, VERIFIED, CANCELLED, REVIEW)
    - start_date: Filter by date (YYYY-MM-DD) - sessions created on or after
    - end_date: Filter by date (YYYY-MM-DD) - sessions created on or before
    - page: Page number for pagination
    - page_size: Number of results per page (default: 10, max: 100)
    
    Permissions:
    - Admins: See all picking sessions
    - Regular users: See only their own picking sessions
    """
    from .serializers import PickingHistorySerializer
    serializer_class = PickingHistorySerializer
    pagination_class = HistoryPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # ✅ PERFORMANCE FIX: Prefetch all invoice related data
        queryset = PickingSession.objects.select_related(
            'invoice', 
            'invoice__customer', 
            'invoice__salesman',
            'invoice__created_user',
            'picker'
        ).prefetch_related(
            'invoice__items'
        ).order_by('created_at')
        
        # Permission check: regular users only see their own sessions.
        # Users with role 'PICKER' are treated like admins and can view all picking sessions.
        if not (user.is_admin_or_superadmin() or getattr(user, 'role', '').upper() == 'PICKER'):
            queryset = queryset.filter(picker=user)
        
        # Invoice filters: by primary key or by invoice number
        invoice_id = self.request.query_params.get('invoice') or self.request.query_params.get('invoice_id')
        if invoice_id:
            try:
                queryset = queryset.filter(invoice__id=int(invoice_id))
            except (ValueError, TypeError):
                queryset = queryset.filter(invoice__invoice_no__iexact=invoice_id)
        invoice_no_param = self.request.query_params.get('invoice_no')
        if invoice_no_param:
            queryset = queryset.filter(invoice__invoice_no__iexact=invoice_no_param)

        # Search filter
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(invoice__invoice_no__icontains=search) |
                Q(invoice__customer__name__icontains=search) |
                Q(invoice__customer__email__icontains=search) |
                Q(picker__email__icontains=search)
            )
        
        # Status filter
        status_filter = self.request.query_params.get('status', '').strip().upper()
        if status_filter and status_filter in ['PREPARING', 'PICKED', 'VERIFIED', 'CANCELLED', 'REVIEW']:
            queryset = queryset.filter(picking_status=status_filter)
        
        # Date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            from datetime import datetime
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        if end_date:
            from datetime import datetime
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        return queryset


class PackingHistoryView(generics.ListAPIView):
    """
    GET /api/sales/packing/history/
    
    List packing session history with filtering and search.
    
    Query Parameters:
    - search: Search by invoice number or customer details
    - status: Filter by packing_status (PENDING, IN_PROGRESS, PACKED, CANCELLED, REVIEW)
    - start_date: Filter by date (YYYY-MM-DD) - sessions created on or after
    - end_date: Filter by date (YYYY-MM-DD) - sessions created on or before
    - page: Page number for pagination
    - page_size: Number of results per page (default: 10, max: 100)
    
    Permissions:
    - Admins: See all packing sessions
    - Regular users: See only their own packing sessions
    """
    from .serializers import PackingHistorySerializer
    serializer_class = PackingHistorySerializer
    pagination_class = HistoryPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # ✅ PERFORMANCE FIX: Prefetch all invoice related data
        queryset = PackingSession.objects.select_related(
            'invoice', 
            'invoice__customer',
            'invoice__salesman',
            'invoice__created_user',
            'packer'
        ).prefetch_related(
            'invoice__items'
        ).order_by('created_at')
        
        # Permission check: regular users only see their own sessions
        if not (user.is_admin_or_superadmin() or getattr(user, 'role', '').upper() == 'PACKER'):
            queryset = queryset.filter(packer=user)
        
        # Invoice filters: by primary key or by invoice number
        invoice_id = self.request.query_params.get('invoice') or self.request.query_params.get('invoice_id')
        if invoice_id:
            try:
                queryset = queryset.filter(invoice__id=int(invoice_id))
            except (ValueError, TypeError):
                queryset = queryset.filter(invoice__invoice_no__iexact=invoice_id)
        invoice_no_param = self.request.query_params.get('invoice_no')
        if invoice_no_param:
            queryset = queryset.filter(invoice__invoice_no__iexact=invoice_no_param)

        # Search filter
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(invoice__invoice_no__icontains=search) |
                Q(invoice__customer__name__icontains=search) |
                Q(invoice__customer__email__icontains=search) |
                Q(packer__email__icontains=search)
            )
        
        # Status filter
        status_filter = self.request.query_params.get('status', '').strip().upper()
        if status_filter and status_filter in ['PENDING', 'IN_PROGRESS', 'PACKED', 'CANCELLED', 'REVIEW']:
            queryset = queryset.filter(packing_status=status_filter)
        
        # Date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            from datetime import datetime
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        if end_date:
            from datetime import datetime
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        return queryset


class DeliveryHistoryView(generics.ListAPIView):
    """
    GET /api/sales/delivery/history/
    
    List delivery session history with filtering and search.
    
    Query Parameters:
    - search: Search by invoice number or customer details
    - status: Filter by delivery_status (PENDING, IN_TRANSIT, DELIVERED)
    - delivery_type: Filter by delivery type (DIRECT, COURIER, INTERNAL)
    - start_date: Filter by date (YYYY-MM-DD) - sessions created on or after
    - end_date: Filter by date (YYYY-MM-DD) - sessions created on or before
    - page: Page number for pagination
    - page_size: Number of results per page (default: 10, max: 100)
    
    Permissions:
    - Admins: See all delivery sessions
    - Regular users: See only their own delivery sessions
    """
    from .serializers import DeliveryHistorySerializer
    serializer_class = DeliveryHistorySerializer
    pagination_class = HistoryPagination
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # ✅ PERFORMANCE FIX: Prefetch all invoice and related data
        queryset = DeliverySession.objects.select_related(
            'invoice', 
            'invoice__customer',
            'invoice__salesman',
            'invoice__created_user',
            'assigned_to',
            'delivered_by'
        ).prefetch_related(
            'invoice__items'
        ).order_by('created_at')
        
        # Permission check: regular users only see their own sessions
        if not (
            user.is_admin_or_superadmin() or
            getattr(user, 'role', '').upper() == 'DELIVERY'
        ):
            queryset = queryset.filter(assigned_to=user)
        
        # Invoice filters: by primary key or by invoice number
        invoice_id = self.request.query_params.get('invoice') or self.request.query_params.get('invoice_id')
        if invoice_id:
            try:
                queryset = queryset.filter(invoice__id=int(invoice_id))
            except (ValueError, TypeError):
                queryset = queryset.filter(invoice__invoice_no__iexact=invoice_id)
        invoice_no_param = self.request.query_params.get('invoice_no')
        if invoice_no_param:
            queryset = queryset.filter(invoice__invoice_no__iexact=invoice_no_param)

        # Search filter
        search = self.request.query_params.get('search', '').strip()
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(invoice__invoice_no__icontains=search) |
                Q(invoice__customer__name__icontains=search) |
                Q(invoice__customer__email__icontains=search) |
                Q(assigned_to__email__icontains=search) |
                Q(courier_name__icontains=search) |
                Q(tracking_no__icontains=search)
            )
        
        # Status filter
        status_filter = self.request.query_params.get('status', '').strip().upper()
        if status_filter and status_filter in ['PENDING', 'IN_TRANSIT', 'DELIVERED']:
            queryset = queryset.filter(delivery_status=status_filter)
        
        # Delivery type filter
        delivery_type = self.request.query_params.get('delivery_type', '').strip().upper()
        if delivery_type and delivery_type in ['DIRECT', 'COURIER', 'INTERNAL']:
            queryset = queryset.filter(delivery_type=delivery_type)
        
        # Date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            from datetime import datetime
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_dt)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        if end_date:
            from datetime import datetime
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_dt)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        return queryset


# ===== Billing Section APIs =====

class BillingInvoicesView(generics.ListAPIView):
    """
    GET /api/sales/billing/invoices/
    List invoices for the billing section.
    
    - Regular users see only invoices where they are the salesman
    - Admin/superadmin see all invoices
    
    Query Parameters:
    - status: Filter by invoice status (INVOICED, PICKING, etc.)
    - billing_status: Filter by billing status (BILLED, REVIEW, RE_INVOICED)
    - salesman: Filter by salesman name (for admin)
    
    Authentication: Required
    """
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InvoiceListPagination
    
    def get_queryset(self):
        user = self.request.user
        # ✅ PERFORMANCE FIX: Prefetch all session and related data
        # Note: Using select_related on OneToOne fields that may not exist (pickingsession, etc.)
        queryset = Invoice.objects.select_related(
            'customer', 
            'salesman', 
            'created_user'
        ).prefetch_related(
            'items', 
            'invoice_returns', 
            'invoice_returns__returned_by',
            'invoice_returns__resolved_by',
            'pickingsession',
            'pickingsession__picker',
            'packingsession',
            'packingsession__packer',
            'deliverysession',
            'deliverysession__assigned_to',
            'deliverysession__delivered_by'
        ).order_by('created_at')
        
        # If user is not admin, filter to only show invoices where they are the salesman
        if not user.is_admin_or_superadmin():
            # Filter by salesman matching user's name
            from django.db.models import Q
            queryset = queryset.filter(
                salesman__name__iexact=user.name
            )
        
        # Filter by invoice status
        status_list = self.request.query_params.getlist('status')
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        
        # Filter by billing status
        billing_status_list = self.request.query_params.getlist('billing_status')
        if billing_status_list:
            queryset = queryset.filter(billing_status__in=billing_status_list)
        
        # Filter by salesman (for admin searches)
        salesman_name = self.request.query_params.get('salesman')
        if salesman_name and user.is_admin_or_superadmin():
            queryset = queryset.filter(salesman__name__icontains=salesman_name)
        
        return queryset


class ReturnToBillingView(APIView):
    """
    POST /api/sales/billing/return/
    Send an invoice for review from picking/packing section.
    
    Request body:
    {
        "invoice_no": "INV-001",
        "return_reason": "Missing items in stock",
        "user_email": "picker@example.com"  // optional, defaults to authenticated user
    }
    
    Authentication: Required
    
    Sets the invoice to REVIEW status with billing_status=REVIEW
    so it can be corrected and re-invoiced by billing staff.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from .serializers import ReturnToBillingSerializer
        from .models import InvoiceReturn
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        serializer = ReturnToBillingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        invoice = serializer.validated_data['invoice']
        return_reason = serializer.validated_data['return_reason']
        user_email = serializer.validated_data.get('user_email')
        
        # Determine who is sending the invoice for review
        if user_email:
            try:
                returning_user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                returning_user = request.user
        else:
            returning_user = request.user
        
        # Auto-detect which section is returning the invoice based on current status
        returned_from_section = None
        if invoice.status in ['PICKING', 'PICKED']:
            returned_from_section = 'PICKING'
        elif invoice.status == 'PACKING':
            returned_from_section = 'PACKING'
        elif invoice.status in ['PACKED', 'DISPATCHED', 'DELIVERED']:
            returned_from_section = 'DELIVERY'
        
        # Create InvoiceReturn record
        invoice_return = InvoiceReturn.objects.create(
            invoice=invoice,
            return_reason=return_reason,
            returned_by=returning_user,
            returned_from_section=returned_from_section
        )
        
        # Update invoice status
        invoice.billing_status = 'REVIEW'
        invoice.status = 'REVIEW'
        invoice.save()
        
        # Cancel any active picking/packing sessions if they exist
        if hasattr(invoice, 'pickingsession'):
            picking_session = invoice.pickingsession
            if picking_session.picking_status == 'PREPARING':
                picking_session.picking_status = 'REVIEW'
                picking_session.notes = f"Cancelled due to review needed: {return_reason}"
                picking_session.save()
        
        if hasattr(invoice, 'packingsession'):
            packing_session = invoice.packingsession
            if packing_session.packing_status == 'IN_PROGRESS':
                packing_session.packing_status = 'REVIEW'
                packing_session.notes = f"Cancelled due to review needed: {return_reason}"
                packing_session.save()
        
        # Send full invoice data event (not just notification)
        try:
            # Refresh invoice with all relations
            invoice_refreshed = Invoice.objects.select_related(
                'customer', 'salesman'
            ).prefetch_related('items', 'invoice_returns', 'invoice_returns__returned_by').get(id=invoice.id)
            
            # Serialize full invoice data with picker/packer info
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            
            # Send full invoice update
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
            
            # Also send a review notification event (includes which section triggered the return)
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                {
                    'type': 'invoice_review',
                    'invoice_no': invoice.invoice_no,
                    'sent_by': returning_user.email,
                    'review_reason': return_reason,
                    'returned_from_section': invoice_return.returned_from_section,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to send invoice review event: {e}")
        
        return Response({
            "success": True,
            "message": f"Invoice {invoice.invoice_no} has been sent for review and corrections",
            "data": {
                "invoice_no": invoice.invoice_no,
                "billing_status": invoice.billing_status,
                "review_reason": invoice_return.return_reason,
                "returned_from_section": invoice_return.returned_from_section,
                "sent_by": returning_user.email,
                "sent_at": invoice_return.returned_at
            }
        }, status=status.HTTP_200_OK)


from rest_framework import viewsets
from apps.common.viewsets import BaseModelViewSet
from apps.common.response import success_response, error_response, created_response
from apps.accounts.models import Courier
from .serializers import CourierSerializer


class CourierViewSet(BaseModelViewSet):
    """
    ViewSet for managing couriers
    Provides CRUD operations for courier management
    """
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'courier_id'
    
    def get_queryset(self):
        """
        Filter couriers based on query parameters
        - status: Filter by status (ACTIVE/INACTIVE)
        - type: Filter by type (EXTERNAL/INTERNAL)
        - search: Search in courier_name, courier_code, contact_person
        """
        queryset = Courier.objects.all()
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())
        
        # Filter by type
        type_param = self.request.query_params.get('type', None)
        if type_param:
            queryset = queryset.filter(type=type_param.upper())
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(courier_name__icontains=search) |
                Q(courier_code__icontains=search) |
                Q(contact_person__icontains=search)
            )
        
        return queryset.order_by('created_at')
    
    def list(self, request, *args, **kwargs):
        """
        List all couriers with optional filtering
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return success_response(
            data=serializer.data,
            message='Couriers retrieved successfully'
        )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new courier
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return created_response(
                data=serializer.data,
                message='Courier created successfully'
            )
        
        return error_response(
            message='Validation error',
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single courier
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return success_response(
            data=serializer.data,
            message='Courier retrieved successfully'
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update a courier (full update)
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message='Courier updated successfully'
            )
        
        return error_response(
            message='Validation error',
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update of a courier
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a courier
        """
        instance = self.get_object()
        courier_name = instance.courier_name
        instance.delete()
        
        return success_response(
            message=f'Courier "{courier_name}" deleted successfully'
        )


