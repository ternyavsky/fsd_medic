# Generated by Django 5.0.1 on 2024-01-28 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_user_city_user_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='main_center',
        ),
    ]