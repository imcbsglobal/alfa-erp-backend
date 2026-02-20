from django.db import models


class DailyHoldSnapshot(models.Model):
    snapshot_date = models.DateField(unique=True)
    hold_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.snapshot_date} - {self.hold_count} holds"