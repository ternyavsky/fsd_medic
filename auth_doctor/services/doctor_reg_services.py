import hashlib
from django.core.cache import cache
from .all_service import get_code_cache_name
from rest_framework.serializers import ValidationError
from ..models import Doctor
from api.models import Country, City
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist


def doctor_create(doctor_hash: str, datetime_obj):
    doctor_data = cache.get(doctor_hash)
    if doctor_data:
        doctor_country = doctor_data.pop("country")
        doctor_city = doctor_data.pop("city")
        doctor = Doctor.objects.create(**doctor_data)
        doctor.review_date = datetime_obj
        doctor.review_passed = False
     #   doctor.country = Country.objects.get(name=doctor_country)
        doctor.city = City.objects.get(name=doctor_city)
        doctor.save()
        return {"message": "Успешно создан", "id": doctor.id}, 201
    else:
        return {"message": "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново"}, 400



def send_verification_code_doctor(doctor_hash,number_to):
    print("Хэш для вставки(Фронт)", doctor_hash)
    print("http://127.0.0.1:8000/api/create_doctor/{}".format(doctor_hash))


def doctor_data_pass(validated_data: dict):
    user_data = f"{validated_data['first_name']}_{validated_data['last_name']}_{validated_data['number']}"
    cache_key = hashlib.sha256(user_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, timeout=None)
    return cache_key
