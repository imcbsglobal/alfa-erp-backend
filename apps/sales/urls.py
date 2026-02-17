from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
import django_eventstream
from rest_framework.routers import DefaultRouter
from .views import (
    ImportInvoiceView,
    UpdateInvoiceView,
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
    BillingInvoicesView,
    ReturnToBillingView,
    CourierViewSet,
    DeliveryConsiderListView,
    AssignDeliveryStaffView,
    UploadCourierSlipView,
    CancelSessionView,
    MissingInvoiceFinderView,
    BulkPickingStartView,
    BulkPickingCompleteView,
    InvoiceReportView,
    GetMyCheckingBillsView,
    GetBillDetailsView,
    StartCheckingView,
    CompleteCheckingView,
    CompletePackingWithBoxesView,
    GetCompletedPackingDataView,
    BoxDetailsView,
    GetBillsByAddressView,
    GetAllCheckingDoneBillsView,
    GetHeldBillsByCustomerView,
    CompleteConsolidatedPackingView,
    BillingUserSummaryView,
)
from .admin_views import AdminCompleteWorkflowView

router = DefaultRouter()
router.register(r'couriers', CourierViewSet, basename='courier')

urlpatterns = [
    # Router URLs for ViewSets
    path('', include(router.urls)),
    
    path("invoices/", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/<int:pk>/", InvoiceDetailView.as_view(), name="invoice-detail"),
    path("import/invoice/", ImportInvoiceView.as_view(), name="import-invoice"),
    path("update/invoice/", UpdateInvoiceView.as_view(), name="update-invoice"),
    
    #Common Invoice SSE endpoint using django-eventstream (CSRF exempt)
    path("sse/invoices/", csrf_exempt(django_eventstream.views.events), {'channels': ['invoices']}, name="invoice-stream"),
    
    # Picking workflow
    path("picking/start/", StartPickingView.as_view(), name="picking-start"),
    path("picking/active/", MyActivePickingView.as_view(), name="picking-active"),
    path("picking/complete/", CompletePickingView.as_view(), name="picking-complete"),
    path("picking/history/", PickingHistoryView.as_view(), name="picking-history"),
    path("picking/bulk-start/", BulkPickingStartView.as_view(), name="bulk-picking-start"),
    path("picking/bulk-complete/", BulkPickingCompleteView.as_view(), name="bulk-picking-complete"),
    
    # Packing workflow
    path("packing/active/", MyActivePackingView.as_view(), name="packing-active"),
    path("packing/start/", StartPackingView.as_view(), name="packing-start"),
    path("packing/complete/", CompletePackingView.as_view(), name="packing-complete"),
    path("packing/history/", PackingHistoryView.as_view(), name="packing-history"),
    
    # Box-based packing workflow
    path("packing/my-checking/", GetMyCheckingBillsView.as_view(), name="packing-my-checking"),
    path("packing/bill/<str:invoice_no>/", GetBillDetailsView.as_view(), name="packing-bill-details"),
    path("packing/start-checking/", StartCheckingView.as_view(), name="packing-start-checking"),
    path("packing/complete-checking/", CompleteCheckingView.as_view(), name="packing-complete-checking"),
    path("packing/complete-packing/", CompletePackingWithBoxesView.as_view(), name="packing-complete-with-boxes"),
    path("packing/completed/<str:invoice_no>/", GetCompletedPackingDataView.as_view(), name="packing-completed-data"),
    path("packing/box-details/<str:box_id>/", BoxDetailsView.as_view(), name="packing-box-details"),
    path("packing/bills-by-address/", GetBillsByAddressView.as_view(), name="packing-bills-by-address"),
    path("packing/all-checking-done-bills/", GetAllCheckingDoneBillsView.as_view(), name="packing-all-checking-done"),
    path("packing/held-bills-by-customer/", GetHeldBillsByCustomerView.as_view(), name="packing-held-bills-by-customer"),
    path("packing/complete-consolidated-packing/", CompleteConsolidatedPackingView.as_view(), name="packing-complete-consolidated"),
    
    # Delivery workflow
    path("delivery/start/", StartDeliveryView.as_view(), name="delivery-start"),
    path("delivery/complete/", CompleteDeliveryView.as_view(), name="delivery-complete"),
    path("delivery/history/", DeliveryHistoryView.as_view(), name="delivery-history"),

    path('cancel-session/', CancelSessionView.as_view(), name='cancel-session'),
    
    path("delivery/consider-list/", DeliveryConsiderListView.as_view(), name="delivery-consider-list"),
    path("delivery/assign/", AssignDeliveryStaffView.as_view(), name="delivery-assign-staff"),
    path("delivery/upload-slip/", UploadCourierSlipView.as_view()),

    # Billing endpoints
    path("billing/invoices/", BillingInvoicesView.as_view(), name="billing-invoices"),
    path("billing/return/", ReturnToBillingView.as_view(), name="billing-return"),
    path("billing/user-summary/", BillingUserSummaryView.as_view(), name="billing-user-summary"),
    
    # Admin endpoints
    path("admin/complete-workflow/", AdminCompleteWorkflowView.as_view(), name="admin-complete-workflow"),
    
    # Missing Invoice Finder
    path("missing-invoices/", MissingInvoiceFinderView.as_view(), name="missing-invoices"),
    
    # Invoice Report
    path("invoice-report/", InvoiceReportView.as_view(), name="invoice-report"),
]

