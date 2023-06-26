import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod


class UserManager(BaseUserManager):

    def create_user(self, number, password, group_name, center_id, email=None, first_name=None, last_name=None,
                    is_patient=None, disease_id=None):
        user = self.model(login=number, number=number)

        user_group = Groups.objects.get(name=group_name)
        user_group.number_of_people += 1
        user_group.save(update_fields=['number_of_people'])
        user.group_id = user_group.id

        user.center_id = center_id

        user.country_id = Centers.objects.get(id=center_id).country_i

        user.set_password(password)

        if group_name == 'Пользователи':
            user.disease_id = disease_id
            user.is_patient = is_patient
            user.is_required = True
        else:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_required = False

        user.save()
        return user

    def update_user(self, user, number=None, email=None, password=None, first_name=None, last_name=None, surname=None,
                    is_patient=None,
                    center_id=None, disease_id=None):
        updated_fields = ["updated_at"]
        if is_patient is not None:
            if is_patient:
                user_group = Groups.objects.get(name='Пациенты')
                last_user_group = Groups.objects.get(name='Пользователи')
                user.group_id = user_group.id
                user.is_patient = True
                updated_fields += "is_patient"
            else:
                user_group = Groups.objects.get(name='Пользователи')
                last_user_group = Groups.objects.get(name='Пациенты')
            user_group.number_of_people += 1
            user_group.save(update_fields=['number_of_people'])
            last_user_group.number_of_people -= 1
            last_user_group.save(update_fields=['number_of_people'])

        if center_id is not None:
            user.center_id = center_id
            user.country_id = Centers.objects.get(id=center_id).country_id
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
        superuser = self.model(login=number, number=number, email=email, first_name=first_name, last_name=last_name)

        superuser_group = Groups.objects.get(name='Администраторы')
        superuser_group.number_of_people += 1
        superuser_group.save(update_fields=['number_of_people'])
        superuser.group_id = superuser_group.id

        superuser.is_staff = True
        superuser.is_required = False

        superuser.set_password(password)

        superuser.save()
        return superuser


