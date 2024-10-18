# Generated by Django 5.1.1 on 2024-10-17 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0007_property_average_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='average_rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=2),
        ),
    ]
