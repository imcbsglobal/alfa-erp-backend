# Generated migration to add performance indexes for DeliverySession queries

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0056_alter_customer_phone1_alter_customer_phone2_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deliverysession',
            options={},
        ),
        migrations.AddIndex(
            model_name='deliverysession',
            index=models.Index(fields=['delivery_type'], name='sales_deliv_delivery_type_idx'),
        ),
        migrations.AddIndex(
            model_name='deliverysession',
            index=models.Index(fields=['created_at'], name='sales_deliv_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='deliverysession',
            index=models.Index(fields=['delivery_status', 'delivery_type'], name='sales_deliv_status_type_idx'),
        ),
        migrations.AddIndex(
            model_name='deliverysession',
            index=models.Index(fields=['delivery_type', 'created_at'], name='sales_deliv_type_date_idx'),
        ),
        migrations.AddIndex(
            model_name='deliverysession',
            index=models.Index(fields=['assigned_to', 'created_at'], name='sales_deliv_assigned_date_idx'),
        ),
    ]
