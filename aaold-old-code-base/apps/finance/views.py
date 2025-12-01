"""
Finance views.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.authentication.permissions import HasAnyRole
from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for Account management."""
    queryset = Account.objects.filter(is_deleted=False)
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, HasAnyRole]
    required_roles = ['ADMIN', 'FINANCE']
