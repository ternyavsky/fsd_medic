import hashlib
from django.core.cache import cache
from .all_service import is_valid_phone_number
from rest_framework.serializers import ValidationError


def doctor_reg_data_validate(data):
    phone = data.get("phone_number")
    if not is_valid_phone_number(phone):
        raise ValidationError({"phone_number": "Невалидный номер телефона"})


def doctor_compare_code_and_create(user_hash, right_code, ver_code):
    if right_code == ver_code:
        pass
    else:
        return 400, "Коды не совпадают"


def doctor_data_passed(validated_data):
    user_data = f"{validated_data['first_name']}_{validated_data['last_name']}_{validated_data['phone_number']}"
    cache_key = hashlib.sha256(user_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, 60 * 5)
    return cache_key
