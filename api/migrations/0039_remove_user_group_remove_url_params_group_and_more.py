# Generated by Django 5.0.1 on 2024-02-09 18:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_note_doctors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='group',
        ),
        migrations.RemoveField(
            model_name='url_params',
            name='group',
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.DeleteModel(
            name='Url_Params',
        ),
    ]