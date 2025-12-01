"""
HRM views.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Department management."""
    queryset = Department.objects.filter(is_deleted=False)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
