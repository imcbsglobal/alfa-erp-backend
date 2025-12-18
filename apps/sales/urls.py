from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
import django_eventstream
from .views import (
    ImportInvoiceView, 
    InvoiceListView, 
    InvoiceDetailView,
    MyActivePickingView,
    MyActivePackingView,
    StartPickingView,
    CompletePickingView,
    StartPackingView,
    CompletePackingView,
    StartDeliveryView,
    CompleteDeliveryView,
    PickingHistoryView,
    PackingHistoryView,
    DeliveryHistoryView,
)

urlpatterns = [
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("import/invoice/", ImportInvoiceView.as_view(), name="import-invoice"),
    
    # SSE endpoint using django-eventstream (CSRF exempt)
    path("sse/invoices/", csrf_exempt(django_eventstream.views.events), {'channels': ['invoices']}, name="invoice-stream"),
    
    # Picking workflow
    path("picking/start/", StartPickingView.as_view(), name="picking-start"),
    path("picking/active/", MyActivePickingView.as_view(), name="picking-active"),
    path("picking/complete/", CompletePickingView.as_view(), name="picking-complete"),
    path("picking/history/", PickingHistoryView.as_view(), name="picking-history"),
    
    # Packing workflow
    path("packing/active/", MyActivePackingView.as_view(), name="packing-active"),
    path("packing/start/", StartPackingView.as_view(), name="packing-start"),
    path("packing/complete/", CompletePackingView.as_view(), name="packing-complete"),
    path("packing/history/", PackingHistoryView.as_view(), name="packing-history"),
    
    # Delivery workflow
    path("delivery/start/", StartDeliveryView.as_view(), name="delivery-start"),
    path("delivery/complete/", CompleteDeliveryView.as_view(), name="delivery-complete"),
    path("delivery/history/", DeliveryHistoryView.as_view(), name="delivery-history"),
]
