# apps/common/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import DeveloperSettings
from .serializers import DeveloperSettingsSerializer
from apps.accounts.models import Tray
from .serializers import TraySerializer


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
        try:
            settings = DeveloperSettings.get_settings()
            serializer = DeveloperSettingsSerializer(settings)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Exception as e:
            print(f"❌ Error fetching developer settings: {e}")
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'message': f'Error fetching settings: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """Update developer settings - SUPERADMIN only"""
        # Check if user is SUPERADMIN
        if request.user.role != 'SUPERADMIN':
            return Response({
                'success': False,
                'message': 'Only SUPERADMIN can update developer settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Debug logging
        print(f"🔍 Received data: {request.data}")
        
        settings = DeveloperSettings.get_settings()
        print(f"🔍 Current settings before update: enable_bulk_picking={settings.enable_bulk_picking}")
        
        serializer = DeveloperSettingsSerializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save(updated_by=request.user.email)
            print(f"✅ Settings saved: {serializer.data}")
            
            # Verify the save
            settings.refresh_from_db()
            print(f"🔍 Settings after refresh: enable_bulk_picking={settings.enable_bulk_picking}")
            
            return Response({
                'success': True,
                'message': 'Developer settings updated successfully',
                'data': serializer.data
            })
        
        print(f"❌ Validation errors: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class TrayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'tray_id'

    def get_queryset(self):
        qs = Tray.objects.all().order_by('-created_at')
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(tray_code__icontains=search)
        return qs

    def get_serializer_class(self):
        return TraySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'data': {'results': serializer.data}})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response({'success': False, 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({'success': True, 'message': 'Tray deleted successfully'})


