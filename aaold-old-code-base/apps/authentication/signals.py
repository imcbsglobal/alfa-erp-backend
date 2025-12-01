"""
Signals for authentication app.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# Example signal handlers (add more as needed)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#     """
#     Create user profile when a new user is created.
#     """
#     if created:
#         logger.info(f"New user created: {instance.username}")
#         # Add logic to create related profiles or send welcome emails
