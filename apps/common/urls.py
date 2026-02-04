"""
Common app URLs
"""
from django.urls import path
from .developer import ClearDataView, TableStatsView, ResetSequencesView, TruncateTableView
from .views import DeveloperSettingsView

urlpatterns = [
    # Developer Tools (SUPERADMIN only)
    path('developer/table-stats/', TableStatsView.as_view(), name='developer-table-stats'),
    path('developer/clear-data/', ClearDataView.as_view(), name='developer-clear-data'),
    path('developer/reset-sequences/', ResetSequencesView.as_view(), name='developer-reset-sequences'),
    path('developer/truncate-table/', TruncateTableView.as_view(), name='developer-truncate-table'),
    
    # Developer Settings (GET: all users, PUT: SUPERADMIN only)
    path('common/developer-settings/', DeveloperSettingsView.as_view(), name='developer-settings'),
]
