from django.urls import path
from .views import (
    ImportInvoiceView, 
    invoice_stream, 
    InvoiceListView, 
    InvoiceDetailView,
    StartPickingView,
    CompletePickingView,
    StartPackingView,
    CompletePackingView,
    StartDeliveryView,
    CompleteDeliveryView,
)

urlpatterns = [
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("import/invoice/", ImportInvoiceView.as_view(), name="import-invoice"),
    path("sse/invoices/", invoice_stream, name="invoice-stream"),
    
    # Picking workflow
    path("picking/start/", StartPickingView.as_view(), name="picking-start"),
    path("picking/complete/", CompletePickingView.as_view(), name="picking-complete"),
    
    # Packing workflow
    path("packing/start/", StartPackingView.as_view(), name="packing-start"),
    path("packing/complete/", CompletePackingView.as_view(), name="packing-complete"),
    
    # Delivery workflow
    path("delivery/start/", StartDeliveryView.as_view(), name="delivery-start"),
    path("delivery/complete/", CompleteDeliveryView.as_view(), name="delivery-complete"),
]
