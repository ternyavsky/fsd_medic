from django.core.mail import send_mail
from dotenv import load_dotenv
import os
from rest_framework.response import Response
from rest_framework import status
import random
import requests
from fsd_medic.settings import BASE_DIR
import random
from api.models import Country
from celery import shared_task
from celery import Celery

app = Celery('tasks', broker="amqp://localhost", backend="redis://localhost")


load_dotenv(BASE_DIR / ".env")

@shared_task
def send_reset_sms(number, code):

    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number}&text=Вы+пытаетесь+восстановить+доступ+к+аккаунту+,+ваш+код+доступа+-+{code}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось')
        return True
    else:
        print(res)
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
def Send_email(user_email, message):
    send_mail(
        'Подтверждение почты',
        message,
        os.getenv("EM_HOST_USER"),
        [user_email],
        fail_silently=False,
    )

@shared_task
def send_sms(number, code):
    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number}&text=Регистрация+была+успешно+пройдена,+ваш+код+подтверждения+{code}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось')
        return True
    else:
        print("не отправилось")
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
        'Привязка почты к вашему аккаунту',
        f'Для подтверждения почты используйте этот код - {email_code}',
        os.getenv('EM_HOST_USER'),
        [user_email],
        fail_silently=False,
    )

def set_new_password(user, new_password):

    user.set_password(new_password)
    user.save()
