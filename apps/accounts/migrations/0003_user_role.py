# Generated migration for adding role field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('ADMIN', 'Admin'),
                    ('STORE', 'Store'),
                    ('DELIVERY', 'Delivery'),
                    ('PURCHASE', 'Purchase'),
                    ('ACCOUNTS', 'Accounts'),
                    ('VIEWER', 'Viewer')
                ],
                default='VIEWER',
                help_text='User role for access control',
                max_length=20
            ),
        ),
    ]
