from django.core.mail import send_mail
from dotenv import load_dotenv
import os
from rest_framework.response import Response
from rest_framework import status
import random

from fsd_medic.settings import BASE_DIR
import random
from .models import Countries

load_dotenv(BASE_DIR / ".env")


def Send_email(user_email, message):
    send_mail(
        'Подтверждение почты',
        message,
        os.getenv("EM_HOST_USER"),
        [user_email],
        fail_silently=False,
    )


def create_or_delete(classmodel, **kwargs):
    try:
        obj = classmodel.objects.get(**kwargs)
        obj.delete()
        return Response({'result': f'обьект {classmodel.__name__} удален'}, status=status.HTTP_200_OK)

    except:
        obj = classmodel.objects.create(**kwargs)
        obj.save()
        return Response({'result': f'обьект {classmodel.__name__} создан'}, status=status.HTTP_200_OK)


def generate_email_code():
    code = random.randrange(start=10000000, stop=99999999)
    return code
