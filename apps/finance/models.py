"""
Finance models.
Add your transaction, ledger, account models here.
"""
from django.db import models
from apps.common.models import BaseModel


class Account(BaseModel):
    """Account model for finance management."""
    name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50, unique=True)
    account_type = models.CharField(
        max_length=50,
        choices=[
            ('ASSET', 'Asset'),
            ('LIABILITY', 'Liability'),
            ('EQUITY', 'Equity'),
            ('REVENUE', 'Revenue'),
            ('EXPENSE', 'Expense'),
        ]
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'finance_accounts'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return f"{self.name} ({self.account_number})"
