"""
User and Role models with RBAC support.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TimeStampedModel, ActiveModel


class UserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    """
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user with email and password.
        """
        if not username:
            raise ValueError(_('The Username field must be set'))
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username, email, password, **extra_fields)


class Role(TimeStampedModel, ActiveModel):
    """
    Role model for RBAC.
    Represents different roles that users can have (e.g., Admin, Manager, Employee).
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Role Name'),
        help_text=_('Unique name for the role')
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Role Code'),
        help_text=_('Unique code identifier for the role (e.g., ADMIN, MANAGER)')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Description of the role and its permissions')
    )
    permissions = models.JSONField(
        default=dict,
        verbose_name=_('Permissions'),
        help_text=_('JSON object containing role permissions')
    )
    
    class Meta:
        db_table = 'auth_roles'
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, ActiveModel):
    """
    Custom User model with RBAC support.
    Users can have multiple roles for flexible access control.
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_('Username'),
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email Address'),
        help_text=_('User email address')
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('First Name')
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_('Last Name')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone Number')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name=_('Avatar')
    )
    
    # Role-based access control
    roles = models.ManyToManyField(
        Role,
        related_name='users',
        blank=True,
        verbose_name=_('Roles'),
        help_text=_('Roles assigned to this user')
    )
    
    # Django admin permissions
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Staff Status'),
        help_text=_('Designates whether the user can log into admin site.')
    )
    
    # Additional user metadata
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Last Login IP')
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name=_('Failed Login Attempts')
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'auth_users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """Return the short name of the user."""
        return self.first_name or self.username
    
    def has_role(self, role_code):
        """
        Check if user has a specific role.
        
        Args:
            role_code: The role code to check (e.g., 'ADMIN', 'MANAGER')
            
        Returns:
            Boolean indicating if user has the role
        """
        return self.roles.filter(code=role_code, is_active=True).exists()
    
    def has_any_role(self, role_codes):
        """
        Check if user has any of the specified roles.
        
        Args:
            role_codes: List of role codes to check
            
        Returns:
            Boolean indicating if user has any of the roles
        """
        return self.roles.filter(code__in=role_codes, is_active=True).exists()
    
    def has_all_roles(self, role_codes):
        """
        Check if user has all of the specified roles.
        
        Args:
            role_codes: List of role codes to check
            
        Returns:
            Boolean indicating if user has all the roles
        """
        return self.roles.filter(code__in=role_codes, is_active=True).count() == len(role_codes)
    
    def get_role_codes(self):
        """
        Get list of role codes assigned to the user.
        
        Returns:
            List of role codes
        """
        return list(self.roles.filter(is_active=True).values_list('code', flat=True))
    
    def get_role_names(self):
        """
        Get list of role names assigned to the user.
        
        Returns:
            List of role names
        """
        return list(self.roles.filter(is_active=True).values_list('name', flat=True))


class UserSession(TimeStampedModel):
    """
    Track user login sessions for security and audit purposes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name=_('User')
    )
    token = models.CharField(
        max_length=500,
        verbose_name=_('JWT Token'),
        help_text=_('JWT access token')
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP Address')
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    expires_at = models.DateTimeField(
        verbose_name=_('Expires At')
    )
    
    class Meta:
        db_table = 'auth_user_sessions'
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"
