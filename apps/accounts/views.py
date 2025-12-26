"""
Views for user authentication and management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.common.response import (
    success_response,
    error_response,
    validation_error_response,
    created_response
)
from apps.common.viewsets import BaseModelViewSet
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    JobTitleSerializer,
    DepartmentSerializer,
    CourierSerializer
)
from .models import JobTitle, Department, Courier

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login endpoint
    Returns JWT tokens and user information
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Wrap the JWT response into our success_response format"""
        try:
            response = super().post(request, *args, **kwargs)
            return success_response(data=response.data, message='Login successful', status_code=response.status_code)
        except Exception as e:
            return error_response(
                message='Invalid email or password',
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class UserViewSet(BaseModelViewSet):
    """
    ViewSet for user management
    - Only admins can create, update, delete users
    - Users can view their own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        - create, update, destroy: Admin only
        - list: Admin only
        - retrieve, me, change_password: Authenticated users
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """
        Admin sees all users
        Regular users see only themselves
        """
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return success_response(data=serializer.data, message='Profile retrieved successfully')
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change current user's password"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        if not user.check_password(serializer.validated_data['old_password']):
            return validation_error_response(
                errors={'old_password': ['Wrong password']},
                message='Password verification failed'
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return success_response(message='Password changed successfully')
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """Activate a user account (admin only)"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return success_response(
            data={'email': user.email, 'is_active': user.is_active},
            message=f'User {user.email} activated successfully'
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate a user account (admin only)"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return success_response(
            data={'email': user.email, 'is_active': user.is_active},
            message=f'User {user.email} deactivated successfully'
        )


class JobTitleViewSet(BaseModelViewSet):
    """
    ViewSet for JobTitle management
    - List all job titles
    - Create, update, delete job titles (admin only)
    """
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """
        - list, retrieve: Authenticated users
        - create, update, destroy: Admin only
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        dept = self.request.query_params.get('department') if hasattr(self, 'request') else None
        if dept:
            return qs.filter(department_id=dept)
        return qs


class DepartmentViewSet(BaseModelViewSet):
    """ViewSet for Department management"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


# ==================== COURIER VIEWSET ====================

class CourierViewSet(BaseModelViewSet):
    """
    ViewSet for Courier CRUD operations
    """
    queryset = Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'courier_id'
    
    def get_permissions(self):
        """
        Only SUPERADMIN and ADMIN can create, update, delete
        All authenticated users can view
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        List all couriers with optional filtering
        """
        queryset = self.get_queryset()
        
        # Search functionality
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(courier_name__icontains=search) |
                Q(courier_code__icontains=search) |
                Q(contact_person__icontains=search)
            )
        
        # Filter by type
        courier_type = request.query_params.get('type', None)
        if courier_type and courier_type != 'ALL':
            queryset = queryset.filter(type=courier_type)
        
        # Filter by status
        courier_status = request.query_params.get('status', None)
        if courier_status and courier_status != 'ALL':
            queryset = queryset.filter(status=courier_status)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return success_response(
            data={
                'results': serializer.data,
                'count': queryset.count()
            },
            message='Couriers retrieved successfully'
        )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new courier
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return created_response(
                data=serializer.data,
                message='Courier created successfully'
            )
        
        return error_response(
            message='Validation error',
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single courier
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return success_response(
            data=serializer.data,
            message='Courier retrieved successfully'
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update a courier (full update)
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message='Courier updated successfully'
            )
        
        return error_response(
            message='Validation error',
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update of a courier
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a courier
        """
        instance = self.get_object()
        courier_name = instance.courier_name
        instance.delete()
        
        return success_response(
            message=f'Courier "{courier_name}" deleted successfully'
        )


from rest_framework.permissions import BasePermission


class IsAdminOrSuperAdmin(BasePermission):
    """
    Custom permission to only allow SUPERADMIN or ADMIN users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               hasattr(request.user, 'role') and \
               request.user.role in ['SUPERADMIN', 'ADMIN']