# Generated by Django 5.0.1 on 2024-01-21 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0027_subscribe'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='center',
        #     name='country',
        # ),
        migrations.RemoveField(
            model_name='clinic',
            name='city',
        ),
        # migrations.RemoveField(
        #     model_name='clinic',
        #     name='country',
        # ),
    ]