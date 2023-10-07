import hashlib

from django.core.cache import cache

from api.models import Clinic, Country, City


def clinic_create(clinic_hash: str, datetime_obj):
    clinic_data = cache.get(clinic_hash)
    if clinic_data:
        supported_diseases = clinic_data.pop("supported_diseases")
        clinic_country = clinic_data.pop("country")
        clinic_city = clinic_data.pop("city")
        clinic = Clinic(**clinic_data)
        clinic.review_date = datetime_obj
        clinic.review_passed = False
        clinic.country = Country.objects.get(name=clinic_country)
        clinic.city = City.objects.get(name=clinic_city)
        clinic.save()
        for i in supported_diseases:
            clinic.supported_diseases.add(i)
        clinic.save()
        return {"message": "Успешно создан", "id": clinic.id}, 201
    else:
        return {"message": "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново"}, 400


def send_verification_code_clinic(clinic_hash, number_to):
    print("Хэш для вставки(Фронт)", clinic_hash)
    print("http://127.0.0.1:8000/api/create_clinic/{}".format(clinic_hash))


def clinic_data_pass(validated_data: dict):
    clinic_data = f"{validated_data['name']}_{validated_data['number']}"
    cache_key = hashlib.sha256(clinic_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, timeout=None)
    return cache_key
