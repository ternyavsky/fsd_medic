import hashlib

from django.core.cache import cache
import logging
from auth_doctor.service import generate_verification_code, send_reset_email, send_reset_sms, send_sms
from ..serializers import *
from api.models import Clinic, Country, City
from ..models import LinkToInterview
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from db.queries import get_clinics
from ..service import *
from celery import shared_task

logger = logging.getLogger(__name__)

def clinic_set_password_service(request):
    serializer = ClinicNewPasswordSerializer(data=request.data)
    if serializer.is_valid():
        if "email" in serializer.validated_data:
            clinic = Clinic.objects.get(
                email=serializer.validated_data["email"])

        if "number" in serializer.validated_data:
            clinic = Clinic.objects.get(
                number=serializer.validated_data["number"])

        else:
            logger.warning("Clinic not found")
            logger.warning(request.path)
            return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
            
        
        clinic_set_new_password(clinic, serializer.validated_data["password2"])
        logger.debug("Password changed successfully")
        logger.debug(request.path)
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def clinic_verify_resetcode_service(request):
    serializer = ClinicVerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        reset_code = serializer.validated_data['reset_code']
        if 'email' in serializer.validated_data:
            clinic = Clinic.objects.get(
                email=serializer.validated_data['email'])
        else:
            clinic = Clinic.objects.get(
                number=serializer.validated_data["number"])
        if reset_code == clinic.reset_code:
            clinic.save()
            logger.debug("Clinic got the access to his account")
            logger.debug(request.path)
            return Response({"message": "Clinic got the access to his account"}, status=status.HTTP_200_OK)

        else:
            logger.warning("Clinic didnt get the access to his account")
            logger.warning(request.path)
            return Response({"message": "Clinic didnt get the access to his account"},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors)

def clinic_resend_sms_service(request):
    number = request.data["number"]
    clinics = cache.get_or_set("clinics", get_clinics())
    clinic = clinics.filter(number=number)
    if clinic:
        code = generate_verification_code()
        logger.debug(code)
        send_sms.delay(clinic.number, code)
        clinic.verification_code = code
        clinic.save()
        logger.debug(request.path)
        return Response({'detail': 'SMS resent successfully'}, status=status.HTTP_200_OK)
    else:
        logger.warning("Clinic not found")
        logger.warning(request.path)
        return Response({'detail': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)


def clinic_password_reset_service(request):
    if 'number' in request.data:
        clinics = cache.get_or_set("clinics", get_clinics())
        clinic = clinics.filter(number=request.data['number']).first()
        if clinic != None:
            code = generate_verification_code()
            num = request.data['number']
            send_reset_sms.delay(num, code)
            clinic.reset_code = code
            logger.debug(code)
            clinic.save()
            return Response({"message": "success"}, 201)
        else:
            return Response({"error": "Clinic not found"}, 400)

    if 'email' in request.data:
        clinics = cache.get_or_set("clinics", get_clinics())
        clinic = clinics.filter(email=request.data['email']).first()
        if clinic != None:
            code = generate_verification_code()
            email = request.data['email']
            send_reset_email.delay(email, code)
            clinic.reset_code = code
            logger.debug(code)
            clinic.save()
            return Response({"message": "success"}, 201)
        else:
            return Response({"error": "Clinic not found"}, 400)
    else:
        return Response({"error": "Not email or number"}, 400)

@transaction.atomic
def clinic_interview_create_service(request, clinic_hash):
    obj = LinkToInterview.objects.get(link=clinic_hash)
    if obj.used:
        return Response({"error": "Ссылка уже использовалась"}, 404)
    else:
        obj.used = True
        obj.save()
        print(cache.get(clinic_hash))
        result, status = clinic_create(clinic_hash, request.data["datetime"])
        return Response(result, status=status)

@transaction.atomic
def clinic_datapast_service(request):
    serializer = ClinicCreateSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        clinic_hash = clinic_data_pass(validated_data)
        try:
            LinkToInterview.objects.create(
                used=False,
                link=clinic_hash
            )
            number = validated_data["number"]
            send_verification_code_clinic.delay(clinic_hash, number)
            response_data = {
                "message": f"Код для регистрации клиники отправлен на номер {number}",
                "clinic_hash": clinic_hash
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Запрос с такими данными уже существует"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # If the data did not pass validation, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def clinic_create(clinic_hash: str, datetime_obj):
    clinic_data = cache.get(clinic_hash)
    if clinic_data:
        supported_diseases = clinic_data.pop("supported_diseases")
        clinic_country = clinic_data.pop("country")
        clinic_city = clinic_data.pop("city")
        
        clinic = Clinic.objects.create(**clinic_data)
        clinic.review_date = datetime_obj
        clinic.review_passed = False
        clinic.country = clinic_country
        clinic.city = City.objects.get(name=clinic_city)
        clinic.supported_diseases.set(supported_diseases)
        clinic.save()
        return {"message": "Успешно создан", "id": clinic.id}, status.HTTP_201_CREATED
    else:
        return {"message": "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново"}, 400

@shared_task
def send_verification_code_clinic(clinic_hash, number_to):
    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number_to}&text=Ссылка+для+собедования+http://127.0.0.1:8000/api/create_clinic/{clinic_hash}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось')
    print("Хэш для вставки(Фронт)", clinic_hash)
    print("http://127.0.0.1:8000/api/create_clinic/{}".format(clinic_hash))


def clinic_data_pass(validated_data: dict):
    clinic_data = f"{validated_data['name']}_{validated_data['number']}"
    cache_key = hashlib.sha256(clinic_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, timeout=None)
    return cache_key
