from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0044_customer_pincode"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BulkStatusUpdateLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("from_status", models.CharField(max_length=20)),
                ("to_status", models.CharField(max_length=20)),
                ("from_date", models.DateField(blank=True, null=True)),
                ("to_date", models.DateField(blank=True, null=True)),
                ("count", models.PositiveIntegerField(default=0)),
                ("invoices_snapshot", models.JSONField(default=list)),
                ("executed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "performed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bulk_status_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-executed_at"],
            },
        ),
        migrations.AddIndex(
            model_name="bulkstatusupdatelog",
            index=models.Index(fields=["-executed_at"], name="sales_bulks_execute_idx"),
        ),
    ]
