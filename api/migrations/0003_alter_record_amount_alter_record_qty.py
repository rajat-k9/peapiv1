# Generated by Django 4.1.5 on 2023-02-01 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_customer_contact_alter_record_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='amount',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='qty',
            field=models.IntegerField(default=1),
        ),
    ]