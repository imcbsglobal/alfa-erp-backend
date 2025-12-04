"""
Custom User model for ALFA ERP Backend
Users can only be created by admin, no self-registration
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('roles', [User.Role.ADMIN]) 
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model
    - Email as username field
    - Admin creates all users
    - No self-registration
    """
    
    # Role choices for access control
    class Role(models.TextChoices):
        #admin,superadmin,user
        ADMIN = 'ADMIN', 'Admin'
        
        STORE = 'STORE', 'Store'
        DELIVERY = 'DELIVERY', 'Delivery'
        PURCHASE = 'PURCHASE', 'Purchase'
        ACCOUNTS = 'ACCOUNTS', 'Accounts'
        VIEWER = 'VIEWER', 'Viewer'
    
    # User identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(
        verbose_name='Email Address',
        max_length=255,
        unique=True,
        db_index=True
    )
    
    # Role-based access control (multiple roles support)
    roles = ArrayField(
        models.CharField(max_length=20, choices=Role.choices),
        default=list,
        blank=True,
        help_text='List of roles assigned to the user for access control'
    )
    
    # Personal information
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    # Avatar / profile photo
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Profile photo (optional)'
    )
    
    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
    )
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.'
    )

    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        help_text='Admin who created this user'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between"""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user"""
        return self.first_name or self.email.split('@')[0]
    
    def has_role(self, role):
        """Check if user has a specific role"""
        return role in self.roles
    
    def has_any_role(self, *roles):
        """Check if user has any of the specified roles"""
        return any(role in self.roles for role in roles)
    
    def has_all_roles(self, *roles):
        """Check if user has all of the specified roles"""
        return all(role in self.roles for role in roles)
    
    @property
    def primary_role(self):
        """Return the first/primary role or VIEWER if no roles assigned"""
        return self.roles[0] if self.roles else self.Role.VIEWER
