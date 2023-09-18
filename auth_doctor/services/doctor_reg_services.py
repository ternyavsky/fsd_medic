import hashlib
from django.core.cache import cache
from .all_service import is_valid_phone_number, get_code_cache_name
from rest_framework.serializers import ValidationError
from ..models import Doctor


def doctor_reg_data_validate(data: dict):
    phone = data.get("phone_number")
    if not is_valid_phone_number(phone):
        raise ValidationError({"phone_number": "Невалидный номер телефона"})


def doctor_compare_code_and_create(user_hash: str, right_code: str, ver_code: str):
    if right_code == ver_code:
        user_data = cache.get(user_hash)
        if user_data:
            doctor = Doctor.objects.create(**user_data)
            doctor.save()
            print("doctor_obj=", doctor)
            print(user_data)
            return 200, "Ваша заявка на регистрацию получена, она пройдет рассмотрение "
        else:
            return 400, "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново"
    else:
        return 400, "Коды не совпадают"


def doctor_data_passed(validated_data: dict):
    user_data = f"{validated_data['first_name']}_{validated_data['last_name']}_{validated_data['phone_number']}"
    cache_key = hashlib.sha256(user_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, 60 * 5)
    return cache_key
