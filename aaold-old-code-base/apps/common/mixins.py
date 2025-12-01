"""
Custom mixins for views and serializers.
"""
from rest_framework import status
from rest_framework.response import Response


class ResponseMixin:
    """
    Mixin to provide standardized response format for API views.
    """
    
    def success_response(self, data=None, message='Success', status_code=status.HTTP_200_OK):
        """Return a successful response."""
        return Response({
            'success': True,
            'message': message,
            'data': data
        }, status=status_code)
    
    def error_response(self, message='Error', errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Return an error response."""
        response_data = {
            'success': False,
            'message': message,
        }
        if errors:
            response_data['errors'] = errors
        return Response(response_data, status=status_code)


class UserTrackingMixin:
    """
    Mixin to automatically set created_by and updated_by fields.
    Use in ViewSets or Views that create/update models with user tracking.
    """
    
    def perform_create(self, serializer):
        """Set the created_by field when creating an object."""
        if hasattr(serializer.Meta.model, 'created_by'):
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating an object."""
        if hasattr(serializer.Meta.model, 'updated_by'):
            serializer.save(updated_by=self.request.user)
        else:
            serializer.save()
