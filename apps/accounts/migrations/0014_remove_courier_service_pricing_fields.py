from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_courier_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courier',
            name='base_rate',
        ),
        migrations.RemoveField(
            model_name='courier',
            name='max_weight',
        ),
        migrations.RemoveField(
            model_name='courier',
            name='rate_type',
        ),
        migrations.RemoveField(
            model_name='courier',
            name='service_area',
        ),
        migrations.RemoveField(
            model_name='courier',
            name='vehicle_type',
        ),
    ]
