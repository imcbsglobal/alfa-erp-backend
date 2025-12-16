"""
URL routing for Access Control
"""
from django.urls import path
from .views import (
    UserMenuView,
    AllMenusView,
    AssignMenusView,
    UserMenuAssignmentsView
)

app_name = 'accesscontrol'

urlpatterns = [
    # User endpoints
    path('menus/', UserMenuView.as_view(), name='user-menus'),
    
    # Admin endpoints
    path('admin/menus/', AllMenusView.as_view(), name='all-menus'),
    path('admin/assign-menus/', AssignMenusView.as_view(), name='assign-menus'),
    path('admin/users/<uuid:user_id>/menus/', UserMenuAssignmentsView.as_view(), name='user-menu-assignments'),
]
