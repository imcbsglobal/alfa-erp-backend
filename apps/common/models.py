# apps/common/models.py
from django.db import models


class DeveloperSettings(models.Model):
    """
    Singleton model to store developer/feature toggle settings.
    Only one instance should exist in the database.
    """
    # Feature Toggles
    enable_manual_picking_completion = models.BooleanField(
        default=False,
        help_text="When enabled, picked invoices remain visible in Picking Management with a Complete button"
    )
    
    enable_bulk_picking = models.BooleanField(
        default=False,
        help_text="When enabled, allows bulk picking of multiple invoices at once"
    )
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Developer Settings"
        verbose_name_plural = "Developer Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion"""
        pass
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Developer Settings"
