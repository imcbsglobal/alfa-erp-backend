# apps/common/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import DeveloperSettings
from .serializers import DeveloperSettingsSerializer


class DeveloperSettingsView(APIView):
    """
    GET /api/common/developer-settings/
    Retrieve current developer settings (available to all authenticated users)
    
    PUT /api/common/developer-settings/
    Update developer settings (SUPERADMIN only)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current developer settings - available to all users"""
        settings = DeveloperSettings.get_settings()
        serializer = DeveloperSettingsSerializer(settings)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def put(self, request):
        """Update developer settings - SUPERADMIN only"""
        # Check if user is SUPERADMIN
        if request.user.role != 'SUPERADMIN':
            return Response({
                'success': False,
                'message': 'Only SUPERADMIN can update developer settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        settings = DeveloperSettings.get_settings()
        serializer = DeveloperSettingsSerializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(updated_by=request.user.email)
            return Response({
                'success': True,
                'message': 'Developer settings updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
