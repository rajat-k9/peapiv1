# Generated by Django 4.1.5 on 2023-02-26 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_stock'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='record',
            options={'ordering': ('-sale_date', '-created_on')},
        ),
        migrations.AddField(
            model_name='record',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.customer'),
        ),
    ]
