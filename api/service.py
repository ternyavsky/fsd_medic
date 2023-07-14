from django.core.mail import send_mail
from dotenv import load_dotenv
import os
from rest_framework.response import Response
from rest_framework import status
import random
import requests
from fsd_medic.settings import BASE_DIR
import random
from .models import Countries



load_dotenv(BASE_DIR / ".env")

def send_reset_sms(number, code):

    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number}&text=Вы+пытаетесь+восстановить+доступ+к+аккаунту+на+www.pre_recover.com+,+ваш+код+доступа+-+{code}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось')
        return True
    else:
        return False

def send_reset_email(email, code):
    send_mail(
        "Восстановление пароля",
        f"Вы пытаетесь восстановить доступ к аккаунту на www.pre_recover.com , ваш код доступа - {code}",
        str(os.getenv("EM_HOST_USER")),
        [email],
        fail_silently=False,
    )




def Send_email(user_email, message):
    send_mail(
        'Подтверждение почты',
        message,
        os.getenv("EM_HOST_USER"),
        [user_email],
        fail_silently=False,
    )


def send_sms(number, code):
    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number}&text=Регистрация+была+успешно+пройдена,+ваш+код+подтверждения+{code}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось')
        return True
    else:
        return False




def create_or_delete(classmodel, **kwargs):
    obj, created = classmodel.objects.get_or_create(**kwargs)

    if created:
        obj.save()
        return Response({'result': f'объект {classmodel.__name__} создан'}, status=status.HTTP_200_OK)
    else:
        obj.delete()
        return Response({'result': f'объект {classmodel.__name__} удален'}, status=status.HTTP_200_OK)
    
def generate_email_code():
    code = random.randrange(start=10000000, stop=99999999)
    return code


def generate_verification_code():
    code = random.randint(1000, 9999)
    return str(code)