"""
Custom User model for ALFA ERP Backend
Users can only be created by admin, no self-registration
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Department(models.Model):
    """Department model for organizing job titles"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    """Job Title model for user positions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150)
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='job_titles'
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_titles'
        verbose_name = 'Job Title'
        verbose_name_plural = 'Job Titles'
        ordering = ['department', 'title']
        unique_together = ('department', 'title')

    def __str__(self):
        return self.title


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Email address is required')

        email = self.normalize_email(email)

        if "role" not in extra_fields:
            extra_fields["role"] = User.Role.USER

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.SUPERADMIN)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model using email as the username field"""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        USER = 'USER', 'User'
        SUPERADMIN = 'SUPERADMIN', 'Super Admin'
        # Operational roles for warehouse / logistics
        PICKER = 'PICKER', 'Picker'  # Handles picking items from warehouse
        PACKER = 'PACKER', 'Packer'  # Handles packing picked items
        DRIVER = 'DRIVER', 'Driver'  # Handles delivery / transport
        BILLING = 'BILLING', 'Billing'  # Handles invoicing / billing tasks
        

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=150, blank=True)

    # Single role field
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text='Assigned role of the user'
    )
    

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
 
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    # first_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name or self.email

    def get_short_name(self):
        return self.name or self.email.split('@')[0]

    def has_role(self, role):
        return self.role == role

    def has_any_role(self, *roles):
        """Return True if user role matches any of the provided roles.

        Usage: `user.has_any_role(User.Role.PACKER, User.Role.PICKER)`
        """
        return self.role in roles

    def is_admin_or_superadmin(self):
        """Check if user is admin, superadmin, or Django staff/superuser."""
        return (
            self.is_staff or 
            self.is_superuser or 
            self.role in [User.Role.ADMIN, User.Role.SUPERADMIN]
        )
