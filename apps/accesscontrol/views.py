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
    AssignMenuSerializer
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
    Assign user's menu assignments (Admin only)
    Frontend sends complete list of selected menus, backend syncs to match
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        """Assign user's menu assignments to match the provided list"""
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
            
            with transaction.atomic():
                # Get current assignments
                current_assignments = UserMenu.objects.filter(user=user).select_related('menu')
                current_menu_ids = set(str(um.menu.id) for um in current_assignments)
                requested_menu_ids = set(str(mid) for mid in menu_ids)
                
                # Determine what to add and what to remove
                to_add = requested_menu_ids - current_menu_ids
                to_remove = current_menu_ids - requested_menu_ids
                
                # Remove assignments not in the new list
                removed_count = 0
                if to_remove:
                    removed_count = UserMenu.objects.filter(
                        user=user,
                        menu_id__in=to_remove
                    ).delete()[0]
                
                # Add new assignments
                added_menus = []
                for menu_id in to_add:
                    menu = MenuItem.objects.get(id=menu_id)
                    user_menu = UserMenu.objects.create(
                        user=user,
                        menu=menu,
                        assigned_by=assigned_by,
                        is_active=True
                    )
                    added_menus.append({
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
                    'added': added_menus,
                    'removed_count': removed_count,
                    'total_added': len(added_menus),
                    'total_menus': len(menu_ids)
                },
                message=f'Successfully synced menus for {user.email}. Added {len(added_menus)}, removed {removed_count}',
                status_code=status.HTTP_200_OK
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
                message='Failed to sync menus',
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
