from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
import django_eventstream
from rest_framework.routers import DefaultRouter
from .views import (
    ImportInvoiceView,
    InvoiceReportExportView,
    UpdateInvoiceView,
    InvoiceListView, 
    InvoiceDetailView,
    MyActivePickingView,
    MyActivePackingView,
    StartPickingView,
    CompletePickingView,
    StartPackingView,
    StartDeliveryView,
    CompleteDeliveryView,
    PickingHistoryView,
    PackingHistoryView,
    DeliveryHistoryView,
    BillingHistoryView,
    BillingInvoicesView,
    ReturnToBillingView,
    BillingUserSummaryView,
    CourierViewSet,
    DeliveryConsiderListView,
    AssignDeliveryStaffView,
    EligibleDeliveryStaffView,
    UploadCourierSlipView,
    CancelSessionView,
    MissingInvoiceFinderView,
    BulkPickingStartView,
    BulkPickingCompleteView,
    InvoiceReportView,
    GetMyCheckingBillsView,
    GetBillDetailsView,
    StartCheckingView,
    SearchTrayView,
    GetTrayBillDetailsView,
    SaveTrayDraftView,
    CompletePackingWithTraysView,
    GetBoxingInvoicesView,
    GetBoxingDataView,
    CompleteBoxingView,
    InvoicePublicDetailView,
)
from .admin_views import AdminCompleteWorkflowView, AdminBulkStatusUpdateView, AdminBulkStatusHistoryView

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
    path("packing/history/", PackingHistoryView.as_view(), name="packing-history"),
    
    # Box-based packing (checking)
    path("packing/my-checking/", GetMyCheckingBillsView.as_view(), name="packing-my-checking"),
    path("packing/bill/<str:invoice_no>/", GetBillDetailsView.as_view(), name="packing-bill-details"),
    path("packing/start-checking/", StartCheckingView.as_view(), name="packing-start-checking"),
    path("packing/invoice-public/<str:invoice_no>/", InvoicePublicDetailView.as_view(), name="packing-invoice-public"),
    path("packing/search-trays/", SearchTrayView.as_view(), name="packing-search-trays"),
    path("packing/tray-bill/<str:invoice_no>/", GetTrayBillDetailsView.as_view(), name="packing-tray-bill-details"),
    path("packing/save-tray-draft/", SaveTrayDraftView.as_view(), name="packing-save-tray-draft"),
    path("packing/complete-tray-packing/", CompletePackingWithTraysView.as_view(), name="packing-complete-with-trays"),
    path("packing/boxing-invoices/", GetBoxingInvoicesView.as_view(), name="packing-boxing-invoices"),
    path("packing/boxing-data/<str:invoice_no>/", GetBoxingDataView.as_view(), name="packing-boxing-data"),
    path("packing/complete-boxing/", CompleteBoxingView.as_view(), name="packing-complete-boxing"),
    
    # Delivery workflow
    path("delivery/start/", StartDeliveryView.as_view(), name="delivery-start"),
    path("delivery/complete/", CompleteDeliveryView.as_view(), name="delivery-complete"),
    path("delivery/history/", DeliveryHistoryView.as_view(), name="delivery-history"),

    path('cancel-session/', CancelSessionView.as_view(), name='cancel-session'),
    
    path("delivery/consider-list/", DeliveryConsiderListView.as_view(), name="delivery-consider-list"),
    path("delivery/eligible-staff/", EligibleDeliveryStaffView.as_view(), name="delivery-eligible-staff"),
    path("delivery/assign/", AssignDeliveryStaffView.as_view(), name="delivery-assign-staff"),
    path("delivery/upload-slip/", UploadCourierSlipView.as_view()),

    # Billing endpoints
    path("billing/history/", BillingHistoryView.as_view(), name="billing-history"),
    path("billing/invoices/", BillingInvoicesView.as_view(), name="billing-invoices"),
    path("billing/return/", ReturnToBillingView.as_view(), name="billing-return"),
    path("billing/user-summary/", BillingUserSummaryView.as_view(), name="billing-user-summary"),
    
    # Admin endpoints
    path("admin/complete-workflow/", AdminCompleteWorkflowView.as_view(), name="admin-complete-workflow"),
    path("admin/bulk-status-update/", AdminBulkStatusUpdateView.as_view(), name="admin-bulk-status-update"),
    path("admin/bulk-status-history/", AdminBulkStatusHistoryView.as_view(), name="admin-bulk-status-history"),
    
    # Missing Invoice Finder
    path("missing-invoices/", MissingInvoiceFinderView.as_view(), name="missing-invoices"),
    
    # Invoice Report
    path("invoice-report/", InvoiceReportView.as_view(), name="invoice-report"),
    path('invoice-report/export/', InvoiceReportExportView.as_view(), name='invoice-report-export'),
]

