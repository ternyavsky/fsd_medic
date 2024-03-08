import logging
import hashlib
import os
from django.core.cache import cache
import requests
from api.models import City, Country
from auth_doctor.serializers import DoctorCreateSerializer, DoctorVerifyResetCodeSerializer, DoctorNewPasswordSerializer
from db.queries import get_doctors
from ..models import Doctor, LinkToInterview
from rest_framework.response import Response
from rest_framework import status
from ..service import *
from celery import shared_task

logger = logging.getLogger(__name__)


def doctor_set_newpassword_service(request):
    serializer = DoctorNewPasswordSerializer(data=request.data)
    if serializer.is_valid():
        if "email" in serializer.validated_data:
            doctor = Doctor.objects.get(
                email=serializer.validated_data["email"])

        if "number" in serializer.validated_data:
            doctor = Doctor.objects.get(
                number=serializer.validated_data["number"])

        else:
            logger.warning("Doctor not found")
            logger.warning(request.path)
            return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        doctor_set_new_password(doctor, serializer.validated_data["password2"])
        logger.debug("Password changed successfully")
        logger.debug(request.path)
        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def doctor_resend_sms_service(request):
    number = request.data["number"]
    doctors = cache.get_or_set("doctors", get_doctors())
    doctor = doctors.filter(number=number)
    if doctor:
        code = generate_verification_code()
        logger.debug(code)
        send_sms.delay(doctor.number, code)
        doctor.verification_code = code
        doctor.save()
        logger.debug(request.path)
        return Response({'detail': 'SMS resent successfully'}, status=status.HTTP_200_OK)
    else:
        logger.warning("Doctor not found")
        logger.warning(request.path)
        return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

def doctor_verify_resetcode_service(request):
    serializer = DoctorVerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        reset_code = serializer.validated_data['reset_code']
        if 'email' in serializer.validated_data:
            doctor = Doctor.objects.get(
                email=serializer.validated_data['email'])
        else:
            doctor = Doctor.objects.get(
                number=serializer.validated_data["number"])
        if reset_code == doctor.reset_code:
            doctor.save()
            logger.debug("Doctor got the access to his account")
            logger.debug(request.path)
            return Response({"message": "Doctor got the access to his account"}, status=status.HTTP_200_OK)

        else:
            logger.warning("Doctor didnt get the access to his account")
            logger.warning(request.path)
            return Response({"message": "Doctor didnt get the access to his account"},
                            status=status.HTTP_404_NOT_FOUND)
    else:
        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors)

def doctor_passoword_reset_service(request):
    if 'number' in request.data:
        doctors = cache.get_or_set("doctors", get_doctors())
        doctor = doctors.filter(number=request.data['number']).first()
        if doctor != None:
            code = generate_verification_code()
            num = request.data['number']
            send_reset_sms.delay(num, code)
            doctor.reset_code = code
            logger.debug(code)
            doctor.save()
            return Response({"message":"success"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Doctor not found"}, 400)

    if 'email' in request.data:
        doctors = cache.get_or_set("doctors", get_doctors())
        doctor = doctors.filter(email=request.data['email']).first()
        if doctor != None:
            code = generate_verification_code()
            email = request.data['email']
            send_reset_email.delay(email, code)
            doctor.reset_code = code
            logger.debug(code)
            doctor.save()
            return Response({"message":"success"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Doctor not found"}, 400)
    else:
        return Response({"error": "Not email or number"}, 400)

def doctor_create_interview_service(request, doctor_hash):
    try:
        obj = LinkToInterview.objects.get(link=doctor_hash)
        if obj.used:
            return Response({"error": "Ссылка уже использовалась"}, 400)
        else:
            obj.used = True
            obj.save()
            logger.debug(obj.used)
            logger.debug(cache.get(doctor_hash))
            result, status = doctor_create(doctor_hash, request.data.get("datetime"))
            return Response(result, status=status)
    except LinkToInterview.DoesNotExist:
        return Response({"error": "Object not found"}, 404)
    except Exception as e:
        logger.exception("An error occurred: %s", str(e))
        return Response({"error": "Internal server error"}, 500)

def doctor_datapast_service(request):
    serializer = DoctorCreateSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        doctor_hash: str = doctor_data_pass(validated_data)
        try:
            LinkToInterview.objects.create(
                used=False,
                link=doctor_hash
            )
            number = validated_data["number"]
            send_verification_code_doctor.delay(doctor_hash, number)
            return Response({"message": f"Код для регистрации врача отправлен на номер {number}",
                                "doctor_hash": doctor_hash}, status=status.HTTP_200_OK)
        except:  # noqa: E722
            return Response({"message": "Запрос с такими данными уже существует, повторите попытку позже"},
                            status.HTTP_400_BAD_REQUEST)
    else:
        # Если данные не прошли валидацию, верните ошибки
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def doctor_create(doctor_hash: str, datetime_obj):
    doctor_data = cache.get(doctor_hash)
    if doctor_data:
        doctor_country = doctor_data.pop("country")
        doctor_city = doctor_data.pop("city")
        doctor = Doctor.objects.create(**doctor_data)
        doctor.review_date = datetime_obj
        doctor.review_passed = False
        doctor.country = Country.objects.get(name=doctor_country)
        doctor.city = City.objects.get(name=doctor_city)
        doctor.save()
        return {"message": "Успешно создан", "id": doctor.id}, 201
    else:
        return {"message": "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново"}, 400



@shared_task
def send_verification_code_doctor(doctor_hash, number_to):
    key = os.getenv('API_KEY')
    email = os.getenv('EMAIL')
    url = f'https://{email}:{key}@gate.smsaero.ru/v2/sms/send?number={number_to}&text=Ссылка+для+собедования+http://127.0.0.1:8000/api/create_doctor/{doctor_hash}&sign=SMSAero'
    res = requests.get(url)
    if res.status_code == 200:
        print('отправилось')
    print("Хэш для вставки(Фронт)", doctor_hash)
    print("http://127.0.0.1:8000/api/create_doctor/{}".format(doctor_hash))


def doctor_data_pass(validated_data: dict):
    user_data = f"{validated_data['first_name']}_{validated_data['last_name']}_{validated_data['number']}"
    cache_key = hashlib.sha256(user_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, timeout=None)
    return cache_key
