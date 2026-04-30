from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import FollowUp
from django.db import models


@receiver(post_save, sender=FollowUp)
@receiver(post_delete, sender=FollowUp)
def refresh_alerts_on_followup_change(sender, instance, **kwargs):
    from datetime import date, timedelta
    from django.contrib.auth import get_user_model
    from .models import PaymentAlert

    User = get_user_model()
    code  = instance.client_code
    today = date.today()
    week_end = today + timedelta(days=7)

    # ── Handle ESCALATED outcome — create a targeted alert ───────────
    if getattr(instance, 'outcome', None) == 'ESCALATED' and instance.escalated_to:
        search_term = instance.escalated_to.split()[0]

        # Find the user whose name matches escalated_to
        escalated_user = (
            User.objects.filter(is_active=True)
            .filter(
                models.Q(name__icontains=search_term) |
                models.Q(email__icontains=search_term)
            )
            .first()
        )

        # Upsert: one unresolved ESCALATED alert per client per assignee
        existing = PaymentAlert.objects.filter(
            client_code=code,
            alert_type='ESCALATED',
            is_resolved=False,
            assigned_to=escalated_user,
        ).first()

        if existing:
            existing.outstanding_amount = float(instance.outstanding_amount or 0)
            existing.client_name        = instance.client_name
            existing.agent              = instance.agent
            existing.area               = instance.area
            existing.severity           = 'HIGH'
            existing.save()
        else:
            PaymentAlert.objects.create(
                client_code        = code,
                client_name        = instance.client_name,
                agent              = instance.agent,
                area               = instance.area,
                outstanding_amount = float(instance.outstanding_amount or 0),
                oldest_due_days    = 0,
                alert_type         = 'ESCALATED',
                severity           = 'HIGH',
                assigned_to        = escalated_user,
            )

    # ── Standard overdue / due_soon alerts ───────────────────────────
    fu = (
        FollowUp.objects
        .filter(client_code=code)
        .order_by('-created_at')
        .first()
    )

    if fu is None or fu.next_followup_date is None or float(fu.outstanding_amount or 0) <= 0:
        return

    nfd         = fu.next_followup_date
    outstanding = float(fu.outstanding_amount or 0)

    if nfd < today:
        alert_type = 'OVERDUE'
        severity   = 'HIGH'
    elif today <= nfd <= week_end:
        alert_type = 'DUE_SOON'
        severity   = 'HIGH' if nfd == today else 'MEDIUM'
    else:
        return

    oldest_due_days = (today - nfd).days

    existing = PaymentAlert.objects.filter(
        client_code=code,
        alert_type=alert_type,
        is_resolved=False,
        assigned_to=None,   # general alerts have no assignee
    ).first()

    if existing:
        existing.outstanding_amount = outstanding
        existing.oldest_due_days    = oldest_due_days
        existing.severity           = severity
        existing.client_name        = fu.client_name
        existing.agent              = fu.agent
        existing.area               = fu.area
        existing.save()
    else:
        PaymentAlert.objects.create(
            client_code        = code,
            client_name        = fu.client_name,
            agent              = fu.agent,
            area               = fu.area,
            outstanding_amount = outstanding,
            oldest_due_days    = oldest_due_days,
            alert_type         = alert_type,
            severity           = severity,
            assigned_to        = None,
        )