"""
Analytics app URL configuration
"""
from django.urls import path
from .views import DashboardStatsView, DashboardStatsSSEView

urlpatterns = [
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard-stats-stream/', DashboardStatsSSEView.as_view(), name='dashboard-stats-stream'),
]
