"""
Inventory views.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product management."""
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
