# Generated by Django 5.0.6 on 2024-06-24 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0017_paymentsystem_is_paid_paymentsystem_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentsystem',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='paymentsystem',
            name='user',
        ),
    ]
