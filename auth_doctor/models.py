from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models import Country, Center


# Create your models here.

class Doctor(models.Model):
    # врачи
    id = models.BigAutoField(primary_key=True, db_index=True)
    phone_number = models.CharField(verbose_name=_("Номер телефона"), max_length=220)
    first_name = models.CharField(verbose_name=_("Имя"), max_length=220)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=220)
    city = models.CharField(verbose_name=_("Город"), max_length=220)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    center = models.ForeignKey(Center, on_delete=models.CASCADE, verbose_name="Центр, в котором зарегистрирован врач")
    is_approved = models.BooleanField()


class LinkToInterview(models.Model):
    id = models.BigAutoField(db_index=True, primary_key=True)
    link = models.CharField(verbose_name=_("Ссылка на интервью"), max_length=220)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
