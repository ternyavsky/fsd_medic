# Generated by Django 4.2.4 on 2023-10-04 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_interest'),
        ('auth_doctor', '0003_doctor_created_at_doctor_updated_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='linktointerview',
            options={'verbose_name': 'Интервью', 'verbose_name_plural': 'Интервью'},
        ),
        migrations.AddField(
            model_name='linktointerview',
            name='center',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.center', verbose_name='Центр'),
        ),
        migrations.AddField(
            model_name='linktointerview',
            name='clinic',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.clinic', verbose_name='Клиника'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='id',
            field=models.BigAutoField(db_index=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='linktointerview',
            name='doctor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auth_doctor.doctor', verbose_name='Врач'),
        ),
    ]