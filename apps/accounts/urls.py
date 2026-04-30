"""
URL configuration for accounts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    TrayViewSet,
    UserViewSet,
    JobTitleViewSet,
    DepartmentViewSet
)

router = DefaultRouter()
#  /api/auth/users/` — Admin-only create user 
router.register(r'users', UserViewSet, basename='user')
router.register(r'job-titles', JobTitleViewSet, basename='job-title')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'trays', TrayViewSet, basename='tray')

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('', include(router.urls)),
]
