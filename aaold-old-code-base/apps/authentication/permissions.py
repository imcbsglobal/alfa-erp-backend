"""
Permission classes and decorators for RBAC.
"""
from functools import wraps
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied


class HasRole(BasePermission):
    """
    Permission class to check if user has a specific role.
    Usage in views: permission_classes = [HasRole]
    Set required_role attribute in the view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        
        # Check if view has required_role attribute
        required_role = getattr(view, 'required_role', None)
        if required_role:
            return request.user.has_role(required_role)
        
        return True


class HasAnyRole(BasePermission):
    """
    Permission class to check if user has any of the specified roles.
    Usage in views: permission_classes = [HasAnyRole]
    Set required_roles attribute (list) in the view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        
        # Check if view has required_roles attribute
        required_roles = getattr(view, 'required_roles', None)
        if required_roles:
            return request.user.has_any_role(required_roles)
        
        return True


class HasAllRoles(BasePermission):
    """
    Permission class to check if user has all of the specified roles.
    Usage in views: permission_classes = [HasAllRoles]
    Set required_roles attribute (list) in the view.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers always have permission
        if request.user.is_superuser:
            return True
        
        # Check if view has required_roles attribute
        required_roles = getattr(view, 'required_roles', None)
        if required_roles:
            return request.user.has_all_roles(required_roles)
        
        return True


def require_role(role_code):
    """
    Decorator to require a specific role for a view function.
    
    Usage:
        @require_role('ADMIN')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied('Authentication required.')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.has_role(role_code):
                raise PermissionDenied(f'Role "{role_code}" required.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_any_role(*role_codes):
    """
    Decorator to require any of the specified roles for a view function.
    
    Usage:
        @require_any_role('ADMIN', 'MANAGER')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied('Authentication required.')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.has_any_role(role_codes):
                raise PermissionDenied(f'One of roles {role_codes} required.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_all_roles(*role_codes):
    """
    Decorator to require all of the specified roles for a view function.
    
    Usage:
        @require_all_roles('ADMIN', 'FINANCE')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied('Authentication required.')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if not request.user.has_all_roles(role_codes):
                raise PermissionDenied(f'All roles {role_codes} required.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission to only allow owners of an object to edit it.
    Assumes the model has a 'created_by' field.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.created_by == request.user
