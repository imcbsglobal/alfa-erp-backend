"""
Reusable response handlers for consistent API responses
"""
from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message=None, status_code=status.HTTP_200_OK, **kwargs):
    """
    Standard success response format
    
    Args:
        data: Response data (dict, list, or any serializable object)
        message: Success message (optional)
        status_code: HTTP status code (default: 200)
        **kwargs: Additional fields to include in response
    
    Returns:
        Response object with standardized format
    
    Example:
        return success_response(
            data={'user': user_data},
            message='User created successfully',
            status_code=status.HTTP_201_CREATED
        )
    """
    response_data = {
        'success': True,
        'status_code': status_code,
    }
    
    if message:
        response_data['message'] = message
    
    if data is not None:
        response_data['data'] = data
    
    # Add any additional fields
    response_data.update(kwargs)
    
    return Response(response_data, status=status_code)


def error_response(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
    """
    Standard error response format
    
    Args:
        message: Error message
        errors: Detailed error information (dict or list)
        status_code: HTTP status code (default: 400)
        **kwargs: Additional fields to include in response
    
    Returns:
        Response object with standardized error format
    
    Example:
        return error_response(
            message='Validation failed',
            errors={'email': ['This field is required']},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    """
    response_data = {
        'success': False,
        'status_code': status_code,
    }
    
    if message:
        response_data['message'] = message
    
    if errors is not None:
        response_data['errors'] = errors
    
    # Add any additional fields
    response_data.update(kwargs)
    
    return Response(response_data, status=status_code)


def paginated_response(data, message=None, status_code=status.HTTP_200_OK, **kwargs):
    """
    Standard paginated response format (for use with DRF pagination)
    
    Args:
        data: Paginated data (should contain 'results', 'count', 'next', 'previous')
        message: Success message (optional)
        status_code: HTTP status code (default: 200)
        **kwargs: Additional fields to include in response
    
    Returns:
        Response object with standardized paginated format
    
    Example:
        paginator = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginator, many=True)
        return paginated_response(
            data={
                'results': serializer.data,
                'count': self.paginator.count,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link(),
            }
        )
    """
    return success_response(data=data, message=message, status_code=status_code, **kwargs)


def created_response(data=None, message='Resource created successfully', **kwargs):
    """
    Shortcut for 201 Created response
    
    Example:
        return created_response(data={'id': user.id}, message='User created')
    """
    return success_response(data=data, message=message, status_code=status.HTTP_201_CREATED, **kwargs)


def no_content_response(message=None):
    """
    Shortcut for 204 No Content response
    
    Example:
        return no_content_response(message='Resource deleted')
    """
    return Response(
        {'success': True, 'message': message} if message else None,
        status=status.HTTP_204_NO_CONTENT
    )


def unauthorized_response(message='Authentication credentials were not provided or are invalid'):
    """
    Shortcut for 401 Unauthorized response
    
    Example:
        return unauthorized_response(message='Invalid token')
    """
    return error_response(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


def forbidden_response(message='You do not have permission to perform this action'):
    """
    Shortcut for 403 Forbidden response
    
    Example:
        return forbidden_response(message='Admin access required')
    """
    return error_response(message=message, status_code=status.HTTP_403_FORBIDDEN)


def not_found_response(message='Resource not found'):
    """
    Shortcut for 404 Not Found response
    
    Example:
        return not_found_response(message='User not found')
    """
    return error_response(message=message, status_code=status.HTTP_404_NOT_FOUND)


def validation_error_response(errors, message='Validation failed 11'):
    """
    Shortcut for validation error response (400)
    
    Example:
        return validation_error_response(
            errors={'email': ['Invalid email format']},
            message='Please correct the errors below'
        )
    """
    return error_response(message=message, errors=errors, status_code=status.HTTP_400_BAD_REQUEST)


def server_error_response(message='Internal server error occurred'):
    """
    Shortcut for 500 Internal Server Error response
    
    Example:
        return server_error_response(message='Database connection failed')
    """
    return error_response(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
