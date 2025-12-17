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
    """
    queryset = Invoice.objects.select_related('customer', 'salesman', 'created_user').prefetch_related('items').order_by('-created_at')
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = InvoiceListPagination


# ===== Retrieve Invoice API =====
class InvoiceDetailView(generics.RetrieveAPIView):
    """
    GET /api/sales/invoices/{id}/
    Retrieve a single invoice by primary key with nested customer, salesman and items.
    """
    queryset = Invoice.objects.select_related('customer', 'salesman', 'created_user').prefetch_related('items')
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
            try:
                with transaction.atomic():
                    data = serializer.validated_data
                    customer_data = data.get('customer')
                    items_data = data.get('items', [])
                    salesman_name = data.get('salesman')

                    # Upsert salesman and customer
                    from .models import Salesman, Customer, InvoiceItem

                    salesman, _ = Salesman.objects.get_or_create(name=salesman_name)
                    customer, _ = Customer.objects.update_or_create(
                        code=customer_data['code'],
                        defaults=customer_data
                    )

                    # Update invoice fields
                    existing.invoice_date = data.get('invoice_date')
                    existing.salesman = salesman
                    existing.customer = customer
                    existing.created_by = data.get('created_by')
                    existing.remarks = data.get('remarks', existing.remarks)
                    if request.user and request.user.is_authenticated:
                        existing.created_user = request.user
                    existing.save()

                    # Replace items: delete existing and recreate
                    InvoiceItem.objects.filter(invoice=existing).delete()
                    for item in items_data:
                        InvoiceItem.objects.create(invoice=existing, **item)

                    total_amount = sum(item['quantity'] * item['mrp'] for item in items_data)

                    # Emit SSE event for updated invoice
                    try:
                        invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=existing.id)
                        serializer_out = InvoiceListSerializer(invoice_refreshed)
                        django_eventstream.send_event(
                            INVOICE_CHANNEL,
                            'message',
                            serializer_out.data
                        )
                        logger.debug("Invoice update event sent: %s", existing.invoice_no)
                    except Exception:
                        logger.exception("Failed to send invoice update event")

                    return Response(
                        {
                            "success": True,
                            "message": "Invoice updated successfully",
                            "data": {"id": existing.id, "invoice_no": existing.invoice_no, "total_amount": total_amount}
                        },
                        status=status.HTTP_200_OK,
                    )
            except Exception:
                logger.exception("Failed to update existing invoice")
                return Response({"success": False, "message": "Failed to update existing invoice."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                picking_status='PENDING'
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
