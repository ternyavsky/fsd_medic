# Generated by Django 4.2.4 on 2023-10-01 14:05

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('is_required', models.BooleanField(blank=True, default=False, verbose_name='Статус подтверждения')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Статус персонала')),
                ('sex', models.CharField(default=None, max_length=255, null=True, verbose_name='Пол')),
                ('number', models.CharField(max_length=30, null=True, unique=True, verbose_name='Номер')),
                ('email', models.CharField(blank=True, max_length=100, null=True, unique=True,
                                           verbose_name='Электронный адрес')),
                ('first_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=30, null=True, verbose_name='Фамилия')),
                ('surname', models.CharField(blank=True, max_length=40, null=True, verbose_name='Отчество')),
                ('interest',
                 models.CharField(blank=True, max_length=225, null=True, verbose_name='Интерес к заболеванию')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('image',
                 models.ImageField(blank=True, default='users_photos/AccauntPreview.png', upload_to='users_photos/',
                                   verbose_name='Фотография Пользователья')),
                ('address', models.CharField(max_length=100, null=True, verbose_name='Адрес')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения')),
                ('verification_code', models.PositiveIntegerField(default=1, verbose_name='СМС код подтверждения')),
                ('reset_code', models.PositiveIntegerField(default=1, verbose_name='Код для сброса пароля')),
                ('email_verification_code',
                 models.PositiveIntegerField(default=0, verbose_name='Код для привязки почты к аккаунту')),
            ],
            options={
                'verbose_name': 'Пользователья',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Доступ',
                'verbose_name_plural': 'Доступ',
            },
        ),
        migrations.CreateModel(
            name='Center',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Название центра')),
                ('image',
                 models.ImageField(blank=True, default='centers_photos/center_photo.jpg', upload_to='centers_photos/',
                                   verbose_name='Фото центра')),
                ('rating', models.FloatField(default=5, max_length=5,
                                             validators=[django.core.validators.MinValueValidator(0.0),
                                                         django.core.validators.MaxValueValidator(5.0)],
                                             verbose_name='Рейтинг центра')),
                (
                'description', models.TextField(blank=True, max_length=550, null=True, verbose_name='Описание центра')),
                ('is_required', models.BooleanField(default=False, verbose_name='Статус подтверждения')),
                ('number', models.CharField(max_length=30, null=True, unique=True, verbose_name='Номер')),
                ('email', models.CharField(max_length=100, null=True, unique=True, verbose_name='Электронный адрес')),
                ('observed', models.IntegerField(default=100, verbose_name='Наблюдается')),
                ('observed_after', models.IntegerField(default=100, verbose_name='Наблюдалось')),
                ('address', models.CharField(max_length=100, null=True, unique=True, verbose_name='Адрес')),
                ('lng', models.DecimalField(decimal_places=4, default=0, max_digits=6, verbose_name='Долгота')),
                ('lat', models.DecimalField(decimal_places=4, default=0, max_digits=6, verbose_name='Широта')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата Изменения')),
            ],
            options={
                'verbose_name': 'Центр',
                'verbose_name_plural': 'Центры',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название страны')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, verbose_name='Название Клиники')),
                ('is_required', models.BooleanField(default=False, verbose_name='Статус подтверждения')),
                ('rating', models.FloatField(default=5, validators=[django.core.validators.MinValueValidator(0.0),
                                                                    django.core.validators.MaxValueValidator(5.0)],
                                             verbose_name='Рейтинг клиники')),
                ('description',
                 models.TextField(blank=True, max_length=550, null=True, verbose_name='Описание клиники')),
                ('image',
                 models.ImageField(blank=True, default='centers_photos/clinic_photo.jpg', upload_to='clinics_photos/',
                                   verbose_name='Фото клиники')),
                ('number', models.CharField(max_length=30, unique=True, verbose_name='Номер')),
                ('email', models.CharField(max_length=100, unique=True, verbose_name='Электронный адрес')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='Адрес')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата Изменения')),
                ('review_date', models.DateTimeField(null=True, verbose_name='Предполагаемая дата и время интервью')),
            ],
            options={
                'verbose_name': 'Клиника',
                'verbose_name_plural': 'Клиники',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название страны')),
            ],
            options={
                'verbose_name': 'Страна',
                'verbose_name_plural': 'Страны',
            },
        ),
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Заболевание',
                'verbose_name_plural': 'Заболевания',
            },
        ),
        migrations.CreateModel(
            name='EmailCode',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('code', models.IntegerField()),
                ('email', models.CharField(max_length=100, null=True, unique=True, verbose_name='Электронный адрес')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, null=True, verbose_name='Название Группы')),
                ('number_of_people', models.IntegerField(default=0, verbose_name='Количество людей')),
            ],
            options={
                'verbose_name': 'Группу',
                'verbose_name_plural': 'Группы',
            },
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=30, null=True, verbose_name='Тип интервью')),
                ('date', models.DateTimeField(null=True, verbose_name='Дата интервью')),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=40, null=True, verbose_name='Фамилия')),
                ('number', models.CharField(max_length=30, null=True, unique=True, verbose_name='Номер')),
                ('email', models.CharField(max_length=100, null=True, unique=True, verbose_name='Электронный адрес')),
                ('is_required', models.BooleanField(default=False, verbose_name='Статус подтверждения')),
                ('application', models.CharField(max_length=30, null=True, verbose_name='Приложение')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Интервью',
                'verbose_name_plural': 'Интервью',
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Лайки',
            },
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=40, null=True, verbose_name='Заголовок новости')),
                ('text', models.TextField(blank=True, max_length=500, null=True, verbose_name='Текст новости')),
                ('image', models.ImageField(default='news_photos/news_photo.jpg', upload_to='news_photos/',
                                            verbose_name='Фото к новости')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name': 'Новость',
                'verbose_name_plural': 'Новости',
            },
        ),
        migrations.CreateModel(
            name='NumberCode',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('code', models.IntegerField()),
                ('number', models.CharField(max_length=30, null=True, unique=True, verbose_name='Номер')),
            ],
        ),
        migrations.CreateModel(
            name='Url_Params',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter', models.CharField(max_length=50, verbose_name='Ссылка')),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.group',
                                            verbose_name='Группа')),
            ],
            options={
                'verbose_name': 'Ссылку',
                'verbose_name_plural': 'Ссылки для регистрации',
            },
        ),
        migrations.CreateModel(
            name='Saved',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('news',
                 models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.news',
                                   verbose_name='Новость')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сохранение',
                'verbose_name_plural': 'Сохраненное',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(db_index=True, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='Название записи')),
                ('online', models.BooleanField(default=False, verbose_name='Онлайн')),
                ('time_start', models.DateTimeField(blank=True, null=True, verbose_name='Начало ')),
                ('time_end', models.DateTimeField(blank=True, null=True, verbose_name='Конец')),
                ('notify', models.DateTimeField(blank=True, null=True, verbose_name='Время уведомления о записи')),
                ('problem', models.CharField(blank=True, max_length=255, null=True, verbose_name='Причина')),
                ('duration_note', models.IntegerField(blank=True, null=True, verbose_name='Длительность')),
                ('file',
                 models.FileField(blank=True, null=True, upload_to='files_to_notes/', verbose_name='Файлы к записи')),
                ('special_check', models.BooleanField(default=False, verbose_name='Доп. проверка специалистов')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения')),
                ('status', models.CharField(choices=[('Passed', 'Подтверждена'), ('In processing', 'На рассмотрении'),
                                                     ('Rejected', 'Отклонена')], default='In processing',
                                            max_length=255, verbose_name='Статус записи')),
                ('center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             to='api.center')),
                ('clinic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                             to='api.clinic')),
            ],
            options={
                'verbose_name': 'Запись',
                'verbose_name_plural': 'Записи',
            },
        ),
    ]
