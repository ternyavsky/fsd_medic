import hashlib
from django.core.cache import cache
from api.models import Clinic
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .all_service import is_valid_phone_number
from rest_framework.exceptions import ValidationError


def clinic_reg_data_validate(data: dict):
    phone = data.get("number")
    if not is_valid_phone_number(phone):
        raise ValidationError({"number": "Невалидный номер телефона"})


def clinic_data_update(object_id, datetime_obj):
    try:
        obj = Clinic.objects.get(id=object_id)
        obj.dateTimeField = datetime_obj
        obj.save()
        return Response({'message': 'Datetime успешно обновлен'}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({'message': 'Объект с указанным id не найден'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'message': 'Произошла ошибка: {}'.format(str(e))},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def clinic_compare_code_and_create(user_hash: str, right_code: str, ver_code: str):
    if right_code == ver_code:
        user_data = cache.get(user_hash)
        if user_data:
            doctor = Clinic.objects.create(**user_data)
            return 201, {"message": "Успешно создан", "id": doctor.id}
        else:
            return 400, {"message": "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново"}
    else:
        return 400, "Коды не совпадают"


def clinic_data_pass(validated_data: dict):
    user_data = f"{validated_data['name']}_{validated_data['number']}"
    cache_key = hashlib.sha256(user_data.encode()).hexdigest()
    cache.set(cache_key, validated_data, 60 * 5)
    return cache_key
