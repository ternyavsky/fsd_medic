# Generated by Django 4.2.6 on 2023-11-02 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_center_last_login_alter_center_password_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinic',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
