# Generated by Django 5.0.1 on 2024-02-09 19:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0040_remove_center_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="center",
            name="country",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="api.country",
                verbose_name="Страна",
            ),
        ),
    ]
