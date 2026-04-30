"""
apps/payment_followup/management/commands/generate_alerts.py

One-time backfill command. Run ONCE to generate alerts for all existing
FollowUp records that already have next_followup_date set.

After this, signals.py handles everything automatically.

Usage:
    python manage.py generate_alerts
"""

from django.core.management.base import BaseCommand
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


def run_generate_alerts():
    from apps.payment_followup.models import FollowUp, PaymentAlert

    today    = date.today()
    week_end = today + timedelta(days=7)

    created = 0
    updated = 0
    skipped = 0

    # ── Get the latest follow-up per client ─────────────────────────────
    seen_clients = {}
    for fu in FollowUp.objects.order_by('client_code', '-created_at'):
        if fu.client_code not in seen_clients:
            seen_clients[fu.client_code] = fu

    for code, fu in seen_clients.items():
        nfd         = fu.next_followup_date
        outstanding = float(fu.outstanding_amount or 0)

        if outstanding <= 0 or nfd is None:
            skipped += 1
            continue

        # ── Determine alert type & severity ─────────────────────────────
        if nfd < today:
            alert_type = 'OVERDUE'
            severity   = 'HIGH'
        elif today <= nfd <= week_end:
            alert_type = 'DUE_SOON'
            severity   = 'HIGH' if nfd == today else 'MEDIUM'
        else:
            skipped += 1
            continue

        oldest_due_days = (today - nfd).days

        # ── Upsert ──────────────────────────────────────────────────────
        existing = PaymentAlert.objects.filter(
            client_code=code,
            alert_type=alert_type,
            is_resolved=False,
        ).first()

        if existing:
            changed = False
            for field, val in [
                ('outstanding_amount', outstanding),
                ('oldest_due_days',    oldest_due_days),
                ('severity',           severity),
            ]:
                if getattr(existing, field) != val:
                    setattr(existing, field, val)
                    changed = True
            if changed:
                existing.save()
                updated += 1
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
            )
            created += 1

    return {'created': created, 'updated': updated, 'skipped': skipped}


class Command(BaseCommand):
    help = "One-time backfill: generate PaymentAlerts from existing FollowUp records"

    def handle(self, *args, **options):
        self.stdout.write("Running alert backfill...")
        result = run_generate_alerts()
        self.stdout.write(
            self.style.SUCCESS(
                f"Done — created: {result['created']}, "
                f"updated: {result['updated']}, "
                f"skipped: {result['skipped']}"
            )
        )