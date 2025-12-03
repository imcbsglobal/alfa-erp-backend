"""
Views for Access Control - Direct User-to-Menu Assignment
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.common.response import success_response, error_response
from .models import UserMenu, MenuItem
from .serializers import (
    MenuItemSerializer, 
    UserMenuSerializer,
    AssignMenuSerializer,
    UnassignMenuSerializer
)

User = get_user_model()


class UserMenuView(APIView):
    """
    Get menus for the authenticated user (direct assignment, no roles)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Return user's menu structure"""
        user = request.user
        
        # Get menu structure directly from user's assigned menus
        menu_structure = UserMenu.get_user_menu_structure(user)
        
        return success_response(
            data={
                'menus': menu_structure,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.get_full_name()
                }
            },
            message='User menus retrieved successfully'
        )


class AllMenusView(APIView):
    """
    Get all available menus (for admin to see what can be assigned)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """Return all menu items in hierarchical structure"""
        # Get root menus (those without parent)
        root_menus = MenuItem.objects.filter(parent=None, is_active=True).order_by('order')
        serializer = MenuItemSerializer(root_menus, many=True)
        
        return success_response(
            data={'menus': serializer.data},
            message='All menus retrieved successfully'
        )


class AssignMenusView(APIView):
    """
    Assign menus to a user (Admin only)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Assign multiple menus to a user"""
        serializer = AssignMenuSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Validation failed',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data['user_id']
        menu_ids = serializer.validated_data['menu_ids']
        
        try:
            user = User.objects.get(id=user_id)
            assigned_by = request.user
            
            assigned_menus = []
            skipped_menus = []
            
            with transaction.atomic():
                for menu_id in menu_ids:
                    menu = MenuItem.objects.get(id=menu_id)
                    
                    # Check if already assigned
                    if UserMenu.objects.filter(user=user, menu=menu).exists():
                        skipped_menus.append({
                            'id': str(menu.id),
                            'name': menu.name,
                            'reason': 'Already assigned'
                        })
                        continue
                    
                    # Create new assignment
                    user_menu = UserMenu.objects.create(
                        user=user,
                        menu=menu,
                        assigned_by=assigned_by,
                        is_active=True
                    )
                    assigned_menus.append({
                        'id': str(user_menu.id),
                        'menu_id': str(menu.id),
                        'menu_name': menu.name,
                        'menu_code': menu.code
                    })
            
            return success_response(
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'full_name': user.get_full_name()
                    },
                    'assigned': assigned_menus,
                    'skipped': skipped_menus,
                    'total_assigned': len(assigned_menus),
                    'total_skipped': len(skipped_menus)
                },
                message=f'Successfully assigned {len(assigned_menus)} menu(s) to {user.email}',
                status_code=status.HTTP_201_CREATED
            )
            
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except MenuItem.DoesNotExist:
            return error_response(
                message='One or more menus not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to assign menus',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnassignMenusView(APIView):
    """
    Unassign menus from a user (Admin only)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Unassign multiple menus from a user"""
        serializer = UnassignMenuSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                message='Validation failed',
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = serializer.validated_data['user_id']
        menu_ids = serializer.validated_data['menu_ids']
        
        try:
            user = User.objects.get(id=user_id)
            
            unassigned_menus = []
            not_found_menus = []
            
            with transaction.atomic():
                for menu_id in menu_ids:
                    try:
                        user_menu = UserMenu.objects.get(user=user, menu_id=menu_id)
                        menu_name = user_menu.menu.name
                        user_menu.delete()
                        
                        unassigned_menus.append({
                            'menu_id': str(menu_id),
                            'menu_name': menu_name
                        })
                    except UserMenu.DoesNotExist:
                        not_found_menus.append({
                            'menu_id': str(menu_id),
                            'reason': 'Not assigned to user'
                        })
            
            return success_response(
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'full_name': user.get_full_name()
                    },
                    'unassigned': unassigned_menus,
                    'not_found': not_found_menus,
                    'total_unassigned': len(unassigned_menus),
                    'total_not_found': len(not_found_menus)
                },
                message=f'Successfully unassigned {len(unassigned_menus)} menu(s) from {user.email}'
            )
            
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to unassign menus',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserMenuAssignmentsView(APIView):
    """
    Get all menu assignments for a specific user (Admin only)
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, user_id):
        """Get all menus assigned to a specific user"""
        try:
            user = User.objects.get(id=user_id)
            
            # Get user's assigned menus
            user_menus = UserMenu.objects.filter(user=user, is_active=True).select_related('menu', 'assigned_by')
            serializer = UserMenuSerializer(user_menus, many=True)
            
            # Get menu structure
            menu_structure = UserMenu.get_user_menu_structure(user)
            
            return success_response(
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'full_name': user.get_full_name()
                    },
                    'assignments': serializer.data,
                    'menu_structure': menu_structure,
                    'total_menus': user_menus.count()
                },
                message='User menu assignments retrieved successfully'
            )
            
        except User.DoesNotExist:
            return error_response(
                message='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                message='Failed to retrieve menu assignments',
                errors={'detail': str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
