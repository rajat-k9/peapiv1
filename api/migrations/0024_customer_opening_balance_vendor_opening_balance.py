# Generated by Django 4.1.5 on 2023-08-08 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_product_opening_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='opening_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='vendor',
            name='opening_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
