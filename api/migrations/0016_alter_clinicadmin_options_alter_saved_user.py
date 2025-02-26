# Generated by Django 5.0.1 on 2024-06-20 12:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_alter_clinic_admin_alter_clinic_password'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clinicadmin',
            options={'verbose_name': 'Администратор клиники', 'verbose_name_plural': 'Администраторы клиник'},
        ),
        migrations.AlterField(
            model_name='saved',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
