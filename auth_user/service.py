import os
import random

import requests
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from dotenv import load_dotenv

from fsd_medic.settings import BASE_DIR
from social.models import Notification

User = get_user_model()


load_dotenv(BASE_DIR / ".env")

key = os.getenv("API_KEY")
email = os.getenv("EMAIL")


@shared_task
def send_reset_sms(number, code):
    key = os.getenv("API_KEY")
    email = os.getenv("EMAIL")
    url = f"https://sms.ru/sms/send?api_id=0F9113E2-B4ED-8975-4BEA-B47ACCC656C6&to={number}&msg=Вы+пытаетесь+восстановить+доступ+к+аккаунту+,+ваш+код+доступа+-+{code}&json=1"
    res = requests.get(url)
    print(code)
    if res.status_code == 200:
        print("отправилось")
        return True
    else:
        return False


@shared_task
def send_reset_email(email, code):
    send_mail(
        "Восстановление пароля",
        f"Вы пытаетесь восстановить доступ к аккаунту, ваш код доступа - {code}",
        str(os.getenv("EM_HOST_USER")),
        [email],
        fail_silently=False,
    )


@shared_task
def send_email(user_email, code):
    send_mail(
        "Регистрация",
        f"Регистрация была успешно пройдена, ваш код подтверждения {code}",
        os.getenv("EM_HOST_USER"),
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_sms(number, code):
    key = os.getenv("API_KEY")
    email = os.getenv("EMAIL")
    url = f"https://sms.ru/sms/send?api_id=0F9113E2-B4ED-8975-4BEA-B47ACCC656C6&to={number}&msg=Код+для+привязки+номера+{code}&json=1"
    res = requests.get(url)
    print(code)
    if res.status_code == 200:
        print("отправилось")
        return True
    else:
        print("no send")
        return False


def generate_email_code():
    code = random.randrange(start=10000000, stop=99999999)
    return code


def generate_verification_code():
    code = random.randint(1000, 9999)
    return str(code)


@shared_task
def send_verification_email(email_code, user_email):
    send_mail(
        "Привязка почты к вашему аккаунту",
        f"Для подтверждения почты используйте этот код - {email_code}",
        os.getenv("EM_HOST_USER"),
        [user_email],
        fail_silently=False,
    )


@shared_task
def start_time_reminder(user, data):
    Notification.objects.create(
        user=User.objects.get(id=user), text=f"Напоминание о записи {data}"
    )


def set_new_password(user, new_password):
    user.set_password(new_password)
    user.save()
