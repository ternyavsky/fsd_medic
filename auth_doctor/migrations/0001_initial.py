# Generated by Django 4.2.4 on 2023-10-01 14:05

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('api', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions without explicitly assigning them.',
                                                     verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                              help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                              max_length=150, unique=True,
                                              validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                                              verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False,
                                                 help_text='Designates whether the user can log into this admin site.',
                                                 verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True,
                                                  help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                                  verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('number', models.CharField(max_length=30, verbose_name='Номер телефона')),
                ('middle_name', models.CharField(max_length=50, verbose_name='Отчетсво')),
                ('city', models.CharField(max_length=220, verbose_name='Город')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес')),
                ('specialization', models.CharField(max_length=200, verbose_name='Специальность/должность')),
                ('work_experience',
                 models.DecimalField(decimal_places=1, max_digits=3, verbose_name='Опыт работы, лет')),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('interview_date_plan', models.DateTimeField(null=True,
                                                             verbose_name='Время, когда пользователь хочет, чтобы было проведено собеседование')),
                ('is_approved_for_interview', models.BooleanField(default=False)),
                ('is_approved_for_work', models.BooleanField(default=False)),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.center',
                                             verbose_name='Центр, в котором зарегистрирован врач')),
                ('clinic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.clinic',
                                             verbose_name='Клиника, где врач работает')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.country')),
                ('groups', models.ManyToManyField(blank=True,
                                                  help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name='user_set', related_query_name='user', to='auth.group',
                                                  verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                                            related_name='user_set', related_query_name='user',
                                                            to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Врач',
                'verbose_name_plural': 'Врачи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='LinkToInterview',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('link', models.CharField(max_length=220, verbose_name='Ссылка на интервью')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth_doctor.doctor')),
            ],
        ),
    ]
