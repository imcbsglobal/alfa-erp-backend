"""
Views for authentication and user management.
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import logout
from datetime import datetime, timedelta

from .models import User, Role, UserSession
from .serializers import (
    LoginSerializer, UserSerializer, UserCreateSerializer,
    ChangePasswordSerializer, RoleSerializer, UserSessionSerializer
)
from .permissions import HasRole, HasAnyRole
from apps.common.mixins import ResponseMixin, UserTrackingMixin
from apps.common.utils import get_client_ip


class LoginView(generics.GenericAPIView, ResponseMixin):
    """
    User login view.
    Returns JWT tokens, user information, and roles for frontend navigation control.
    
    POST /api/auth/login/
    {
        "username": "john_doe",
        "password": "password123"
    }
    
    Response:
    {
        "success": true,
        "message": "Login successful",
        "data": {
            "user": {...},
            "tokens": {
                "access": "...",
                "refresh": "..."
            },
            "roles": ["ADMIN", "MANAGER"],
            "permissions": {...}
        }
    }
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            data = serializer.validated_data
            user = User.objects.get(username=request.data.get('username'))
            
            # Update last login IP
            user.last_login_ip = get_client_ip(request)
            user.failed_login_attempts = 0
            user.save(update_fields=['last_login_ip', 'failed_login_attempts'])
            
            # Create session record
            UserSession.objects.create(
                user=user,
                token=data['tokens']['access'],
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=datetime.now() + timedelta(hours=24)
            )
            
            return self.success_response(
                data={
                    'user': data['user'],
                    'tokens': data['tokens'],
                    'roles': data['roles'],  # For frontend navigation
                    'permissions': data['permissions']  # For fine-grained control
                },
                message='Login successful'
            )
        
        # Increment failed login attempts
        username = request.data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                user.failed_login_attempts += 1
                user.save(update_fields=['failed_login_attempts'])
            except User.DoesNotExist:
                pass
        
        return self.error_response(
            message='Invalid credentials',
            errors=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(generics.GenericAPIView, ResponseMixin):
    """
    User logout view.
    Blacklists the refresh token and deactivates the session.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Deactivate user sessions
            UserSession.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            logout(request)
            
            return self.success_response(message='Logout successful')
        except Exception as e:
            return self.error_response(
                message='Logout failed',
                errors=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView, ResponseMixin):
    """
    User registration view.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]  # Change to HasRole for protected registration
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            
            return self.success_response(
                data=user_data,
                message='User registered successfully',
                status_code=status.HTTP_201_CREATED
            )
        
        return self.error_response(
            message='Registration failed',
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet, ResponseMixin, UserTrackingMixin):
    """
    ViewSet for managing users.
    Provides CRUD operations for users with role-based access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on user role."""
        queryset = super().get_queryset()
        
        # Non-superusers can only see active users
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile.
        GET /api/auth/users/me/
        """
        serializer = self.get_serializer(request.user)
        return self.success_response(data=serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Update current user profile.
        PUT/PATCH /api/auth/users/update_profile/
        """
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message='Profile updated successfully'
            )
        
        return self.error_response(
            message='Update failed',
            errors=serializer.errors
        )
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password.
        POST /api/auth/users/change_password/
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            
            return self.success_response(message='Password changed successfully')
        
        return self.error_response(
            message='Password change failed',
            errors=serializer.errors
        )
    
    @action(detail=True, methods=['post'])
    def assign_roles(self, request, pk=None):
        """
        Assign roles to a user.
        POST /api/auth/users/{id}/assign_roles/
        Body: {"role_ids": [1, 2, 3]}
        """
        user = self.get_object()
        role_ids = request.data.get('role_ids', [])
        
        if not role_ids:
            return self.error_response(message='No roles provided')
        
        roles = Role.objects.filter(id__in=role_ids)
        user.roles.set(roles)
        
        serializer = self.get_serializer(user)
        return self.success_response(
            data=serializer.data,
            message='Roles assigned successfully'
        )


class RoleViewSet(viewsets.ModelViewSet, ResponseMixin):
    """
    ViewSet for managing roles.
    Provides CRUD operations for roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ['ADMIN', 'SUPERADMIN']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active roles.
        GET /api/auth/roles/active/
        """
        roles = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(roles, many=True)
        return self.success_response(data=serializer.data)


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet, ResponseMixin):
    """
    ViewSet for viewing user sessions.
    """
    queryset = UserSession.objects.all()
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own sessions."""
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active sessions for current user."""
        sessions = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(sessions, many=True)
        return self.success_response(data=serializer.data)