class User(AbstractBaseUser):
    login = models.CharField(verbose_name=_('Логин'), max_length=50, blank=True, null=True, unique=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False, blank=True)
    is_staff = models.BooleanField(verbose_name=_('Статус персонала'), default=False)
    group = models.ForeignKey('Groups', verbose_name=_('Группа'), on_delete=models.CASCADE, )
    center = models.ForeignKey('Centers', verbose_name=_('Центр'), on_delete=models.PROTECT, null=True)
    disease = models.ForeignKey('Disease', verbose_name=_('Заболевание'), on_delete=models.SET_NULL, null=True)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, blank=True, null=True)
    first_name = models.CharField(verbose_name=_('Имя'), max_length=20, null=True, blank=True)
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=30, null=True, blank=True)
    surname = models.CharField(verbose_name=_('Отчество'), max_length=40, null=True, blank=True)
    birthday = models.DateField(verbose_name=_('День рождения'), null=True, blank=True)
    image = models.ImageField(verbose_name=_('Фотография Пользователья'), upload_to='users_photos/', blank=True,
                              default='media/site_photos/AccauntPreview.png')
    country = models.ForeignKey('Countries', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    city = models.CharField(verbose_name=_('Город'), max_length=50, null=True)
    address = models.CharField(verbose_name=_('Адрес'), max_length=100, unique=False, null=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, blank=True, null=True, )
    updated_at = models.DateTimeField(verbose_name=_('Дата изменения'), auto_now=True, blank=True, null=True, )
    USERNAME_FIELD = 'login'

    objects = UserManager()

    def __str__(self):
        return self.login

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
        ordering = ['-created_at']


class Groups(models.Model):
    name = models.CharField(verbose_name=_('Название Группы'), max_length=100, null=True)
    number_of_people = models.IntegerField(verbose_name=_('Количество людей'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'Группу'


class Centers(models.Model):
    name = models.CharField(verbose_name=_('Название Центра'), max_length=100, null=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, unique=True, null=True)
    employees_number = models.IntegerField(verbose_name=_('Число Сотрудников'), null=True)
    country = models.ForeignKey('Countries', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    city = models.CharField(verbose_name=_('Город'), max_length=50, blank=True, null=True)
    address = models.CharField(verbose_name=_('Адрес'), max_length=100, unique=True, null=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата Изменения'), auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Центры'
        verbose_name = 'Центр'


class Clinics(models.Model):
    name = models.CharField(verbose_name=_('Название Клиники'), max_length=100, null=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, unique=True, null=True)
    employees_number = models.IntegerField(verbose_name=_('Число Сотрудников'), null=True)
    country = models.ForeignKey('Countries', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    city = models.CharField(verbose_name=_('Город'), max_length=50, blank=True, null=True)
    address = models.CharField(verbose_name=_('Адрес'), max_length=100, unique=True, null=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата Изменения'), auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Клиники'
        verbose_name = 'Клинику'


class Url_Params(models.Model):
    parameter = models.CharField(verbose_name=_('Ссылка'), max_length=50, )
    group = models.ForeignKey('Groups', verbose_name=_('Группа'), on_delete=models.CASCADE, null=True)

    def save(self):
        self.parameter = get_random_string(length=50)
        super(Url_Params, self).save()

    

    def __str__(self):
        return self.parameter

    class Meta:
        verbose_name_plural = 'Ссылки для регистрации'
        verbose_name = 'Ссылку'


class Email_Codes(models.Model):
    code = models.IntegerField()
    user = models.OneToOneField('User', on_delete=models.SET_NULL,
                                null=True, blank=True)
    interview = models.OneToOneField('Interviews', on_delete=models.SET_NULL,
                                     null=True, blank=True)


class Countries(models.Model):
    name = models.CharField(verbose_name=_('Название страны'), max_length=50, unique=True)
    number_code = models.CharField(verbose_name=_('Телефонный код страны'), max_length=15, null=True)
    number_length = models.CharField(verbose_name=_('Длина номера'), max_length=2, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Страны'
        verbose_name = 'Страну'


class Country_Codes(models.Model):
    country = models.CharField(verbose_name=_('Название страны'), max_length=30)
    code = models.IntegerField(verbose_name=_('Код страны'))

    class Meta:
        verbose_name_plural = 'Номерные коды'
        verbose_name = 'Номерной код'


class Interviews(models.Model):
    type = models.CharField(verbose_name=_('Тип интервью'), max_length=30, null=True)
    date = models.DateTimeField(verbose_name=_('Дата интервью'), null=True)
    first_name = models.CharField(verbose_name=_('Имя'), max_length=30, null=True)
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=40, null=True, blank=True)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, unique=True, null=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False)
    application = models.CharField(verbose_name=_('Приложение'), max_length=30, null=True, )
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата обновления'), auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Интервью'
        verbose_name = 'Интервью'

    def __str__(self):
        return str(self.date)


class News(models.Model):
    title = models.CharField(verbose_name=_('Заголовок новости'), max_length=40, null=True, blank=True)
    text = models.TextField(verbose_name=_('Текст новости'), max_length=500, null=True, blank=True)
    image = models.ImageField(verbose_name=_('Фото к новости'), upload_to='news_photos/')
    center = models.ForeignKey('Centers', verbose_name=_('Центр'), on_delete=models.SET_NULL, null=True, blank=True)
    disease = models.ForeignKey('Disease', verbose_name=_('Заболевание'), on_delete=models.SET_NULL, null=True,
                                blank=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата обновления'), auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Новости'
        verbose_name = 'Новость'

    def __str__(self):
        return self.title


class Like(models.Model):
    news = models.ForeignKey('News', verbose_name=_('Новость'), on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name=_('Пользователь'), on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'{self.user} - {self.news}'


class Saved(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, null=True, blank=True)
    news = models.ForeignKey('News', verbose_name=_('Новость'), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Сохраненное'
        verbose_name = 'Сохранение'

    def __str__(self):
        return f'{self.user} - {self.news}'


class Disease(models.Model):
    pass

    class Meta:
        verbose_name_plural = 'Заболевания'
        verbose_name = 'Заболевание'
