"""
Base models for common functionality across the ERP system.
These abstract models provide common fields and behavior.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract model providing automatic created_at and updated_at timestamps.
    All models should inherit from this for audit trail.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At'),
        help_text=_('Timestamp when the record was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At'),
        help_text=_('Timestamp when the record was last updated')
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']


class UserTrackingModel(TimeStampedModel):
    """
    Abstract model providing user tracking for create and update operations.
    Tracks which user created and last modified the record.
    """
    created_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name=_('Created By'),
        help_text=_('User who created this record')
    )
    updated_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        verbose_name=_('Updated By'),
        help_text=_('User who last updated this record')
    )
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model providing soft delete functionality.
    Records are marked as deleted instead of being physically removed.
    """
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_('Is Deleted'),
        help_text=_('Indicates if the record has been soft deleted')
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Deleted At'),
        help_text=_('Timestamp when the record was deleted')
    )
    deleted_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        verbose_name=_('Deleted By'),
        help_text=_('User who deleted this record')
    )
    
    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """
    Abstract model providing active/inactive status.
    Useful for temporarily disabling records without deleting them.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Indicates if the record is active')
    )
    
    class Meta:
        abstract = True


class BaseModel(UserTrackingModel, SoftDeleteModel, ActiveModel):
    """
    Complete base model combining all common functionality.
    Provides timestamps, user tracking, soft delete, and active status.
    """
    class Meta:
        abstract = True
