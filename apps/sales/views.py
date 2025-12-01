"""
Sales views.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer management."""
    queryset = Customer.objects.filter(is_deleted=False)
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
