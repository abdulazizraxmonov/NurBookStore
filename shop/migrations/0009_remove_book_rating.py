# Generated by Django 5.0.6 on 2024-06-21 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_book_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='rating',
        ),
    ]
