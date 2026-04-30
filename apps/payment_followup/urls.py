from django.urls import path
from .views import (
    FollowUpTrackerAPI,
    EscalationRecipientsAPI,
    FollowUpListCreateAPI,
    FollowUpDetailAPI,
    AlertListAPI,
    AlertResolveAPI,
    FollowUpReportAPI,
)

urlpatterns = [
    path('tracker/',                    FollowUpTrackerAPI.as_view(),       name='followup_tracker'),
    path('escalation-recipients/',      EscalationRecipientsAPI.as_view(),  name='followup_escalation_recipients'),
    path('logs/',                       FollowUpListCreateAPI.as_view(),    name='followup_list_create'),
    path('logs/<int:pk>/',              FollowUpDetailAPI.as_view(),        name='followup_detail'),
    path('alerts/',                     AlertListAPI.as_view(),             name='alert_list'),
    path('alerts/<int:pk>/resolve/',    AlertResolveAPI.as_view(),          name='alert_resolve'),
    path('report/',                     FollowUpReportAPI.as_view(),        name='followup_report'),
]