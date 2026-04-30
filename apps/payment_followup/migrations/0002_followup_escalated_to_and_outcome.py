from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_followup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='followup',
            name='escalated_to',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='followup',
            name='outcome',
            field=models.CharField(choices=[('PROMISED', 'Payment Promised'), ('PARTIAL', 'Partial Payment'), ('NO_RESPONSE', 'No Response'), ('DISPUTE', 'Dispute Raised'), ('ESCALATED', 'Escalated'), ('PAID', 'Payment Received')], max_length=20),
        ),
    ]