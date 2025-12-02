"""
URL configuration for accounts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView, UserViewSet

router = DefaultRouter()
#  /api/auth/users/` — Admin-only create user 
router.register(r'users', UserViewSet, basename='user')

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User management endpoints
    path('', include(router.urls)),
]
