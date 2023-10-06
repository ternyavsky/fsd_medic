import random
from re import VERBOSE
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.db import models
from rest_framework import serializers
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod
from django.core.validators import MaxValueValidator, MinValueValidator
from .choices import NOTE_CHOICES, PROCESS


class UserManager(BaseUserManager):
    def create_user(self, number, password, group=None, center_id=None, email=None, first_name=None, last_name=None,
                    disease_id=None, *args, **kwargs):
        user = self.model(number=number)
        user_group = Group.objects.get(name='Пользователи')
        user_group.number_of_people += 1
        user_group.save(update_fields=['number_of_people'])
        user.group_id = user_group.id

        user.set_password(password)

        if group == 'Пользователи':
            user.disease_id = disease_id
            user.is_required = True
        else:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_required = False
        # это UserManager(BaseUserManager)

        user.save()
        return user

    def update_user(self, user, number=None, email=None, password=None, first_name=None, last_name=None, surname=None,
                    center_id=None, disease_id=None):

        updated_fields = ["updated_at"]
        user_group = Group.objects.get(name='Пользователи')
        last_user_group = Group.objects.get(name='Пациенты')
        user.group_id = user_group.id
        user_group.number_of_people += 1
        user_group.save(update_fields=['number_of_people'])
        last_user_group.number_of_people -= 1
        last_user_group.save(update_fields=['number_of_people'])

        if center_id is not None:
            user.center_id = center_id
            user.country_id = Center.objects.get(id=center_id).country_id
            updated_fields += 'center_id'

        if number is not None:
            user.number = number

        if email is not None:
            user.email = email

        if password is not None:
            user.set_password()

        user.save(update_fields=updated_fields)
        return user

    def create_superuser(self, number, email, first_name, last_name, password=None):
        superuser = self.model(number=number, email=email,
                               first_name=first_name, last_name=last_name)

        superuser_group = Group.objects.get(name='Администраторы')
        superuser_group.number_of_people += 1
        superuser_group.save(update_fields=['number_of_people'])
        superuser.group_id = superuser_group.id

        superuser.is_staff = True
        superuser.is_required = False

        superuser.set_password(password)

        superuser.save()
        return superuser


