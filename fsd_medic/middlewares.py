from django.db import models
import jwt

from api.models import Clinic, User, BaseModel
from auth_doctor.models import Doctor


class AuthMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def get_instance(self, model, param):
        instance = model.objects.get(**param)
        return instance

    def jwt_decode(self, token: str, request):
        data: dict = jwt.decode(token, "Bearer", algorithms=["HS256"])
        print(data)
        match data["type"]:
            case "clinic":
                clinic = None
                if data["number"] != None:
                    clinic = self.get_instance(Clinic, {"number": data["number"]})
                elif data["email"] != None:
                    clinic = self.get_instance(Clinic, {"email": data["email"]})
                request.clinic = clinic
            case "doctor":
                doctor = None
                if data["number"] != None:
                    doctor = self.get_instance(Doctor, {"number": data["number"]})
                elif data["email"] != None:
                    doctor = self.get_instance(Doctor, {"email": data["email"]})
                request.doctor = doctor
            case "user":
                user = None
                if data["number"] != None:
                    user = self.get_instance(User, {"number": data["number"]})
                elif data["email"] != None:
                    user = self.get_instance(User, {"email": data["email"]})
                request.user = user
        return request

    def __call__(self, request):
        request.clinic = None
        request.user = None
        request.doctor = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
            req = self.jwt_decode(token, request)
            response = self.get_response(req)
            return response
        return self.get_response(request)
