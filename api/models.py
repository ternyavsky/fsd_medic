from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django_mysql.models import ListCharField

from .choices import NOTE_CHOICES, PROCESS
from .managers.base_manager import SimpleManager
from .managers.news_manager import NewsManager


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"), auto_now_add=True, blank=True, null=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Дата изменения"), auto_now=True, blank=True, null=True
    )

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(
        self,
        password,
        email=None,
        first_name=None,
        last_name=None,
        birthday=None,
        *args,
        **kwargs,
    ):
        user = self.model(email=email)
        user.birthday = birthday
        user.password = make_password(password)
        # это UserManager(BaseUserManager)

        user.save()
        return user

    def create_superuser(self, number, email, first_name, last_name, password=None):
        superuser = self.model(
            number=number, email=email, first_name=first_name, last_name=last_name
        )

        superuser.is_staff = True
        superuser.is_required = False
        superuser.set_password(password)
        superuser.save()
        return superuser


class User(AbstractBaseUser, BaseModel):
    is_required = models.BooleanField(
        verbose_name=_("Статус подтверждения"), default=False, blank=True
    )
    is_staff = models.BooleanField(verbose_name=_("Статус персонала"), default=False)
    online = models.BooleanField(_("Онлайн"), default=False)
    sex = models.CharField(_("Пол"), max_length=255, default=None, null=True)
    clinic = models.ForeignKey(
        "Clinic",
        on_delete=models.PROTECT,
        verbose_name=_("Клиника"),
        null=True,
        related_name="user_clinic",
    )
    centers = models.ManyToManyField("Center", verbose_name=_("Центр"), blank=True)
    disease = models.ManyToManyField(
        "Disease", verbose_name=_("Заболевания"), blank=True
    )
    number = models.CharField(
        verbose_name=_("Номер"), max_length=30, unique=True, null=True, blank=True
    )
    email = models.CharField(
        verbose_name=_("Электронный адрес"),
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_("Имя"), max_length=20, null=True, blank=True
    )
    last_name = models.CharField(
        verbose_name=_("Фамилия"), max_length=30, null=True, blank=True
    )
    surname = models.CharField(
        verbose_name=_("Отчество"), max_length=40, null=True, blank=True
    )
    interest = models.ForeignKey(
        "Disease",
        verbose_name=_("Интерес к заболеванию"),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="interest",
    )
    birthday = models.DateField(verbose_name=_("Дата рождения"), null=True, blank=True)
    image = models.ImageField(
        verbose_name=_("Фотография Пользователья"),
        upload_to="users_photos/",
        blank=True,
        default=None,
    )

    country = models.ForeignKey(
        "Country",
        verbose_name=_("Страна"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        "City",
        verbose_name=_("Город"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    address = models.CharField(
        verbose_name=_("Адрес"), max_length=100, unique=False, null=True
    )
    verification_code = models.PositiveIntegerField(
        verbose_name=_("СМС код подтверждения"), default=1
    )
    reset_code = models.PositiveIntegerField(_("Код для сброса пароля"), default=1)
    number_verification_code = models.PositiveIntegerField(
        _("Код для привязки номера к аккаунту"), default=1
    )

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return str(self.number)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователи"


class Subscribe(BaseModel):
    clinic = models.ForeignKey(
        "Clinic", on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=True, blank=True)
    main_doctor = models.ForeignKey(
        "auth_doctor.Doctor", on_delete=models.CASCADE, null=True, blank=True
    )

    objects = SimpleManager()

    def __str__(self):
        return f"Subscribe for user {self.user.number}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"


class Access(BaseModel):
    user = models.ForeignKey(
        "User",
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        related_name="user",
    )
    access_accept = models.ManyToManyField(
        "User", verbose_name=_("Доступ (принятые)"), related_name="access"
    )
    access_unaccept = models.ManyToManyField(
        "User", verbose_name=_("Доступ (непринятые)"), related_name="unaccept"
    )

    def __str__(self):
        return f"Доступ пользователя {self.user}"

    class Meta:
        verbose_name_plural = "Доступ"
        verbose_name = "Доступ"


class Note(BaseModel):
    user = models.ForeignKey(
        "User",
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField(verbose_name=_("Название записи"), max_length=255)
    online = models.BooleanField(verbose_name=_("Онлайн"), default=False)
    time_start = models.DateTimeField(verbose_name=_("Начало "), null=True, blank=True)
    time_end = models.DateTimeField(verbose_name=_("Конец"), null=True, blank=True)
    notify = models.DateTimeField(
        verbose_name=_("Время уведомления о записи"), null=True, blank=True
    )
    doctors = models.ManyToManyField("auth_doctor.Doctor", verbose_name=_("Врачи"))
    problem = models.CharField(
        verbose_name=_("Причина"), max_length=255, null=True, blank=True
    )
    duration_note = models.IntegerField(
        verbose_name=_("Длительность"), null=True, blank=True
    )
    center = models.ForeignKey(
        "Center", on_delete=models.CASCADE, null=True, blank=True
    )
    clinic = models.ForeignKey(
        "Clinic", on_delete=models.CASCADE, null=True, blank=True
    )
    file = models.FileField(
        verbose_name=_("Файлы к записи"),
        upload_to="files_to_notes/",
        null=True,
        blank=True,
    )
    special_check = models.BooleanField(
        verbose_name=_("Доп. проверка специалистов"), default=False
    )
    status = models.CharField(
        verbose_name=_("Статус записи"),
        choices=NOTE_CHOICES,
        max_length=255,
        default=PROCESS,
    )

    def __str__(self):
        return f"{self.title} - {self.user}"

    class Meta:
        verbose_name_plural = "Записи"
        verbose_name = "Запись"


class Center(AbstractBaseUser):
    USERNAME_FIELD = "number"
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(
        verbose_name=_("Название центра"), max_length=255, null=True
    )
    password = models.CharField(_("Пароль"), max_length=128, null=True)
    last_login = models.DateTimeField(_("Последний вход"), blank=True, null=True)
    image = models.ImageField(
        verbose_name=_("Фото центра"),
        upload_to="centers_photos/",
        blank=True,
        default="centers_photos/center_photo.jpg",
    )
    rating = models.FloatField(
        verbose_name=_("Рейтинг центра"),
        max_length=5,
        default=5,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    admin = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        verbose_name=_("Администратор центра"),
        null=True,
        related_name="admin",
    )
    description = models.TextField(
        verbose_name=_("Описание центра"), blank=True, null=True, max_length=550
    )
    is_required = models.BooleanField(
        verbose_name=_("Статус подтверждения"), default=False
    )
    number = models.CharField(
        verbose_name=_("Номер"), max_length=30, unique=True, null=True
    )
    email = models.CharField(
        verbose_name=_("Электронный адрес"), max_length=100, unique=True, null=True
    )
    employees = models.ManyToManyField(
        to="auth_doctor.Doctor", verbose_name=_("Сотрудники"), related_name="employees"
    )
    supported_diseases = models.ManyToManyField(
        "Disease", verbose_name=_("Поддерживаемые заболевания")
    )

    country = models.ForeignKey(
        "Country",
        verbose_name=_("Страна"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        "City",
        verbose_name=_("Город"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    observed = models.IntegerField(verbose_name=_("Наблюдается"), default=100)
    observed_after = models.IntegerField(verbose_name=_("Наблюдалось"), default=100)

    address = models.CharField(
        verbose_name=_("Адрес"), max_length=100, unique=True, null=True
    )
    lng = models.DecimalField(
        verbose_name=_("Долгота"), max_digits=6, decimal_places=4, default=0
    )
    lat = models.DecimalField(
        verbose_name=_("Широта"), max_digits=6, decimal_places=4, default=0
    )
    created_at = models.DateTimeField(
        verbose_name=_("Дата создания"), auto_now_add=True, null=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Дата Изменения"), auto_now=True, null=True
    )
    review_date = models.DateTimeField(
        null=True, verbose_name=_("Предполагаемая дата и время интервью")
    )
    review_passed = models.BooleanField(_("Собеседование пройдено"), null=True)

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    class Meta:
        verbose_name_plural = "Центры"
        verbose_name = "Центр"


class ClinicAdmin(BaseModel):
    firstname = models.CharField(_("Имя админа"), blank=True, max_length=220)
    surname = models.CharField(_("Фамилия админа"), blank=True, max_length=220)
    birthday = models.DateField(
        verbose_name=_("Дата рождения админа"), null=True, blank=True
    )
    lastname = models.CharField(_("Отчество админа"), blank=True, max_length=220)
    number = models.CharField(_("Номер админа"), blank=True, max_length=220)
    photo = models.ImageField(
        _("Фото админа"), upload_to="clinic_admin_photos/", default=None, blank=True
    )

    def __str__(self) -> str:
        return f"Администратор {self.firstname} {self.surname}"

    class Meta:
        verbose_name_plural = "Администраторы клиник"
        verbose_name = "Администратор клиники"


class Clinic(AbstractBaseUser, BaseModel):
    USERNAME_FIELD = "number"
    name = models.CharField(verbose_name=_("Название Клиники"), max_length=100)
    password = models.CharField(_("password"), max_length=128, null=True, blank=True)
    last_login = models.DateTimeField(_("last login"), blank=True, null=True)
    specialization = models.CharField(_("Специализация"), blank=True, max_length=220)
    workdays = ListCharField(
        base_field=models.CharField(max_length=2),
        size=7,
        max_length=(7 * 3),
        null=True,
        blank=True,
    )
    worktime = models.IntegerField(
        _("Время активности на сайте (в минутах)"), default=0
    )
    admin = models.ForeignKey(
        "ClinicAdmin",
        on_delete=models.CASCADE,
        verbose_name=_("Администартор"),
        null=True,
        blank=True,
        related_name="admin_clinic",
    )
    is_required = models.BooleanField(
        verbose_name=_("Статус подтверждения"), default=False
    )
    rating = models.FloatField(
        verbose_name=_("Рейтинг клиники"),
        default=5,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    description = models.TextField(
        verbose_name=_("Описание клиники"), blank=True, null=True, max_length=550
    )
    image = models.ImageField(
        verbose_name=_("Фото клиники"),
        upload_to="clinics_photos/",
        default="centers_photos/clinic_photo.jpg",
        blank=True,
    )
    number = models.CharField(verbose_name=_("Номер"), max_length=30, unique=True)
    email = models.CharField(
        verbose_name=_("Электронный адрес"), max_length=100, unique=True, default=None
    )
    employees = models.IntegerField(_("Кол-во сотрудников"), default=0)
    supported_diseases = models.ManyToManyField(
        "Disease", verbose_name="Изученные заболевания"
    )
    country = models.ForeignKey(
        "Country",
        verbose_name=_("Страна"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        "City",
        verbose_name=_("Город"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    address = models.CharField(verbose_name=_("Адрес"), max_length=100, unique=True)
    center = models.ForeignKey(
        Center, verbose_name="Центры", null=True, on_delete=models.CASCADE
    )
    verification_code = models.PositiveIntegerField(
        verbose_name=_("СМС код подтверждения"), default=1
    )
    reset_code = models.PositiveIntegerField(_("Код для сброса пароля"), default=1)
    email_verification_code = models.PositiveIntegerField(
        _("Код для привязки почты к аккаунту"), default=0
    )

    def __str__(self):
        return self.number

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    class Meta:
        verbose_name_plural = "Клиники"
        verbose_name = "Клиника"


class EmailCode(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    code = models.IntegerField()
    email = models.CharField(
        verbose_name=_("Электронный адрес"), max_length=100, unique=True, null=True
    )


class NumberCode(models.Model):
    id = models.BigAutoField(primary_key=True, db_index=True)
    code = models.IntegerField()
    number = models.CharField(
        verbose_name=_("Номер"), max_length=30, unique=True, null=True
    )


class Country(BaseModel):
    name = models.CharField(
        verbose_name=_("Название страны"), max_length=50, unique=True
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Страны"
        verbose_name = "Страна"


class City(BaseModel):
    name = models.CharField(
        verbose_name=_("Название страны"), max_length=255, unique=True
    )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Города"
        verbose_name = "Город"


class NewsImages(models.Model):
    image = models.ImageField(
        default="news_photos/news_photo.jpg",
        verbose_name=_("Фото к новости"),
        upload_to="news_photos/",
    )
    news = models.ForeignKey(
        "News",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="news_images",
    )


class NewsVideos(models.Model):
    video = models.FileField(
        verbose_name=_("Видео к новости"),
        upload_to="news_videos/",
        default="news_photos/news_photo.jpg",
    )
    news = models.ForeignKey(
        "News",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="news_videos",
    )


class News(BaseModel):
    title = models.CharField(
        verbose_name=_("Заголовок новости"), max_length=40, null=True, blank=True
    )
    text = models.TextField(
        verbose_name=_("Текст новости"), max_length=500, null=True, blank=True
    )
    clinic = models.ForeignKey(
        "Clinic",
        verbose_name=_("Клиника"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    disease = models.ForeignKey(
        "Disease",
        verbose_name=_("Заболевание"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    objects = NewsManager()

    class Meta:
        verbose_name_plural = "Новости"
        verbose_name = "Новость"

    def __str__(self):
        return str(self.title)


class Like(BaseModel):
    news = models.ForeignKey(
        "News", verbose_name=_("Новость"), on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "User", verbose_name=_("Пользователь"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name_plural = "Лайки"

    def __str__(self):
        return f"{self.user} - {self.news}"


class Saved(BaseModel):
    user = models.ForeignKey(
        "User",
        verbose_name=_("Пользователь"),
        on_delete=models.CASCADE,
    )
    news = models.ForeignKey(
        "News",
        verbose_name=_("Новость"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Сохраненное"
        verbose_name = "Сохранение"

    def __str__(self):
        return f"{self.user} - {self.news}"


class Disease(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = "Заболевания"
        verbose_name = "Заболевание"
