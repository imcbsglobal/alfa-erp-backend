"""
Custom exception handler for REST API.
Provides consistent error response format across the application.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error format.
    
    Returns:
        Response with format:
        {
            "error": "error_type",
            "message": "Error message",
            "details": {...}  # Optional
        }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle Django's Http404
    if isinstance(exc, Http404):
        return Response({
            'error': 'not_found',
            'message': 'Resource not found',
            'details': str(exc)
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle Django's ValidationError
    if isinstance(exc, ValidationError):
        return Response({
            'error': 'validation_error',
            'message': 'Validation failed',
            'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # If response is None, return generic error
    if response is None:
        return Response({
            'error': 'internal_server_error',
            'message': 'An unexpected error occurred',
            'details': str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Customize the response format
    custom_response = {
        'error': exc.__class__.__name__,
        'message': str(exc),
    }
    
    # Add details if available
    if hasattr(response, 'data') and response.data:
        custom_response['details'] = response.data
    
    response.data = custom_response
    
    return response
