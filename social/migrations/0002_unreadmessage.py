# Generated by Django 4.2.6 on 2023-11-19 21:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnreadMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.chat', verbose_name='Чат')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.message', verbose_name='Сообщение')),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]