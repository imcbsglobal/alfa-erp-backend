from django.urls import path
from .views import ImportInvoiceView

urlpatterns = [
    path("import/invoice/", ImportInvoiceView.as_view(), name="import-invoice"),
]