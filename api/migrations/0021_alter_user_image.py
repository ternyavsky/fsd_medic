# Generated by Django 5.0.1 on 2024-01-11 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_alter_user_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, default=None, upload_to='users_photos/', verbose_name='Фотография Пользователья'),
        ),
    ]