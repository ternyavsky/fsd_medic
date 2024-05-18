from django.db import models

from api.models import BaseModel

# Create your models here.


class Balance(BaseModel):
    clinic = models.ForeignKey("api.Clinic", on_delete=models.CASCADE, null=True)
