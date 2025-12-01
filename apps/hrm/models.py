"""
HRM models.
Add your employee, department, attendance, and payroll models here.
"""
from django.db import models
from apps.common.models import BaseModel


# Example model - expand as needed
class Department(BaseModel):
    """Department model for organizing employees."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    
    class Meta:
        db_table = 'hrm_departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return self.name
