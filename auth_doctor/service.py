from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from dotenv import load_dotenv
import os
from rest_framework.response import Response
from rest_framework import status
import random
import requests
from fsd_medic.settings import BASE_DIR
import random
from celery import shared_task
from celery import Celery

app = Celery('tasks', broker="amqp://localhost")


load_dotenv(BASE_DIR / ".env")


def generate_email_code():
    code = random.randrange(start=10000000, stop=99999999)
    return code


def generate_verification_code():
    code = random.randint(1000, 9999)
    return str(code)

@app.task
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

@app.task
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