class User(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True, db_index=True)
    is_required = models.BooleanField(verbose_name=_(
        'Статус подтверждения'), default=False, blank=True)
    is_staff = models.BooleanField(
        verbose_name=_('Статус персонала'), default=False)
    group = models.ForeignKey('Group', verbose_name=_(
        'Группа'), on_delete=models.CASCADE)
    sex = models.CharField(_("Пол"), max_length=255, default=None, null=True)
    main_center = models.ForeignKey('Center', verbose_name=_('Ведущий центр'), on_delete=models.PROTECT, null=True,
                                    blank=True, related_name="main_center")
    clinic = models.ForeignKey("Clinic", on_delete=models.PROTECT, verbose_name=_("Клиника"), null=True, related_name="user_clinic")
    centers = models.ManyToManyField('Center', verbose_name=_('Центр'),  blank=True)
    disease = models.ManyToManyField('Disease', verbose_name=_('Заболевания'), blank=True)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, blank=True, null=True, unique=True)
    first_name = models.CharField(verbose_name=_('Имя'), max_length=20, null=True, blank=True)
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=30, null=True, blank=True)
    surname = models.CharField(verbose_name=_('Отчество'), max_length=40, null=True, blank=True)
    interest = models.ForeignKey("Disease", verbose_name=_('Интерес к заболеванию'), null=True, blank=True, on_delete=models.CASCADE, related_name="interest")
    birthday = models.DateField(verbose_name=_('Дата рождения'), null=True, blank=True)
    image = models.ImageField(verbose_name=_('Фотография Пользователья'), upload_to='users_photos/', blank=True,
                              default='users_photos/AccauntPreview.png')
    country = models.ForeignKey(
        'Country', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    city = models.ForeignKey("City", on_delete=models.PROTECT, verbose_name=_("Город"), default=None)
    address = models.CharField(verbose_name=_(
        'Адрес'), max_length=100, unique=False, null=True)
    created_at = models.DateTimeField(verbose_name=_(
        'Дата создания'), auto_now_add=True, blank=True, null=True, )
    updated_at = models.DateTimeField(verbose_name=_(
        'Дата изменения'), auto_now=True, blank=True, null=True, )
    verification_code = models.PositiveIntegerField(
        verbose_name=_('СМС код подтверждения'), default=1)
    reset_code = models.PositiveIntegerField(
        _('Код для сброса пароля'), default=1)
    email_verification_code = models.PositiveIntegerField(
        _('Код для привязки почты к аккаунту'), default=0)

    USERNAME_FIELD = 'number'

    objects = UserManager()

    def __str__(self):
        return self.number

    def delete(self, using=None, keep_parents=False):
        group = Groups.objects.get(id=self.group_id)
        group.number_of_people -= 1
        group.save(update_fields=['number_of_people'])

        super(User, self).delete()

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователья'


class Group(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(verbose_name=_(
        'Название Группы'), max_length=100, null=True)
    number_of_people = models.IntegerField(
        verbose_name=_('Количество людей'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'Группу'


class Access(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    user = models.ForeignKey("User", verbose_name=_(
        "Пользователь"), on_delete=models.CASCADE, related_name="user")
    access_accept = models.ManyToManyField(
        "User", verbose_name=_("Доступ (принятые)"), related_name="access")
    access_unaccept = models.ManyToManyField("User", verbose_name=_(
        "Доступ (непринятые)"), related_name="unaccept")

    def __str__(self):
        return f'Доступ пользователя {self.user}'

    class Meta:
        verbose_name_plural = 'Доступ'
        verbose_name = 'Доступ'


class Note(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    user = models.ForeignKey('User', verbose_name=_(
        'Пользователь'), on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(verbose_name=_('Название записи'), max_length=255)
    online = models.BooleanField(verbose_name=_('Онлайн'), default=False)
    time_start = models.DateTimeField(
        verbose_name=_('Начало '), null=True, blank=True)
    time_end = models.DateTimeField(
        verbose_name=_('Конец'), null=True, blank=True)
    notify = models.DateTimeField(verbose_name=_(
        'Время уведомления о записи'), null=True, blank=True)
    doctor = models.ForeignKey('auth_doctor.Doctor', verbose_name=_('Врач'), on_delete=models.PROTECT, null=True,
                               related_name="to_doctor")
    problem = models.CharField(verbose_name=_(
        'Причина'), max_length=255, null=True, blank=True)
    duration_note = models.IntegerField(
        verbose_name=_('Длительность'), null=True, blank=True)
    center = models.ForeignKey('Center', on_delete=models.CASCADE, null=True, blank=True)
    clinic = models.ForeignKey('Clinic', on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(verbose_name=_(
        'Файлы к записи'), upload_to='files_to_notes/', null=True, blank=True)
    special_check = models.BooleanField(verbose_name=_(
        "Доп. проверка специалистов"), default=False)
    created_at = models.DateTimeField(verbose_name=_(
        'Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_(
        'Дата изменения'), auto_now=True, null=True)
    status = models.CharField(verbose_name=_(
        'Статус записи'), choices=NOTE_CHOICES, max_length=255, default=PROCESS)

    def __str__(self):
        return f'{self.title} - {self.user}'

    class Meta:
        verbose_name_plural = 'Записи'
        verbose_name = 'Запись'


class Center(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(verbose_name=_(
        'Название центра'), max_length=255, null=True)
    image = models.ImageField(verbose_name=_('Фото центра'), upload_to='centers_photos/', blank=True,
                              default='centers_photos/center_photo.jpg')
    rating = models.FloatField(verbose_name=_('Рейтинг центра'), max_length=5, default=5,
                               validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    admin = models.ForeignKey("User", on_delete=models.PROTECT, verbose_name=_(
        "Администратор центра"), null=True, related_name="admin")
    description = models.TextField(verbose_name=_(
        'Описание центра'), blank=True, null=True, max_length=550)
    is_required = models.BooleanField(
        verbose_name=_('Статус подтверждения'), default=False)
    number = models.CharField(verbose_name=_(
        'Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_(
        'Электронный адрес'), max_length=100, unique=True, null=True)
    employees = models.ManyToManyField(to="auth_doctor.Doctor", verbose_name=_(
        'Сотрудники'), related_name="employees")
    supported_diseases = models.ManyToManyField(
        "Disease", verbose_name=_('Поддерживаемые заболевания'))
    country = models.ForeignKey(
        'Country', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    observed = models.IntegerField(verbose_name=_("Наблюдается"), default=100)
    observed_after = models.IntegerField(verbose_name=_("Наблюдалось"), default=100)
    city = models.ForeignKey("City", on_delete=models.PROTECT, verbose_name=_("Город"), default=None)
    address = models.CharField(verbose_name=_('Адрес'), max_length=100, unique=True, null=True)
    lng = models.DecimalField(verbose_name=_("Долгота"), max_digits=6,  decimal_places=4, default=0)
    lat = models.DecimalField(verbose_name=_("Широта"), max_digits=6, decimal_places=4, default=0)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата Изменения'), auto_now=True, null=True)
    review_date = models.DateTimeField(
        null=True, verbose_name=_("Предполагаемая дата и время интервью"))
    review_passed = models.BooleanField(_("Собеседование пройдено"), null=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Центры'
        verbose_name = 'Центр'


class Clinic(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(verbose_name=_('Название Клиники'), max_length=100)
    admin = models.ForeignKey("User", on_delete=models.CASCADE, verbose_name=_("Администартор"), null=True, related_name="admin_clinic")
    is_required = models.BooleanField(
        verbose_name=_('Статус подтверждения'), default=False)
    rating = models.FloatField(verbose_name=_('Рейтинг клиники'), default=5,
                               validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    description = models.TextField(verbose_name=_(
        'Описание клиники'), blank=True, null=True, max_length=550)
    image = models.ImageField(verbose_name=_('Фото клиники'), upload_to='clinics_photos/',
                              default='centers_photos/clinic_photo.jpg', blank=True)
    number = models.CharField(verbose_name=_(
        'Номер'), max_length=30, unique=True)
    email = models.CharField(verbose_name=_(
        'Электронный адрес'), max_length=100, unique=True)
    employees = models.ManyToManyField(to="auth_doctor.Doctor", verbose_name=_(
        'Сотрудники'), related_name="clinic_employees")
    supported_diseases = models.ManyToManyField('Disease', verbose_name="Изученные заболевания")
    country = models.ForeignKey('Country', on_delete=models.PROTECT, verbose_name=_('Страна'))
    city = models.ForeignKey("City", on_delete=models.PROTECT, verbose_name=_("Город"), default=None)
    address = models.CharField(verbose_name=_(
        'Адрес'), max_length=100, unique=True)
    created_at = models.DateTimeField(
        verbose_name=_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(
        verbose_name=_('Дата Изменения'), auto_now=True)
    center = models.ForeignKey(
        Center, verbose_name="Центры", null=True, on_delete=models.CASCADE)
    review_date = models.DateTimeField(
        null=True, verbose_name="Предполагаемая дата и время интервью")
    review_passed = models.BooleanField(_("Собеседование пройдено"), null=True)
    verification_code = models.PositiveIntegerField(
        verbose_name=_('СМС код подтверждения'), default=1)
    reset_code = models.PositiveIntegerField(
        _('Код для сброса пароля'), default=1)
    email_verification_code = models.PositiveIntegerField(
        _('Код для привязки почты к аккаунту'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Клиники'
        verbose_name = 'Клиника'


class Url_Params(models.Model):
    parameter = models.CharField(verbose_name=_('Ссылка'), max_length=50, )
    group = models.ForeignKey('Group', verbose_name=_(
        'Группа'), on_delete=models.CASCADE, null=True)

    def save(self):
        self.parameter = get_random_string(length=50)
        super(Url_Params, self).save()

    def __str__(self):
        return self.parameter

    class Meta:
        verbose_name_plural = 'Ссылки для регистрации'
        verbose_name = 'Ссылку'


class EmailCode(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    code = models.IntegerField()
    email = models.CharField(verbose_name=_(
        'Электронный адрес'), max_length=100, unique=True, null=True)


class NumberCode(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    code = models.IntegerField()
    number = models.CharField(verbose_name=_(
        'Номер'), max_length=30, unique=True, null=True)


class Country(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    cities = models.ManyToManyField("City", verbose_name=_("Города"))
    name = models.CharField(verbose_name=_(
        'Название страны'), max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Страны'
        verbose_name = 'Страна'

class City(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(verbose_name=_("Название страны"), max_length=255, unique=True)

    def __str__(self):
        return self.name 

    class Meta:
        verbose_name_plural = 'Города'
        verbose_name = 'Город'



class News(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    title = models.CharField(verbose_name=_(
        'Заголовок новости'), max_length=40, null=True, blank=True)
    text = models.TextField(verbose_name=_(
        'Текст новости'), max_length=500, null=True, blank=True)
    image = models.ImageField(verbose_name=_('Фото к новости'), default='news_photos/news_photo.jpg',
                              upload_to='news_photos/')
    center = models.ForeignKey('Center', verbose_name=_(
        'Центр'), on_delete=models.SET_NULL, null=True, blank=True)
    disease = models.ForeignKey('Disease', verbose_name=_('Заболевание'), on_delete=models.SET_NULL, null=True,
                                blank=True)
    created_at = models.DateTimeField(verbose_name=_(
        'Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_(
        'Дата обновления'), auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Новости'
        verbose_name = 'Новость'

    def __str__(self):
        return str(self.title)


class Like(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    news = models.ForeignKey('News', verbose_name=_(
        'Новость'), on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name=_(
        'Пользователь'), on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'{self.user} - {self.news}'


class Saved(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, null=True, blank=True)
    news = models.ForeignKey('News', verbose_name=_(
        'Новость'), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Сохраненное'
        verbose_name = 'Сохранение'

    def __str__(self):
        return f'{self.user} - {self.news}'


class Disease(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Заболевания'
        verbose_name = 'Заболевание'
