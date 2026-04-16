# Generated migration for is_express_delivery field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0057_add_delivery_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='is_express_delivery',
            field=models.BooleanField(default=False, help_text='True when invoice is processed through Express Billing (INVOICED→PICKED→PACKED pathway)'),
        ),
    ]
