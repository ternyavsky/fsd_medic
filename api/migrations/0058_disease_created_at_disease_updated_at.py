# Generated by Django 5.0.1 on 2024-02-17 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0057_saved_created_at_saved_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='disease',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания'),
        ),
        migrations.AddField(
            model_name='disease',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения'),
        ),
    ]