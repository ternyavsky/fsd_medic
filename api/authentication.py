from rest_framework import HTTP_HEADER_ENCODING, authentication
from django.utils.translation import gettext_lazy as _
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Center, Clinic
from auth_doctor.models import Doctor
from rest_framework import authentication
from rest_framework import exceptions
from db.queries import get_doctors
from datetime import date, datetime


# write custom auth for socket

#  smash on clinic, center, doctor
class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        token = request.headers["Authorization"].split(" ")
        if token[0] != "Bearer":
            raise exceptions.AuthenticationFailed("No valid secret word")
        else:
            jwt_token = token[1]
            payload = jwt.decode(jwt_token, "Bearer", algorithms=["HS256"])
            exp = payload["exp"]
            number = payload["number"]
            match payload["type"]:
                case "doctor":
                    try:
                        doctor = Doctor.objects.get(number=number)
                        return (doctor, None)
                    except Doctor.DoesNotExist:
                        raise exceptions.AuthenticationFailed("Doctor not found")
                case "center":
                    try:
                        center = Center.objects.get(number=number)
                        return (center, None)
                    except Center.DoesNotExist:
                        raise exceptions.AuthenticationFailed("Center not found")
                case "clinic":
                    try:
                        clinic = Clinic.objects.get(number=number)
                        return (clinic, None)
                    except Clinic.DoesNotExist:
                        raise exceptions.AuthenticationFailed("Clinic not found")
