from django.urls import path
from .views import ImportInvoiceView, invoice_stream, InvoiceListView, InvoiceDetailView

urlpatterns = [
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("import/invoice/", ImportInvoiceView.as_view(), name="import-invoice"),
    path("sse/invoices/", invoice_stream, name="invoice-stream"),  
]
