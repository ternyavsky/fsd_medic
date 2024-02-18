from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import Country, Center, Clinic, City, BaseModel


# Create your models here.
class Doctor(AbstractBaseUser, BaseModel):
    main_status = models.BooleanField(default=False, null=True, blank=True)
    online = models.BooleanField(default=False, blank=True, null=True)
    # Любой сотрудник центра
    first_name = models.CharField(verbose_name=_("Имя"), max_length=50, null=True)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=50, null=True)
    number = models.CharField(verbose_name=_("Номер телефона"), max_length=30)
    email = models.CharField(verbose_name=_("Почта"), max_length=220, null=True, blank=True)
    image = models.ImageField(verbose_name=_('Фотография Пользователья'), upload_to='users_photos/', blank=True,
                              default='users_photos/AccauntPreview.png')
    middle_name = models.CharField(verbose_name="Отчетсво", max_length=50)
    country = models.CharField(verbose_name=_('Страна'), max_length=255, null=True, blank=True)
    city = models.CharField(verbose_name=_('Город'), max_length=255, null=True, blank=True)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name=_(
        "Центр, в котором зарегистрирован врач"))
    clinic = models.ForeignKey(Clinic, null=True, on_delete=models.CASCADE, verbose_name=_(
        "Клиника, где врач работает"), blank=True)
    address = models.CharField(max_length=200, verbose_name=_("Адрес"))
    specialization = models.CharField(
        max_length=200, verbose_name=_("Специальность/должность"))
    work_experience = models.DecimalField(verbose_name=_(
        "Опыт работы, лет"), max_digits=3, decimal_places=1)
    registration_date = models.DateTimeField(auto_now_add=True)
    review_date = models.DateTimeField(
        null=True, verbose_name="Предполагаемая дата и время интервью" ,blank=True)
    review_passed = models.BooleanField(_("Собеседование пройдено"), null=True)
    verification_code = models.PositiveIntegerField(
        verbose_name=_('СМС код подтверждения'), default=1)
    reset_code = models.PositiveIntegerField(
        _('Код для сброса пароля'), default=1)
    email_verification_code = models.PositiveIntegerField(
        _('Код для привязки почты к аккаунту'), default=0)

    USERNAME_FIELD = 'number'
    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def __str__(self):
        return f"{self.id}_{self.first_name}_{self.last_name}"



class LinkToInterview(BaseModel):
    link = models.CharField(verbose_name=_(
        "Ссылка на интервью"), max_length=220, unique=True)
    used = models.BooleanField(_("Использована"), default=False)

    class Meta:
        verbose_name = "Интервью"
        verbose_name_plural = "Интервью"

    def __str__(self):
        return f"{self.link}"


class Interview(BaseModel):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, verbose_name=_("Врач"))
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, null=True, verbose_name=_("Клиника"))
    center = models.ForeignKey(Center, on_delete=models.CASCADE, null=True, verbose_name=_("Центр"))
    link = models.ForeignKey(LinkToInterview, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.doctor | self.clinic | self.center}"
