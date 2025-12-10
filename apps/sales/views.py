# apps/sales/views.py

import time
import json
from collections import deque

from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import InvoiceImportSerializer
from .events import invoice_events  # global queue for SSE events


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
        invoice = serializer.save()

        # Push event for SSE live updates
        invoice_events.append({
            "id": invoice.id,
            "amount": str(invoice.amount),
            "created_at": invoice.created_at.isoformat()
        })

        return Response(
            {
                "success": True,
                "message": "Invoice imported successfully"
            },
            status=status.HTTP_201_CREATED
        )


# -----------------------------------
# SSE Stream View: Live Invoice Updates
# -----------------------------------
def invoice_stream(request):
    """
    SSE endpoint that streams new invoices in real-time.
    Frontend can connect using EventSource.
    """

    def event_stream():
        while True:
            if invoice_events:  # check for new events
                event = invoice_events.popleft()
                yield f"data: {json.dumps(event)}\n\n"
            
            time.sleep(0.5)  

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response
