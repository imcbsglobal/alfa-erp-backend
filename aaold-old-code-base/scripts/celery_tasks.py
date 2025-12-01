"""
Example Celery task for sending emails.
Add your async tasks here.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list):
    """
    Send email asynchronously.
    
    Args:
        subject: Email subject
        message: Email body
        recipient_list: List of recipient email addresses
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_list}")
        return f"Email sent to {len(recipient_list)} recipients"
    except Exception as exc:
        logger.error(f"Error sending email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_expired_sessions():
    """
    Clean up expired user sessions.
    Run this task periodically (e.g., daily).
    """
    from apps.authentication.models import UserSession
    from django.utils import timezone
    
    expired_count = UserSession.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True
    ).update(is_active=False)
    
    logger.info(f"Deactivated {expired_count} expired sessions")
    return f"Deactivated {expired_count} sessions"


@shared_task
def generate_daily_report():
    """
    Generate daily reports.
    Run this task daily at midnight.
    """
    # Add your report generation logic here
    logger.info("Daily report generated")
    return "Daily report generated successfully"


@shared_task
def check_low_inventory():
    """
    Check for products below reorder level.
    Send alerts to relevant users.
    """
    from apps.inventory.models import Product
    
    low_stock = Product.objects.filter(
        stock_quantity__lte=models.F('reorder_level'),
        is_active=True,
        is_deleted=False
    )
    
    if low_stock.exists():
        # Send notification
        logger.warning(f"Low stock alert: {low_stock.count()} products")
        # Add notification logic here
    
    return f"Checked inventory: {low_stock.count()} items need reorder"
