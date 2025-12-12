"""
Create Department model, add FK from JobTitle to Department, and migrate existing user.department strings to FK
"""
from django.db import migrations, models
import django.db.models.deletion
import uuid


def migrate_department_strings(apps, schema_editor):
    Department = apps.get_model('accounts', 'Department')
    User = apps.get_model('accounts', 'User')

    # Gather unique department names from users
    names = set()
    for u in User.objects.filter(department__isnull=False):
        # department used to be a string: ensure it's a string before creating
        name = getattr(u, 'department')
        if name:
            names.add(name.strip())

    # Create departments for each unique name
    name_to_obj = {}
    for name in names:
        dept = Department.objects.create(name=name)
        name_to_obj[name] = dept

    # Update users to reference the created department objects (into department_fk)
    for u in User.objects.filter(department__isnull=False):
        name = getattr(u, 'department')
        if name:
            dept = name_to_obj.get(name.strip())
            if dept:
                setattr(u, 'department_fk', dept)
                u.save(update_fields=['department_fk'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_rename_first_name_user_name_remove_user_last_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Department',
                'verbose_name_plural': 'Departments',
                'db_table': 'departments',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='jobtitle',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_titles', to='accounts.department', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='jobtitle',
            name='title',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterUniqueTogether(
            name='jobtitle',
            unique_together={('department', 'title')},
        ),
        # Add a temporary FK field to hold department references
        migrations.AddField(
            model_name='user',
            name='department_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_tmp', to='accounts.department'),
        ),
        # Convert existing department string values in users to FK into department_fk
        migrations.RunPython(migrate_department_strings, reverse_code=migrations.RunPython.noop),
        # Remove the old charfield 'department'
        migrations.RemoveField(
            model_name='user',
            name='department',
        ),
        # Rename the temporary field back to 'department'
        migrations.RenameField(
            model_name='user',
            old_name='department_fk',
            new_name='department',
        ),
    ]
