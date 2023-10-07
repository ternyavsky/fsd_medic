import logging

from django.core.cache import cache
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CenterSerializer
from auth_user.service import set_new_password
from db.queries import *
from .models import LinkToInterview
from .serializers import *
from .service import *
from .services.clinic_reg_service import (
    clinic_data_pass,
    clinic_create,
    send_verification_code_clinic,
)
from .services.doctor_reg_services import (
    doctor_data_pass,
    send_verification_code_doctor,
    doctor_create,
)

logger = logging.getLogger(__name__)


class ClinicDataPast(views.APIView):
    @swagger_auto_schema(
        operation_summary="Сохраняет данные клиники в кэш",
        query_serializer=ClinicCreateSerializer,
        responses={
            status.HTTP_200_OK: DoctorDataResponseSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = ClinicCreateSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            clinic_hash: str = clinic_data_pass(validated_data)
            try:
                LinkToInterview.objects.create(
                    used=False,
                    link=clinic_hash
                )
                number = validated_data["number"]
                send_verification_code_clinic(clinic_hash, number)
                return Response({"message": f"Код для регистрации клиники отправлен на номер {number}",
                                 "clinic_hash": clinic_hash}, status=status.HTTP_200_OK)
            except:
                return Response({"error": "Запрос с такими данными уже существует"}, status.HTTP_400_BAD_REQUEST)
        else:
            # Если данные не прошли валидацию, верните ошибки
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicInterviewCreate(views.APIView):
    def post(self, request, clinic_hash):
        obj = LinkToInterview.objects.get(link=clinic_hash)
        if obj.used == True:
            return Response({"error": "Ссылка уже использовалась"}, 404)
        else:
            obj.used = True
            obj.save()
            print(cache.get(clinic_hash))
            result, status = clinic_create(clinic_hash, request.data["datetime"])
            return Response(result, status=status)


class DoctorDataPast(views.APIView):
    @swagger_auto_schema(
        operation_summary="Сохранение данных врача в кэш и отправка ссылки",
        query_serializer=DoctorCreateSerializer,
        responses={
            status.HTTP_200_OK: DoctorDataResponseSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
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
                send_verification_code_doctor(doctor_hash, number)
                return Response({"message": f"Код для регистрации врача отправлен на номер {number}",
                                 "doctor_hash": doctor_hash}, status=status.HTTP_200_OK)
            except:
                return Response({"message": "Запрос с такими данными уже существует, повторите попытку позже"},
                                status.HTTP_400_BAD_REQUEST)
        else:
            # Если данные не прошли валидацию, верните ошибки
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorInterviewCreate(views.APIView):
    def post(self, request, doctor_hash):
        obj = LinkToInterview.objects.get(link=doctor_hash)
        if obj.used == True:
            return Response({"error": "Ссылка уже использовалась"}, 404)
        else:
            print(obj.used)
            obj.used = True
            obj.save()
            print(cache.get(doctor_hash))
            result, status = doctor_create(doctor_hash, request.data["datetime"])
            return Response(result, status=status)


class DoctorPasswordResetView(APIView):
    """Сброс пароля. Этап отправки"""

    def post(self, request):
        serializer = DoctorPasswordResetSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            doctor = serializer.save()
            if 'number' in request.data:
                code = generate_verification_code()
                num = request.data['number']
                send_reset_sms(num, code)
                doctor.reset_code = code
                logger.debug(code)
                doctor.save()

            if 'email' in request.data:
                code = generate_verification_code()
                email = request.data['email']
                send_reset_email(email, code)
                doctor.reset_code = code
                logger.debug(code)
                doctor.save()

            logger.info(serializer.data)
            logger.debug(request.path)
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorVerifyResetCodeView(APIView):
    """Проверка кода для сброса пароля"""

    def post(self, request):
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


class DoctorSetNewPasswordView(APIView):
    """Установка нового пароля"""

    def post(self, request):
        serializer = DoctorNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password1 = serializer.validated_data['password1']
            password2 = serializer.validated_data['password2']

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

            if password1 == password2:
                doctor_set_new_password(doctor, password2)
                logger.debug("Password changed successfully")
                logger.debug(request.path)
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            else:
                logger.warning("Password do not match")
                logger.warning(request.path)
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning(serializer.errors)
            logger.warning(request.path)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicPasswordResetView(APIView):
    """Сброс пароля. Этап отправки"""

    def post(self, request):
        serializer = ClinicPasswordResetSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            clinic = serializer.save()
            if 'number' in request.data:
                code = generate_verification_code()
                num = request.data['number']
                send_reset_sms(num, code)
                clinic.reset_code = code
                logger.debug(code)
                clinic.save()

            if 'email' in request.data:
                code = generate_verification_code()
                email = request.data['email']
                send_reset_email(email, code)
                clinic.reset_code = code
                logger.debug(code)
                clinic.save()

            logger.info(serializer.data)
            logger.debug(request.path)
            return Response(serializer.data, status=status.HTTP_200_OK)

        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClinicVerifyResetCodeView(APIView):
    """Проверка кода для сброса пароля"""

    def post(self, request):
        serializer = ClinicVerifyResetCodeSerializer(data=request.data)
        if serializer.is_valid():
            reset_code = serializer.validated_data['reset_code']
            if 'email' in serializer.validated_data:
                clinic = Clinic.objects.get(
                    email=serializer.validated_data['email'])
            else:
                clinic = Clinic.objects.get(
                    number=serializer.validated_data["number"])
            if reset_code == clinic.reset_code:
                clinic.save()
                logger.debug("Clinic got the access to his account")
                logger.debug(request.path)
                return Response({"message": "Clinic got the access to his account"}, status=status.HTTP_200_OK)

            else:
                logger.warning("Clinic didnt get the access to his account")
                logger.warning(request.path)
                return Response({"message": "Clinic didnt get the access to his account"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            logger.warning(serializer.errors)
            logger.warning(request.path)
            return Response(serializer.errors)


class ClinicSetNewPasswordView(APIView):
    """Установка нового пароля"""

    def post(self, request):
        serializer = ClinicNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password1 = serializer.validated_data['password1']
            password2 = serializer.validated_data['password2']

            if "email" in serializer.validated_data:
                clinic = Clinic.objects.get(
                    email=serializer.validated_data["email"])

            if "number" in serializer.validated_data:
                clinic = Clinic.objects.get(
                    number=serializer.validated_data["number"])

            else:
                logger.warning("Clinic not found")
                logger.warning(request.path)
                return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)

            if password1 == password2:
                set_new_password(clinic, password2)
                logger.debug("Password changed successfully")
                logger.debug(request.path)
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            else:
                logger.warning("Password do not match")
                logger.warning(request.path)
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.warning(serializer.errors)
            logger.warning(request.path)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InterviewView(generics.ListCreateAPIView):  # как бы это не называлось
    permission_classes = [AllowAny]
    """Работа с сотрудниками"""
    serializer_class = InterviewSerializer
    queryset = Interview.objects.all()

    def post(self, request):
        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            interview = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city):
        data = cache.get_or_set("centers", get_centers(city=city))
        centers = data.filter(city=city)
        logger.debug(centers)
        data = CenterSerializer(centers, many=True).data
        logger.debug(data)
        logger.debug(request.path)
        return Response(data, status=status.HTTP_200_OK)
