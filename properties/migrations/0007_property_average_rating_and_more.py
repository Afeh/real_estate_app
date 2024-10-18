# Generated by Django 5.1.1 on 2024-10-17 09:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_remove_propertyreviews_average_rating_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='average_rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=2),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='propertyreviews',
            name='property',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='properties.property'),
        ),
    ]
