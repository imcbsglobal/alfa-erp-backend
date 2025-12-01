"""
Common utility functions and helpers.
"""
import random
import string
from typing import Any, Dict
from django.core.paginator import Paginator
from django.db.models import QuerySet


def generate_random_string(length: int = 10) -> str:
    """
    Generate a random alphanumeric string of specified length.
    
    Args:
        length: Length of the string to generate
        
    Returns:
        Random alphanumeric string
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def generate_unique_code(prefix: str = '', length: int = 8) -> str:
    """
    Generate a unique code with optional prefix.
    
    Args:
        prefix: Prefix to add to the code
        length: Length of the random part
        
    Returns:
        Unique code string
    """
    random_part = generate_random_string(length)
    return f"{prefix}{random_part}".upper() if prefix else random_part.upper()


def paginate_queryset(queryset: QuerySet, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """
    Paginate a queryset and return structured data.
    
    Args:
        queryset: Django QuerySet to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page
        
    Returns:
        Dictionary with pagination data
    """
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    return {
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
        'page_size': page_size,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'results': list(page_obj.object_list)
    }


def format_response(success: bool = True, message: str = '', data: Any = None, 
                   errors: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """
    Format a standardized API response.
    
    Args:
        success: Whether the operation was successful
        message: Response message
        data: Response data
        errors: Error details if any
        status_code: HTTP status code
        
    Returns:
        Formatted response dictionary
    """
    response = {
        'success': success,
        'message': message,
        'status_code': status_code
    }
    
    if data is not None:
        response['data'] = data
    
    if errors is not None:
        response['errors'] = errors
    
    return response


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: Django request object
        
    Returns:
        Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
