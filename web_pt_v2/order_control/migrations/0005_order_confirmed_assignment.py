# Generated by Django 4.2.7 on 2024-01-09 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_control', '0004_alter_technician_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='confirmed_assignment',
            field=models.BooleanField(default=False, verbose_name='Asignación confirmada'),
        ),
    ]
