# Generated by Django 5.0.6 on 2024-07-08 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0033_city_check_city_delete_usercity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='check',
            name='city',
            field=models.CharField(max_length=100),
        ),
        migrations.DeleteModel(
            name='City',
        ),
    ]
