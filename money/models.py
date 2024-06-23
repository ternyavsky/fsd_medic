from django.db import models

from django.utils.translation import gettext_lazy as _
from api.models import BaseModel

# Create your models here.


class Balance(BaseModel):
    clinic = models.ForeignKey("api.Clinic", on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(
        verbose_name=_("Баланс"), max_digits=10, decimal_places=2, default=0
    )
