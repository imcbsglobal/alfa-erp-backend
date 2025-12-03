"""
URL routing for Access Control
"""
from django.urls import path
from .views import UserMenuView

app_name = 'accesscontrol'

urlpatterns = [
    path('menus/', UserMenuView.as_view(), name='user-menus'),
]
