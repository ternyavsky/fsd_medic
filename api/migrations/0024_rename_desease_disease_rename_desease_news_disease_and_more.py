# Generated by Django 4.2.1 on 2023-06-16 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_saved_options_user_image_alter_images_image_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Desease',
            new_name='Disease',
        ),
        migrations.RenameField(
            model_name='news',
            old_name='desease',
            new_name='disease',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='desease',
            new_name='disease',
        ),
    ]