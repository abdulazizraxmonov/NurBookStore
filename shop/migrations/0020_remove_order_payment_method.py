# Generated by Django 5.0.6 on 2024-06-24 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_order_payment_system'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment_method',
        ),
    ]
