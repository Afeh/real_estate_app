# Generated by Django 5.1.1 on 2024-10-16 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_property_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
    ]