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


class AssignMenuSerializer(serializers.Serializer):
    """Serializer for syncing user's menu assignments"""
    user_id = serializers.UUIDField(required=True)
    menu_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=True,
        allow_empty=True,
        help_text="Complete list of menu IDs that should be assigned to the user. Any existing assignments not in this list will be removed."
    )
    
    def validate_user_id(self, value):
        """Validate user exists"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found")
        return value
    
    def validate_menu_ids(self, value):
        """Validate all menu IDs exist"""
        if not value:  # Empty list is valid (removes all menus)
            return value
            
        existing_menus = MenuItem.objects.filter(id__in=value).values_list('id', flat=True)
        existing_menus = set(str(menu_id) for menu_id in existing_menus)
        requested_menus = set(str(menu_id) for menu_id in value)
        
        invalid_menus = requested_menus - existing_menus
        if invalid_menus:
            raise serializers.ValidationError(
                f"Invalid menu IDs: {', '.join(invalid_menus)}"
            )
        return value
