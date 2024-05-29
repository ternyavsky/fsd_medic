import logging
import jwt
import datetime
from datetime import UTC, time, time, date, date, timezone
from django.core.cache import cache
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_user.serializers import ResendCodeSerializer
from api.serializers import CenterSerializer, ClinicSerializer, DoctorGetSerializer
from auth_user.service import set_new_password
from api.backends import *
from db.queries import *
from .models import LinkToInterview
from .serializers import *
from .service import *
from .services.clinic_reg_service import *
from .services.doctor_reg_services import *

logger = logging.getLogger(__name__)


class ClinicViewSet(ModelViewSet):
    serializer_class = ClinicSerializer
    queryset = Clinic.objects.all()

    @swagger_auto_schema(
        operation_summary="Регистрация клиники", request_body=ClinicCreateSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = ClinicCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        clinic = serializer.save()
        headers = self.get_success_headers(self.get_serializer(clinic).data)
        return Response(
            self.get_serializer(clinic).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class DoctorsListView(generics.ListAPIView):
    serializer_class = DoctorGetSerializer
    queryset = Doctor.objects.all()
    permissions_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "country",
        "city",
        "first_name",
        "last_name",
        "work_experience",
        "specialization",
        "main_status",
    ]

    def get_queryset(self):
        return self.queryset.filter(country=self.request.user.country)


class ClinicDataPast(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Сохраняет данные клиники в кэш",
        # query_serializer=ClinicCreateSerializer,
        responses={
            # status.HTTP_200_OK: DoctorDataResponseSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        },
    )
    def post(self, request, *args, **kwargs):
        return clinic_datapast_service(request)


class ClinicInterviewCreate(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Назначение даты интервью (Клиника)",
    )
    def post(self, request, clinic_hash):
        return clinic_interview_create_service(request, clinic_hash)


class DoctorDataPast(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Сохранение данных врача в кэш и отправка ссылки",
        # query_serializer=DoctorCreateSerializer,
        responses={
            # status.HTTP_200_OK: DoctorDataResponseSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return doctor_datapast_service(request)


class DoctorInterviewCreate(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Назначение даты интервью (Доктор)",
    )
    def post(self, request, doctor_hash):
        return doctor_create_interview_service(request, doctor_hash)


class DoctorPasswordResetView(APIView):
    """Сброс пароля. Этап отправки"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Сброс пароля (Доктор), отправка кода",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return doctor_passoword_reset_service(request)


class DoctorVerifyResetCodeView(APIView):
    """Проверка кода для сброса пароля"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Проверка кода для сброса пароля (Доктор)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["reset_code"],
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "reset_code": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        return doctor_verify_resetcode_service(request)


class DoctorResendSmsView(APIView):
    """Переотправка смс, в разделе 'получить смс снова'"""

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Переотправка смс (Доктор)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return doctor_resend_sms_service(request)


class DoctorSetNewPasswordView(APIView):
    permission_classes = [AllowAny]
    """Установка нового пароля"""

    @swagger_auto_schema(
        operation_summary="Установка нового пароля (Доктор)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["password1", "password2"],
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password1": openapi.Schema(type=openapi.TYPE_STRING),
                "password2": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return doctor_set_newpassword_service(request)


class ClinicPasswordResetView(APIView):
    permission_classes = [AllowAny]
    """Сброс пароля. Этап отправки"""

    @swagger_auto_schema(
        operation_summary="Сброс пароля(Клиника), отправка кода",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return clinic_password_reset_service(request)


class ClinicResendSmsView(APIView):
    permission_classes = [AllowAny]
    """Переотправка смс, в разделе 'получить смс снова'"""

    @swagger_auto_schema(
        operation_summary="Переотправка смс (Клиника)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return clinic_resend_sms_service(request)


class ClinicVerifyResetCodeView(APIView):
    permission_classes = [AllowAny]
    """Проверка кода для сброса пароля"""

    @swagger_auto_schema(
        operation_summary="Проверка кода для сброса пароля (Клиника)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["reset_code"],
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "reset_code": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        return clinic_verify_resetcode_service(request)


class ClinicSetNewPasswordView(APIView):
    permission_classes = [AllowAny]
    """Установка нового пароля"""

    @swagger_auto_schema(
        operation_summary="Установка нового пароля (Клиника)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["password1", "password2"],
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password1": openapi.Schema(type=openapi.TYPE_STRING),
                "password2": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return clinic_set_password_service(request)


class InterviewView(generics.ListCreateAPIView):  # как бы это не называлось
    permission_classess = [AllowAny]

    """Работа с сотрудниками"""
    serializer_class = InterviewSerializer
    queryset = Interview.objects.all()

    def get(self, request):
        return super().get(self, request)

    def post(self, request):
        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginDoctor(APIView):
    def post(self, request):
        number, password = request.data["number"], request.data["password"]
        doctor = doctor_authenticate(number, password)
        if doctor != None:
            doctor_jwt = jwt.encode(
                {
                    "number": doctor.number,
                    "email": doctor.email,
                    "type": "doctor",
                    "exp": datetime.datetime.now(tz=timezone.utc)
                    + datetime.timedelta(days=30),
                },
                "Bearer",
                algorithm="HS256",
            )
            return Response({"access_token": doctor_jwt}, status=status.HTTP_200_OK)
        return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginCenter(APIView):
    def post(self, request):
        number, password = request.data["number"], request.data["password"]
        center = center_authenticate(number, password)
        if center != None:
            center_jwt = jwt.encode(
                {
                    "number": center.number,
                    "email": center.email,
                    "type": "center",
                    "exp": datetime.now(tz=timezone.utc) + datetime.timedelta(days=30),
                },
                "Bearer",
                algorithm="HS256",
            )
            return Response({"access_token": center_jwt}, status=status.HTTP_200_OK)
        return Response({"error": "Center not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginClinic(APIView):
    def post(self, request):
        number, password = request.data["number"], request.data["password"]
        print(number, password)
        clinics = cache.get_or_set("clinics", get_clinics())
        clinic = clinic_authenticate(number, password)
        if clinic != None:
            clinic_jwt = jwt.encode(
                {
                    "number": clinic.number,
                    "email": clinic.email,
                    "type": "clinic",
                    "exp": datetime.datetime.now(tz=timezone.utc),
                },
                "Bearer",
                algorithm="HS256",
            )
            return Response({"access_token": clinic_jwt}, status=status.HTTP_200_OK)
        return Response({"error": "Clinic not found"}, status=status.HTTP_404_NOT_FOUND)
