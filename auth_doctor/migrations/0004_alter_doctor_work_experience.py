# Generated by Django 5.0.1 on 2024-07-13 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_doctor', '0003_alter_doctor_center'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='work_experience',
            field=models.DecimalField(decimal_places=1, max_digits=3, null=True, verbose_name='Опыт работы, лет'),
        ),
    ]