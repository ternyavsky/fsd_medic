import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod


class UserManager(BaseUserManager):

    def create_user(self, number, email, password=None,
                    commit=True):
        email_name = email.strip().rsplit("@", 1)[0] + str(random.randrange(start=1, stop=9))
        login = email_name

        user = self.model(login=login, number=number, email=self.normalize_email(email), password=password)

        user_group = Groups.objects.get(name='Пользователи')
        user_group.number_of_people += 1
        user_group.save(update_fields=['number_of_people'])
        user.group_id = user_group.id

        user.set_password(password)
        if commit:
            user.save()
        return user

    def update_user(self, user, center=None, is_patient=None):
        if is_patient:
            user_group = Groups.objects.get(name='Пациенты')
            last_user_group = Groups.objects.get(name='Пользователи')
            user_group.number_of_people += 1
            user_group.save(update_fields=['number_of_people'])
            last_user_group.number_of_people -= 1
            last_user_group.save(update_fields=['number_of_people'])
            user.group_id = user_group.id
            user.is_required = True
            user.center_id = center.id
            user.save(update_fields=["center_id", "is_required", "group_id", "updated_at"])
            return user

        user.is_required = True
        user.center_id = center.id
        user.country_id = center.country_id
        user.save(update_fields=["center_id", "is_required", "updated_at"])
        return user

    def create_superuser(self, first_name, last_name, email, number, password=None):
        email_name = email.strip().rsplit("@", 1)[0] + str(random.randrange(start=1, stop=9))
        login = email_name
        superuser = self.model(login=login, number=number, email=email, first_name=first_name, last_name=last_name)
        superuser.set_password(password)
        superuser.is_staff = True
        superuser.is_required = True
        superuser_group = Groups.objects.get(name='Администраторы')
        superuser_group.number_of_people += 1
        superuser_group.save(update_fields=['number_of_people'])
        superuser.group_id = superuser_group.id
        superuser.save()
        return superuser


class User(AbstractBaseUser):
    login = models.CharField(verbose_name=_('Логин'), max_length=50, blank=True, unique=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False)
    group = models.ForeignKey('Groups', verbose_name=_('Группа'), on_delete=models.CASCADE, default='2', )
    is_staff = models.BooleanField(verbose_name=_('Статус персонала'), default=False)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, unique=True)
    first_name = models.CharField(verbose_name=_('Имя'), max_length=20, null=True, blank=True)
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=30, null=True, blank=True)
    birthday = models.DateField(verbose_name=_('День рождения'), null=True, blank=True)
    country = models.ForeignKey('Countries', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    city = models.CharField(verbose_name=_('Город'), max_length=50, blank=True, null=True)
    center = models.ForeignKey('Centers', verbose_name=_('Центр'), on_delete=models.PROTECT, null=True)
    desease = models.ForeignKey('Desease', verbose_name=_('Заболевание'), on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата изменения'), auto_now=True)
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
        ordering = ['-created_at']


class Groups(models.Model):
    name = models.CharField(verbose_name=_('Название Группы'), max_length=100, null=True)
    number_of_people = models.IntegerField(verbose_name=_('Количество людей'), default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Группы'


class Centers(models.Model):
    name = models.CharField(verbose_name=_('Название Центра'), max_length=100, null=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, unique=True, null=True)
    employees_number = models.IntegerField(verbose_name=_('Число Сотрудников'), null=True)
    country = models.ForeignKey('Countries', on_delete=models.PROTECT, verbose_name=_('Страна'), null=True)
    city = models.CharField(verbose_name=_('Город'), max_length=50, blank=True, null=True)
    address = models.CharField(verbose_name=_('Адрес'), max_length=100, unique=True, null=True)
    coordinate_latitude = models.FloatField(verbose_name=_('Широта'), null=True)
    coordinate_longitude = models.FloatField(verbose_name=_('Долгата'), null=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата Изменения'), auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Центры'


class Url_Params(models.Model):
    parameter = models.CharField(max_length=50, )
    user = models.OneToOneField('User', on_delete=models.SET_NULL,
                                null=True, blank=True)
    interview = models.OneToOneField('Interviews', on_delete=models.SET_NULL,
                                     null=True, blank=True)


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


class Interviews(models.Model):
    type = models.CharField(verbose_name=_('Тип интервью'), max_length=30, null=True)
    date = models.DateTimeField(verbose_name=_('Дата интервью'), null=True)
    first_name = models.CharField(verbose_name=_('Имя'), max_length=30, null=True)
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=40, null=True)
    number = models.CharField(verbose_name=_('Номер'), max_length=30, unique=True, null=True)
    email = models.CharField(verbose_name=_('Электронный адрес'), max_length=100, unique=True, null=True)
    is_required = models.BooleanField(verbose_name=_('Статус подтверждения'), default=False)
    application = models.CharField(verbose_name=_('Приложение'), max_length=30, null=True, )
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата обновления'), auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Интервью'

    def __str__(self):
        return str(self.date)


class News(models.Model):
    title = models.CharField(verbose_name=_('Заголовок новости'), max_length=40, null=True, blank=True)
    text = models.TextField(verbose_name=_('Текст новости'), max_length=500, null=True, blank=True)
    image = models.ImageField(verbose_name=_('Фото к новости'), upload_to='news_photos/')
    center = models.ForeignKey('Centers', verbose_name=_('Центр'), on_delete=models.SET_NULL, null=True, blank=True)
    desease = models.ForeignKey('Desease', verbose_name=_('Заболевание'), on_delete=models.SET_NULL, null=True,
                                blank=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата обновления'), auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Like(models.Model):
    news = models.ForeignKey('News', verbose_name=_('Новость'), on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name=_('Пользователь'), on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Лайки'

    def __str__(self):
        return f'{self.user} - {self.news}'


class Country_Codes(models.Model):
    country = models.CharField(verbose_name=_('Название страны'), max_length=30)
    code = models.IntegerField(verbose_name=_('Код страны'))


class Saved(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, null=True, blank=True)
    news = models.ForeignKey('News', verbose_name=_('Новость'), on_delete=models.CASCADE, null=True, blank=True)


class Desease(models.Model):
    pass
