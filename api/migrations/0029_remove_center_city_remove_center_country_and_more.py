# Generated by Django 5.0.1 on 2024-01-21 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0028_remove_center_country_remove_clinic_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='center',
            name='city',
        ),
        migrations.RemoveField(
            model_name='center',
            name='country',
        ),
        migrations.RemoveField(
            model_name='clinic',
            name='country',
        ),
    ]