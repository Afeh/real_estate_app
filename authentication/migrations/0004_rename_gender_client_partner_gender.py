# Generated by Django 5.1.1 on 2024-10-06 21:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_agent_client_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='gender',
            new_name='partner_gender',
        ),
    ]
