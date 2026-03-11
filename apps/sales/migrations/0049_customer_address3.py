from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0048_invoice_self_boxing'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='address3',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
