# Generated by Django 4.1.5 on 2023-08-12 02:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_productloghistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warehouse', models.CharField(choices=[('shop', 'Shop'), ('home', 'Home'), ('po_godown', 'Post Office Godown'), ('colony', 'Teacher Colony Godown'), ('hameerpur', 'Hameerpur Road')], default='home', max_length=100)),
                ('qty', models.IntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
        ),
    ]
