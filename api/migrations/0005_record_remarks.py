# Generated by Django 4.1.5 on 2023-02-01 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_record_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='remarks',
            field=models.TextField(default=''),
        ),
    ]
