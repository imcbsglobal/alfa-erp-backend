"""
Serializers for authentication and user management.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role, UserSession


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with role information."""
    
    roles = RoleSerializer(many=True, read_only=True)
    role_codes = serializers.SerializerMethodField()
    role_names = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone', 
            'avatar', 'roles', 'role_codes', 'role_names', 'full_name',
            'is_active', 'is_staff', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_login', 'created_at', 'updated_at']
    
    def get_role_codes(self, obj):
        """Get list of role codes for the user."""
        return obj.get_role_codes()
    
    def get_role_names(self, obj):
        """Get list of role names for the user."""
        return obj.get_role_names()
    
    def get_full_name(self, obj):
        """Get full name of the user."""
        return obj.get_full_name()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role_ids'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Password fields didn\'t match.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create a new user with roles."""
        validated_data.pop('password_confirm')
        role_ids = validated_data.pop('role_ids', [])
        
        user = User.objects.create_user(**validated_data)
        
        # Assign roles
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids)
            user.roles.set(roles)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Returns JWT tokens and user information with roles.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """Authenticate user and return tokens with user data."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".',
                code='authorization'
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare user data with roles for frontend navigation
        user_data = UserSerializer(user).data
        
        attrs['user'] = user_data
        attrs['tokens'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        # Include roles explicitly for frontend navigation control
        attrs['roles'] = user.get_role_codes()
        attrs['permissions'] = self._get_user_permissions(user)
        
        return attrs
    
    def _get_user_permissions(self, user):
        """
        Aggregate all permissions from user's roles.
        Frontend can use this for fine-grained access control.
        """
        permissions = {}
        for role in user.roles.filter(is_active=True):
            if role.permissions:
                permissions.update(role.permissions)
        return permissions


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        write_only=True
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password_confirm': 'Password fields didn\'t match.'
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model."""
    
    user = serializers.StringRelatedField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user', 'ip_address', 'user_agent', 
            'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = fields
