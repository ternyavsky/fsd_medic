# Generated by Django 4.2.4 on 2023-10-05 19:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0005_center_review_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='review_passed',
            field=models.BooleanField(null=True, verbose_name='Собеседование пройдено'),
        ),
        migrations.AddField(
            model_name='clinic',
            name='review_passed',
            field=models.BooleanField(null=True, verbose_name='Собеседование пройдено'),
        ),
    ]
