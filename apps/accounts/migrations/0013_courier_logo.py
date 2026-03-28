from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_tray_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='courier_logo',
            field=models.ImageField(blank=True, null=True, upload_to='couriers/logos/'),
        ),
    ]
