# Generated by Django 4.2.7 on 2023-11-18 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order_control', '0002_alter_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', related_query_name='order', to='order_control.customer', verbose_name='Cliente'),
        ),
    ]