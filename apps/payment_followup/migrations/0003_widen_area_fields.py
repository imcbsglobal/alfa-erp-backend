from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_followup', '0002_followup_escalated_to_and_outcome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followup',
            name='area',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='paymentalert',
            name='area',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]