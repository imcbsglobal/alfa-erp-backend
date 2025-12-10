# apps/sales/views.py

import time
import json
import queue
import logging
from django.db import IntegrityError


from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import InvoiceImportSerializer, InvoiceListSerializer
from .events import invoice_events  
from .models import Invoice
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly


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

# -----------------------------------
# DRF API View: Import Invoice
# -----------------------------------
class ImportInvoiceView(APIView):
    """
    API endpoint to import a new invoice.
    After saving, it pushes an event to the SSE queue for live updates.
    """
    def post(self, request):
        serializer = InvoiceImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invoice_no = serializer.validated_data.get("invoice_no")

        # If you want to disallow duplicates: check before save and return 409
        existing = Invoice.objects.filter(invoice_no=invoice_no).first()
        if existing:
            return Response(
                {
                    "success": False,
                    "message": "Invoice with this invoice_no already exists.",
                    "data": {"id": existing.id, "invoice_no": existing.invoice_no},
                },
                status=status.HTTP_409_CONFLICT,
            )

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

        # Push full invoice payload to SSE queue (same format as list API)
        try:
            invoice_refreshed = Invoice.objects.select_related('customer', 'salesman').prefetch_related('items').get(id=invoice.id)
            serializer = InvoiceListSerializer(invoice_refreshed)
            invoice_events.put(serializer.data, block=False)
            logger.debug("Invoice event queued: %s", invoice.invoice_no)
        except Exception:
            logger.exception("Failed to enqueue invoice event")

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



def invoice_stream(request):

    def event_stream():
        while True:
            try:
                # Wait up to 1 second for new event
                event = invoice_events.get(timeout=1)

                yield f"data: {json.dumps(event)}\n\n"

            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield ": keep-alive\n\n"

            time.sleep(0.2)

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"

    return response
