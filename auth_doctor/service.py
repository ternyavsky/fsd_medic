import os
import random

import requests
from celery import Celery, shared_task
from django.core.mail import send_mail
from dotenv import load_dotenv

from fsd_medic.settings import BASE_DIR


load_dotenv(BASE_DIR / ".env")


def generate_email_code():
    code = random.randrange(start=10000000, stop=99999999)
    return code


def generate_verification_code():
    code = random.randint(1000, 9999)
    return str(code)


@shared_task
def send_reset_sms(number, code):
    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number}&text=Вы+пытаетесь+восстановить+доступ+к+аккаунту+,+ваш+код+доступа+-+{code}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось', code)
        return True
    else:
        print(res)
        return False


@shared_task
def send_reset_email(email, code):
    print(code)
    send_mail(
        "Восстановление пароля",
        f"Вы пытаетесь восстановить доступ к аккаунту, ваш код доступа - {code}",
        str(os.getenv("EM_HOST_USER")),
        [email],
        fail_silently=False,
    )


def doctor_set_new_password(doctor, new_password):
    doctor.set_password(new_password)
    doctor.save()


def clinic_set_new_password(clinic, new_password):
    clinic.set_password(new_password)
    clinic.save()
