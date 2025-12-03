"""
Serializers for Access Control - Direct User-to-Menu Assignment
"""
from rest_framework import serializers
from .models import MenuItem, UserMenu


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for menu items with children"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'code', 'icon', 'url', 'order', 'children']
    
    def get_children(self, obj):
        """Get child menu items"""
        children = obj.get_children()
        if children.exists():
            return MenuItemSerializer(children, many=True).data
        return []


class UserMenuSerializer(serializers.ModelSerializer):
    """Serializer for user menu assignments"""
    menu_name = serializers.CharField(source='menu.name', read_only=True)
    menu_code = serializers.CharField(source='menu.code', read_only=True)
    menu_url = serializers.CharField(source='menu.url', read_only=True)
    assigned_by_email = serializers.CharField(source='assigned_by.email', read_only=True)
    
    class Meta:
        model = UserMenu
        fields = [
            'id', 'menu', 'menu_name', 'menu_code', 'menu_url', 
            'is_active', 'assigned_by_email', 'assigned_at'
        ]
        read_only_fields = ['assigned_at']
