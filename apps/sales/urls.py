from django.urls import path
from .views import ImportInvoiceView, invoice_stream

urlpatterns = [
    path("import/invoice/", ImportInvoiceView.as_view(), name="import-invoice"),
    path("sse/invoices/", invoice_stream, name="invoice-stream"),  
]
