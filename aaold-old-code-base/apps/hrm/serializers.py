"""
HRM serializers.
"""
from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    
    class Meta:
        model = Department
        fields = '__all__'
