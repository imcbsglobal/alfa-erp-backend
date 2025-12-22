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
        queryset = Invoice.objects.select_related('customer', 'salesman', 'created_user').prefetch_related('items').order_by('-created_at')
        
        # Filter by status (supports multiple values: ?status=PENDING&status=PICKING)
        status_list = self.request.query_params.getlist('status')
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        
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

        # Check for active picking session
        picking_session = PickingSession.objects.filter(
            picker=target_user,
            picking_status='PREPARING'
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

        # Check for active packing session
        packing_session = PackingSession.objects.filter(
            packer=target_user,
            packing_status='IN_PROGRESS'
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
                    "total_amount": total_amount
                }
            },
            status=status.HTTP_201_CREATED
        )

# SSE endpoint is now handled by django-eventstream
# See urls.py for the eventstream path configuration


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
                "message": "Validation failed",
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
                picking_status='PREPARING'
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
        "notes": "Picking completed"
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
        
        # Update picking session
        picking_session.end_time = timezone.now()
        picking_session.picking_status = "PICKED"
        if notes:
            picking_session.notes = (picking_session.notes or '') + f"\n{notes}"
        picking_session.save()
        
        # Update invoice status
        invoice.status = "PICKED"
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
            logger.exception("Failed to emit picking complete event")
        
        response_serializer = PickingSessionReadSerializer(picking_session)
        return Response({
            "success": True,
            "message": f"Picking completed for {invoice.invoice_no}",
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
            packing_status='IN_PROGRESS'
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
            notes=notes
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

class StartDeliveryView(APIView):
    """
    POST /api/sales/delivery/start/
    Start delivery session - User scans their email (required for DIRECT/INTERNAL)
    Body: {
        "invoice_no": "INV-001",
        "user_email": "driver@company.com",  # Required for DIRECT/INTERNAL
        "delivery_type": "DIRECT",  # DIRECT, COURIER, INTERNAL
        "courier_name": "DHL",      # For COURIER type
        "tracking_no": "TRK123",    # Optional
        "notes": "Starting delivery"
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
        user = validated_data.get('user')
        delivery_type = validated_data['delivery_type']
        courier_name = validated_data.get('courier_name', '')
        tracking_no = validated_data.get('tracking_no', '')
        notes = validated_data.get('notes', '')
        
        # Create delivery session
        delivery_session = DeliverySession.objects.create(
            invoice=invoice,
            delivery_type=delivery_type,
            assigned_to=user,
            courier_name=courier_name,
            tracking_no=tracking_no,
            start_time=timezone.now(),
            delivery_status="IN_TRANSIT",
            notes=notes
        )
        
        # Update invoice status
        invoice.status = "DISPATCHED"
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
            logger.exception("Failed to emit delivery start event")
        
        response_serializer = DeliverySessionReadSerializer(delivery_session)
        return Response({
            "success": True,
            "message": f"Delivery started - {delivery_type}",
            "data": response_serializer.data
        }, status=status.HTTP_201_CREATED)


class CompleteDeliveryView(APIView):
    """
    POST /api/sales/delivery/complete/
    Complete delivery - User scans their email to confirm delivery
    Body: {
        "invoice_no": "INV-001",
        "user_email": "driver@company.com",  # Optional for COURIER
        "delivery_status": "DELIVERED",  # DELIVERED or IN_TRANSIT
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
        
        # Update delivery session
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
        queryset = PickingSession.objects.select_related(
            'invoice', 'invoice__customer', 'picker'
        ).order_by('-created_at')
        
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
        queryset = PackingSession.objects.select_related(
            'invoice', 'invoice__customer', 'packer'
        ).order_by('-created_at')
        
        # Permission check: regular users only see their own sessions
        if not user.is_admin_or_superadmin():
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
        queryset = DeliverySession.objects.select_related(
            'invoice', 'invoice__customer', 'assigned_to'
        ).order_by('-created_at')
        
        # Permission check: regular users only see their own sessions
        if not user.is_admin_or_superadmin():
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
    
    - Regular users see only their own created invoices (by created_by or created_user)
    - Admin/superadmin see all invoices
    
    Query Parameters:
    - status: Filter by invoice status (INVOICED, PICKING, etc.)
    - billing_status: Filter by billing status (BILLED, REVIEW, RE_INVOICED)
    - created_by: Filter by created_by string field (for admin)
    
    Authentication: Required
    """
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = InvoiceListPagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Invoice.objects.select_related('customer', 'salesman', 'created_user', 'returned_by').prefetch_related('items').order_by('-created_at')
        
        # If user is not admin, filter to only show their own invoices
        if not user.is_admin_or_superadmin():
            # Filter by created_user or created_by matching user's email or name
            from django.db.models import Q
            queryset = queryset.filter(
                Q(created_user=user) | 
                Q(created_by=self.request.user.email) | 
                Q(created_by__icontains=self.request.user.name)
            )
        
        # Filter by invoice status
        status_list = self.request.query_params.getlist('status')
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        
        # Filter by billing status
        billing_status_list = self.request.query_params.getlist('billing_status')
        if billing_status_list:
            queryset = queryset.filter(billing_status__in=billing_status_list)
        
        # Filter by created_by (for admin searches)
        created_by = self.request.query_params.get('created_by')
        if created_by and user.is_admin_or_superadmin():
            queryset = queryset.filter(created_by__icontains=created_by)
        
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
        
        # Update invoice with review information
        invoice.billing_status = 'REVIEW'
        invoice.return_reason = return_reason
        invoice.returned_by = returning_user
        invoice.returned_at = timezone.now()
        invoice.status = 'REVIEW'  # Set to REVIEW status for billing corrections
        invoice.save()
        
        # Cancel any active picking/packing sessions if they exist
        if hasattr(invoice, 'pickingsession'):
            picking_session = invoice.pickingsession
            if picking_session.picking_status == 'PREPARING':
                picking_session.picking_status = 'CANCELLED'
                picking_session.notes = f"Cancelled due to review needed: {return_reason}"
                picking_session.save()
        
        if hasattr(invoice, 'packingsession'):
            packing_session = invoice.packingsession
            if packing_session.packing_status == 'IN_PROGRESS':
                packing_session.packing_status = 'CANCELLED'
                packing_session.notes = f"Cancelled due to review needed: {return_reason}"
                packing_session.save()
        
        # Send full invoice data event (not just notification)
        try:
            # Refresh invoice with all relations
            invoice_refreshed = Invoice.objects.select_related(
                'customer', 'salesman', 'returned_by'
            ).prefetch_related('items').get(id=invoice.id)
            
            # Serialize full invoice data with picker/packer info
            invoice_data = InvoiceListSerializer(invoice_refreshed).data
            
            # Send full invoice update
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                invoice_data
            )
            
            # Also send a review notification event
            django_eventstream.send_event(
                INVOICE_CHANNEL,
                'message',
                {
                    'type': 'invoice_review',
                    'invoice_no': invoice.invoice_no,
                    'sent_by': returning_user.email,
                    'review_reason': return_reason,
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
                "review_reason": invoice.return_reason,
                "sent_by": returning_user.email,
                "sent_at": invoice.returned_at
            }
        }, status=status.HTTP_200_OK)


