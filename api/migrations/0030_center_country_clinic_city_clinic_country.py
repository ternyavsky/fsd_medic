# Generated by Django 5.0.1 on 2024-01-21 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_remove_center_city_remove_center_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Cтрана'),
        ),
        migrations.AddField(
            model_name='clinic',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Город'),
        ),
        migrations.AddField(
            model_name='clinic',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Cтрана'),
        ),
    ]