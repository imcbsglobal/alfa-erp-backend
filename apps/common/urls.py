from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .developer import ClearDataView, TableStatsView, ResetSequencesView, TruncateTableView
from .views import DeveloperSettingsView, TrayViewSet

router = DefaultRouter()
router.register(r'trays', TrayViewSet, basename='tray')

urlpatterns = [
    path('developer/table-stats/', TableStatsView.as_view(), name='developer-table-stats'),
    path('developer/clear-data/', ClearDataView.as_view(), name='developer-clear-data'),
    path('developer/reset-sequences/', ResetSequencesView.as_view(), name='developer-reset-sequences'),
    path('developer/truncate-table/', TruncateTableView.as_view(), name='developer-truncate-table'),
    path('developer-settings/', DeveloperSettingsView.as_view(), name='developer-settings'),
    path('', include(router.urls)),
]