# Generated by Django 5.0.1 on 2024-01-30 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0003_unreadmessage_center_unreadmessage_doctor_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='centers',
        ),
        migrations.RemoveField(
            model_name='message',
            name='center',
        ),
    ]