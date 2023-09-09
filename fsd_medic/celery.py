import os

from . import settings
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fsd_medic.settings")

app = Celery("fsd_medic")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
