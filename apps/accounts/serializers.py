"""
Serializers for user authentication and management
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer
    Returns user information, tokens, and menu structure
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom user data to the response
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'name': self.user.name,
            'avatar': (self.user.avatar.url if self.user.avatar else None),
            'role': self.user.role,
            'department': self.user.department.name if self.user.department else None,
            'department_id': str(self.user.department.id) if self.user.department else None,
            'job_title': {
                'id': str(self.user.job_title.id),
                'title': self.user.job_title.title
            } if self.user.job_title else None,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }

        # Include Django groups (if any) for backward compatibility
        data['user']['groups'] = list(self.user.groups.values_list('name', flat=True))
        
        # Add menu structure based on user's directly assigned menus (no roles)
        try:
            from apps.accesscontrol.models import UserMenu, MenuItem

            # If user is admin/staff or has ADMIN/SUPERADMIN role, return full menu tree
            user_role = getattr(self.user, 'role', 'USER')
            is_admin_user = bool(self.user.is_staff or self.user.is_superuser or user_role in ['ADMIN', 'SUPERADMIN'])

            if is_admin_user:
                menu_structure = MenuItem.get_all_menu_structure()
            else:
                # Get menu structure directly from user's assigned menus
                menu_structure = UserMenu.get_user_menu_structure(self.user)
            data['menus'] = menu_structure
                
        except Exception as e:
            # Fallback if accesscontrol app is not available
            data['menus'] = []
        
        return data


class JobTitleSerializer(serializers.ModelSerializer):
    """Serializer for JobTitle model"""
    
    class Meta:
        from apps.accounts.models import JobTitle
        model = JobTitle
        fields = ['id', 'title', 'description', 'is_active', 'department_id', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    from apps.accounts.models import Department

    department = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        source='department',
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model with nested job titles"""
    job_titles = JobTitleSerializer(many=True, read_only=True)
    
    class Meta:
        from apps.accounts.models import Department
        model = Department
        fields = ['id', 'name', 'description', 'is_active', 'job_titles', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# class DepartmentListSerializer(serializers.ModelSerializer):
#     """Lightweight Department serializer for lists with job_titles array"""
#     job_titles = serializers.SerializerMethodField()
    
#     class Meta:
#         from apps.accounts.models import Department
#         model = Department
#         fields = ['id', 'name', 'description', 'is_active', 'job_titles']
    
#     def get_job_titles(self, obj):
#         """Return array of job titles under this department"""
#         return [{
#             'id': str(jt.id),
#             'title': jt.title,
#             'description': jt.description,
#             'is_active': jt.is_active
#         } for jt in obj.job_titles.filter(is_active=True)]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    password = serializers.CharField(write_only=True, required=False)
    # avatar = serializers.ImageField(required=False, allow_null=True)
    job_title_name = serializers.CharField(source='job_title.title', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    from apps.accounts.models import Department
    department_id = serializers.PrimaryKeyRelatedField(source='department', queryset=Department.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name',
            'phone', 'avatar', 'role', 'department', 'department_id',
            'job_title', 'job_title_name', 'is_active', 'is_staff', 'date_joined',
            'last_login', 'password', 'created_by_name'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'job_title_name', 'created_by_name']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name()
        return None

    def get_department(self, obj):
        if obj.department:
            return obj.department.name
        return None
    
    def create(self, validated_data):
        """Create a new user (admin only)"""
        password = validated_data.pop('password', None)
        # If a request context with user (admin) is provided, set created_by
        created_by = None
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            created_by = request.user

        user = User.objects.create(created_by=created_by, **validated_data)
        
        if password:
            user.set_password(password)
            user.save()

        # if avatar and hasattr(avatar, "name") and avatar.name:
        #     user.avatar = avatar

        
        return user
    
    def update(self, instance, validated_data):
        """Update user details"""
        password = validated_data.pop('password', None)
        avatar = validated_data.pop('avatar', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        if avatar is not None:
            instance.avatar = avatar
        
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user lists"""
    
    job_title_name = serializers.CharField(source='job_title.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    department = serializers.CharField(source='department.name', read_only=True)
    department_id = serializers.UUIDField(source='department.id', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'department', 'department_id', 'job_title_name', 'is_active', 'is_staff','created_by_name','avatar']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        # Add custom password validation if needed
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value
