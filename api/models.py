import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod


class UserManager(BaseUserManager):

    def create_user(self, number, password, center_id, is_patient, disese_id):

        user = self.model(login=number, is_required=True, number=number)

        try:
            user_group = Groups.objects.get(name='Пользователи')
        except:
            user_group = Groups(name='Пользователи')
            user_group.save()
        user_group.number_of_people += 1
        user_group.save(update_fields=['number_of_people'])
        user.group_id = user_group.id

        user.center_id = center_id

        user.disease_id = disese_id

        user.country_id = Centers.objects.get(id=center_id).country_id

        user.set_password(password)

        user.save()
        return user

    def update_user(self, user, number=None, email=None, password=None, first_name=None, last_name=None, surname=None,
                    center_id=None, is_patient=None, disease_id=None):
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

        user.save(update_fields=updated_fields)
        return user

    def create_superuser(self, first_name, last_name, surname=None, email=None, number=None, password=None):
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
    city = models.CharField(verbose_name=_('Город'), max_length=50, blank=True, null=True)
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
    last_name = models.CharField(verbose_name=_('Фамилия'), max_length=40, null=True, blank=True)
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
    disease = models.ForeignKey('Disease', verbose_name=_('Заболевание'), on_delete=models.SET_NULL, null=True,
                                blank=True)
    created_at = models.DateTimeField(verbose_name=_('Дата создания'), auto_now_add=True, null=True)
    updated_at = models.DateTimeField(verbose_name=_('Дата обновления'), auto_now=True, null=True)

    class Meta:
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title


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

    class Meta:
        verbose_name_plural = 'Сохраненное'
    def __str__(self):
        return f'{self.user} - {self.news}'

class Disease(models.Model):
    pass

    class Meta:
        verbose_name_plural = 'Заболевания'
        verbose_name = 'Заболевание'


class Images(models.Model):
    title = models.CharField(verbose_name=_('Описание фотографии'), max_length=20)
    image = models.ImageField(verbose_name=_('Фотография Сайта'), upload_to='site_photos/', blank=True)
