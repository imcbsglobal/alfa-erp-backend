from functools import lru_cache

import requests
from django.conf import settings
from rest_framework import serializers
from .models import FollowUp, PaymentAlert


@lru_cache(maxsize=1)
def _fetch_area_map():
    url = getattr(
        settings,
        'ACC_SERVICEMASTER_API_URL',
        'https://alfasyncapi.imcbs.com/api/get-servicemaster/',
    )
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json().get('data', [])
        return {item['code']: item['name'] for item in data if item.get('code')}
    except Exception:
        return {}


@lru_cache(maxsize=1)
def _fetch_client_area_map():
    url = getattr(
        settings,
        'ACC_MASTER_API_URL',
        'https://alfasyncapi.imcbs.com/api/get-acc-master/',
    )
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json().get('data', [])
        return {
            str(item.get('code', '')).strip(): str(item.get('area', '')).strip()
            for item in data
            if item.get('code')
        }
    except Exception:
        return {}


def _resolve_area_display(value, client_code=None):
    text = (value or '').strip()

    # Keep consistent with tracker: prefer current area from AccMaster by client code.
    code = (client_code or '').strip()
    if code:
        area_code = _fetch_client_area_map().get(code)
        if area_code:
            return _fetch_area_map().get(area_code, area_code)

    if not text:
        return ''

    area_map = _fetch_area_map()
    return area_map.get(text, text)


class FollowUpSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    area_display = serializers.SerializerMethodField()
    next_followup_date = serializers.DateField(          # ← ADD
        required=False,
        allow_null=True,
        input_formats=['%Y-%m-%d', '%d-%m-%Y', 'iso-8601'],
    )

    class Meta:
        model  = FollowUp
        fields = [
            'id', 'client_code', 'client_name', 'agent', 'area', 'area_display',
            'outstanding_amount','promised_amount','channel', 'outcome', 'escalated_to', 'notes',
            'next_followup_date', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() or obj.created_by.username if obj.created_by else None

    def get_area_display(self, obj):
        return _resolve_area_display(obj.area, obj.client_code)

    def validate(self, attrs):
        outcome = attrs.get('outcome', getattr(self.instance, 'outcome', None))
        escalated_to = attrs.get('escalated_to', getattr(self.instance, 'escalated_to', ''))
        if outcome == 'ESCALATED' and not (escalated_to or '').strip():
            raise serializers.ValidationError({'escalated_to': 'This field is required when outcome is Escalated.'})
        return attrs

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PaymentAlertSerializer(serializers.ModelSerializer):
    resolved_by_name  = serializers.SerializerMethodField()
    activity_status   = serializers.SerializerMethodField()
    assigned_to_name  = serializers.SerializerMethodField()   # ← ADD
    area_display      = serializers.SerializerMethodField()

    class Meta:
        model  = PaymentAlert
        fields = [
            'id', 'client_code', 'client_name', 'agent', 'area', 'area_display',
            'outstanding_amount', 'oldest_due_days',
            'alert_type', 'severity', 'is_resolved',
            'resolved_at', 'resolved_by', 'resolved_by_name',
            'assigned_to', 'assigned_to_name',                 # ← ADD
            'activity_status', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_resolved_by_name(self, obj):
        return obj.resolved_by.get_full_name() or obj.resolved_by.username if obj.resolved_by else None

    def get_assigned_to_name(self, obj):                       # ← ADD
        return obj.assigned_to.get_full_name() or obj.assigned_to.username if obj.assigned_to else None

    def get_area_display(self, obj):
        return _resolve_area_display(obj.area, obj.client_code)

    def get_activity_status(self, obj):
        if obj.is_resolved:
            return 'RESOLVED'
        if getattr(obj, 'has_followup', False):
            return 'RESPONDED'
        return 'ACTIVE'