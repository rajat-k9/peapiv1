# Generated by Django 4.1.5 on 2023-02-02 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_record_amount_alter_record_remarks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='amount',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]
