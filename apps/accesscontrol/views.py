"""
Views for Access Control - Direct User-to-Menu Assignment
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.common.response import success_response
from .models import UserMenu


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
