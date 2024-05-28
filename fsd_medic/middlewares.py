import jwt

from api.models import Clinic, User
from auth_doctor.models import Doctor


class AuthMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def jwt_decode(self, token: str, request):
        data = jwt.decode(token, "Bearer", algorithms=["HS256"])
        match data["type"]:
            case "clinic":
                print(1)
                clinic = Clinic.objects.get(number=data["number"])
                request.clinic = clinic
            case "doctor":
                doctor = Doctor.objects.get(number=data["number"])
                request.doctor = doctor
            case "user":
                user = User.objects.get(number=data["number"])
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
