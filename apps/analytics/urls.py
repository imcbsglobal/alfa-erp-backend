from django.urls import path
from .views import DashboardStatsView, DashboardStatsSSEView, RecalculateHoldSnapshotView, StatusBreakdownView

urlpatterns = [
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard-stats-stream/', DashboardStatsSSEView.as_view(), name='dashboard-stats-stream'),
    path('recalculate-hold/', RecalculateHoldSnapshotView.as_view(), name='recalculate-hold'),
    path('status-breakdown/', StatusBreakdownView.as_view(), name='status-breakdown'),
]