# apps/common/serializers.py
from rest_framework import serializers
from .models import DeveloperSettings


class DeveloperSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeveloperSettings
        fields = ['enable_manual_picking_completion', 'updated_at', 'updated_by']
        read_only_fields = ['updated_at']
