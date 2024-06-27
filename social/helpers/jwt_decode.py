import jwt
from api.models import User
from auth_doctor.models import Doctor
from api.serializers import UserSerializer, DoctorGetSerializer
from db.queries import get_doctors, get_users
from django.core.cache import cache


def jwt_decode(token: str, connect: bool = True) -> User | Doctor:
    instance = jwt.decode(token, "Bearer", algorithms="HS256")
    if instance["type"] == "doctor":
        doctor = (
            cache.get_or_set("doctors", get_doctors())
            .filter(number=instance["number"])
            .first()
        )
        doctor.online = True if connect else False
        doctor.save()
        return DoctorGetSerializer(doctor).data
    else:
        user = (
            cache.get_or_set("users", get_users())
            .filter(id=instance["user_id"])
            .first()
        )
        user.online = True if connect else False
        user.save()
        return UserSerializer(user).data
