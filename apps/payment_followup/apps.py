"""
apps/payment_followup/apps.py

Registers the signals so they fire automatically on every FollowUp save/delete.
"""

from django.apps import AppConfig


class PaymentFollowupConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payment_followup"

    def ready(self):
        import apps.payment_followup.signals  # noqa: F401 — registers receivers