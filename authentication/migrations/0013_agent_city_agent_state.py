# Generated by Django 5.1.1 on 2024-10-20 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_testimonials_caption'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='city',
            field=models.CharField(default='Lagos', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agent',
            name='state',
            field=models.CharField(choices=[('Abia', 'AB'), ('Adamawa', 'AD'), ('Akwa Ibom', 'AK'), ('Anambra', 'AN'), ('Bauchi', 'BA'), ('Bayelsa', 'BY'), ('Benue', 'BE'), ('Borno', 'BO'), ('Cross River', 'CR'), ('Delta', 'DE'), ('Ebonyi', 'EB'), ('Edo', 'ED'), ('Ekiti', 'EK'), ('Enugu', 'EN'), ('Gombe', 'GO'), ('Imo', 'IM'), ('Jigawa', 'JI'), ('Kaduna', 'KD'), ('Kano', 'KN'), ('Katsina', 'KT'), ('Kebbi', 'KE'), ('Kogi', 'KO'), ('Kwara', 'KW'), ('Lagos', 'LA'), ('Nasarawa', 'NA'), ('Niger', 'NI'), ('Ogun', 'OG'), ('Ondo', 'ON'), ('Osun', 'OS'), ('Oyo', 'OY'), ('Plateau', 'PL'), ('Rivers', 'RV'), ('Sokoto', 'SO'), ('Taraba', 'TA'), ('Yobe', 'YO'), ('Zamfara', 'ZA'), ('Federal Capital Territory', 'FC')], default='Lagos', max_length=50),
            preserve_default=False,
        ),
    ]
