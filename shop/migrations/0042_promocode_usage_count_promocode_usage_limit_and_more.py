# Generated by Django 5.0.6 on 2024-07-12 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0041_check_promo_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='usage_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='promocode',
            name='usage_limit',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='discount_percentage',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]
