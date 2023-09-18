from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import Country, Center, Clinic

from django.contrib.auth.models import AbstractUser


# Create your models here.
class Doctor(AbstractUser):
    # Любой сотрудник центра
    phone_number = models.CharField(verbose_name=_("Номер телефона"), max_length=12)
    middle_name = models.CharField(verbose_name="Отчетсво", max_length=50)
    city = models.CharField(verbose_name=_("Город"), max_length=220)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="Центр, в котором зарегистрирован врач")
    clinic = models.ForeignKey(Clinic, null=True, on_delete=models.CASCADE, verbose_name="Клиника, где врач работает")
    address = models.CharField(max_length=200, verbose_name="Адрес")
    specialization = models.CharField(max_length=200, verbose_name="Специальность/должность")
    work_experience = models.DecimalField(verbose_name="Опыт работы, лет", max_digits=3, decimal_places=1)
    registration_date = models.DateTimeField(auto_now_add=True)
    interview_date_plan = models.DateTimeField(null=True,
                                               verbose_name="Время, когда пользователь хочет, чтобы было проведено собеседование")
    # флаги
    is_approved_for_interview = models.BooleanField(default=False)
    is_approved_for_work = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"

    def __str__(self):
        return f"{self.id}_{self.first_name}_{self.last_name}"


class LinkToInterview(models.Model):
    id = models.BigAutoField(db_index=True, primary_key=True)
    link = models.CharField(verbose_name=_("Ссылка на интервью"), max_length=220)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
