from django.db import models
from django.conf import settings


class FollowUp(models.Model):
    """
    A follow-up log entry for a client payment.
    Linked to acc_master via client_code (from the sync tool).
    """
    OUTCOME_CHOICES = [
        ('PROMISED',    'Payment Promised'),
        ('PARTIAL',     'Partial Payment'),
        ('NO_RESPONSE', 'No Response'),
        ('DISPUTE',     'Dispute Raised'),
        ('ESCALATED',   'Escalated'),
        ('PAID',        'Payment Received'),
    ]

    CHANNEL_CHOICES = [
        ('PHONE',    'Phone Call'),
        ('WHATSAPP', 'WhatsApp'),
        ('EMAIL',    'Email'),
        ('VISIT',    'Field Visit'),
    ]

    # ── Client info (denormalised from acc_master for speed) ──
    client_code  = models.CharField(max_length=30, db_index=True)
    client_name  = models.CharField(max_length=250)
    agent        = models.CharField(max_length=30, null=True, blank=True)
    area         = models.CharField(max_length=250, null=True, blank=True)

    # ── Financial snapshot at log time ──
    outstanding_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    promised_amount = models.DecimalField(max_digits=16, decimal_places=2,null=True, blank=True)

    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='PHONE')

    # ── Follow-up details ──
    outcome      = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    escalated_to = models.CharField(max_length=250, blank=True, default='')
    notes        = models.TextField(blank=True, default='')
    next_followup_date = models.DateField(null=True, blank=True)

    # ── Meta ──
    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='followups_logged'
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table   = 'followup_log'
        ordering   = ['-created_at']

    def __str__(self):
        return f"{self.client_name} — {self.outcome} ({self.created_at.date()})"


class PaymentAlert(models.Model):
    """
    Auto-generated or manual alerts for overdue / at-risk clients.
    """
    ALERT_TYPE_CHOICES = [
        ('OVERDUE',      'Overdue'),
        ('DUE_SOON',     'Due This Week'),
        ('HIGH_RISK',    'High Risk'),
        ('NO_FOLLOWUP',  'No Follow-Up Logged'),
        ('ESCALATED',   'Escalated To You'),  
    ]
    SEVERITY_CHOICES = [
        ('HIGH',   'High'),
        ('MEDIUM', 'Medium'),
        ('LOW',    'Low'),
    ]

    client_code        = models.CharField(max_length=30, db_index=True)
    client_name        = models.CharField(max_length=250)
    agent              = models.CharField(max_length=30, null=True, blank=True)
    area               = models.CharField(max_length=250, null=True, blank=True)
    outstanding_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    oldest_due_days    = models.IntegerField(default=0)
    alert_type         = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity           = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MEDIUM')
    is_resolved        = models.BooleanField(default=False)
    resolved_at        = models.DateTimeField(null=True, blank=True)
    resolved_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='resolved_alerts'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_alerts'
    )
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'followup_alert'
        ordering = ['-oldest_due_days', '-outstanding_amount']

    def __str__(self):
        return f"[{self.severity}] {self.client_name} — {self.alert_type}"