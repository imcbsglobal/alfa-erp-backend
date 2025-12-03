# Generated migration for changing role to roles (multiple roles support)

from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


def migrate_role_to_roles(apps, schema_editor):
    """Migrate existing single role to roles array"""
    User = apps.get_model('accounts', 'User')
    for user in User.objects.all():
        if hasattr(user, 'role') and user.role:
            user.roles = [user.role]
            user.save(update_fields=['roles'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_role'),
    ]

    operations = [
        # Add new roles field
        migrations.AddField(
            model_name='user',
            name='roles',
            field=ArrayField(
                models.CharField(
                    choices=[
                        ('ADMIN', 'Admin'),
                        ('STORE', 'Store'),
                        ('DELIVERY', 'Delivery'),
                        ('PURCHASE', 'Purchase'),
                        ('ACCOUNTS', 'Accounts'),
                        ('VIEWER', 'Viewer')
                    ],
                    max_length=20
                ),
                blank=True,
                default=list,
                help_text='List of roles assigned to the user for access control'
            ),
        ),
        # Migrate data from role to roles
        migrations.RunPython(migrate_role_to_roles, migrations.RunPython.noop),
        # Remove old role field
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
