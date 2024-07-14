# Generated by Django 5.0.6 on 2024-07-12 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0039_usergift'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_percentage', models.FloatField()),
            ],
        ),
    ]
