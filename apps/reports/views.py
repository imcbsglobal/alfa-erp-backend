"""
Reports views.
Add your reporting endpoints here.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Get dashboard summary data.
    """
    # Add your reporting logic here
    data = {
        'total_users': 0,
        'total_products': 0,
        'total_customers': 0,
        'total_revenue': 0,
    }
    return Response(data, status=status.HTTP_200_OK)
