# Generated by Django 5.0.1 on 2024-02-17 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0051_access_created_at_access_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinic',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='clinic',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения'),
        ),
    ]