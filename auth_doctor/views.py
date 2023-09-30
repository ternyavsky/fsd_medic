import logging

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CenterSerializer, UserGetSerializer
from api.models import Interview
from auth_doctor.serializers import InterviewSerializer
from .serializers import DoctorCreateSerializer, DateTimeUpdateSerializer
from db.queries import *
from rest_framework import views
from .services.doctor_reg_services import doctor_data_passed, doctor_compare_code_and_create, doctor_data_update
from .services.all_service import send_verification_code_msg, get_code_cache_name
from .serializers import VerificationCodeSerializer, DoctorDataResponseSerializer, ClinicCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.models import Clinic
from .services.clinic_reg_service import clinic_data_pass, clinic_compare_code_and_create, clinic_date_update

logger = logging.getLogger(__name__)


class UpdateDateTimeViewClinic(APIView):
    @swagger_auto_schema(
        request_body=DateTimeUpdateSerializer,
        responses={
            200: 'Datetime успешно обновлен',
            400: 'Неверный формат данных',
            404: 'Объект с указанным id не найден',
            500: 'Произошла ошибка'
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Обновляет значение поля dateTimeField объекта по его ID.

        :param request: Запрос с данными id и datetime.
        :return: Сообщение об успешном обновлении или сообщение об ошибке.
        """
        serializer = DateTimeUpdateSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            datetime_obj = serializer.validated_data['datetime']
            return clinic_date_update(id, datetime_obj)
        else:
            return Response({'message': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)


class ClinicDataPast(views.APIView):
    @swagger_auto_schema(
        operation_summary="Сохраняет данные клиники в кэш",
        query_serializer=ClinicCreateSerializer,
        responses={
            status.HTTP_200_OK: DoctorDataResponseSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = ClinicCreateSerializer(data=request.data)

        if serializer.is_valid():   
            validated_data = serializer.validated_data
            user_hash = clinic_data_pass(validated_data)
            response_serializer = DoctorDataResponseSerializer({
                'message': "Данные сохранены, ожидаем подтверждение",
                'user_hash': user_hash
            })
            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        else:
            # Если данные не прошли валидацию, верните ошибки
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsClinicVerCodeRight(views.APIView):
    @swagger_auto_schema(
        operation_summary="Проверка верификационного кода для клиники, создание аккаунта",
        request_body=VerificationCodeSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Успешно создан'),
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_404_NOT_FOUND: "Not Found",
        }
    )
    def post(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user_hash = validated_data.get("user_hash")
            right_code = cache.get(get_code_cache_name(user_hash))
            if right_code:
                verification_code = validated_data.get("verification_code")
                status_code, msg = clinic_compare_code_and_create(
                    user_hash, right_code, verification_code)
                return Response(status=status_code, data={"message": msg})
            else:
                return Response(status=404,
                                data={"message": "Время проверки кодов вышло или такого пользователя вообще не было"})


class UpdateDateTimeViewDoctor(APIView):
    @swagger_auto_schema(
        request_body=DateTimeUpdateSerializer,
        responses={
            200: 'Datetime успешно обновлен',
            400: 'Неверный формат данных',
            404: 'Объект с указанным id не найден',
            500: 'Произошла ошибка'
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Обновляет значение поля dateTimeField объекта по его ID.

        :param request: Запрос с данными id и datetime.
        :return: Сообщение об успешном обновлении или сообщение об ошибке.
        """
        serializer = DateTimeUpdateSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data['id']
            datetime_obj = serializer.validated_data['datetime']
            return doctor_data_update(id, datetime_obj)
        else:
            return Response({'message': 'Неверный формат данных'}, status=status.HTTP_400_BAD_REQUEST)


class DoctorDataPast(views.APIView):
    @swagger_auto_schema(
        operation_summary="Сохраняет данные врача в кэш",
        query_serializer=DoctorCreateSerializer,
        responses={
            status.HTTP_200_OK: DoctorDataResponseSerializer(),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = DoctorCreateSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            user_hash = doctor_data_passed(validated_data)
            response_serializer = DoctorDataResponseSerializer({
                'message': "Данные сохранены, ожидаем подтверждение",
                'user_hash': user_hash
            })

            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        else:
            # Если данные не прошли валидацию, верните ошибки
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegSmsCodeSend(views.APIView):
    @swagger_auto_schema(
        operation_summary="Отправка SMS-кода для регистрации",
        responses={
            status.HTTP_200_OK: "Success",
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_404_NOT_FOUND: "Not Found",
        }
    )
    def get(self, request, user_hash):
        user_data = cache.get(user_hash)
        if user_data:
            to_phone = user_data.get("number")
            if to_phone is not None:
                send_verification_code_msg(user_hash, to_phone)
                return Response(status=200, data={
                    "message": "Отправлено"
                })
            else:
                return Response(status=400,
                                data={
                                    "message": "У нас нет вашего номера телефона, попробуйте начать регистрацию заново"})
            pass
        else:
            return Response(status=404,
                            data={"message": "Время проверки кодов вышло или такого пользователя вообще не было"})


class IsDoctorVerCodeRight(views.APIView):
    @swagger_auto_schema(
        operation_summary="Проверка верификационного кода для врача и создание аккаунта",
        request_body=VerificationCodeSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Успешно создан'),
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )

            ),
            status.HTTP_400_BAD_REQUEST: "Bad Request",
            status.HTTP_404_NOT_FOUND: "Not Found",
        }
    )
    def post(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            user_hash = validated_data.get("user_hash")
            right_code = cache.get(get_code_cache_name(user_hash))
            if right_code:
                verification_code = validated_data.get("verification_code")
                status_code, msg = doctor_compare_code_and_create(
                    user_hash, right_code, verification_code)
                return Response(status=status_code, data={"message": msg})
            else:
                return Response(status=404,
                                data={"message": "Время проверки кодов вышло или такого пользователя вообще не было"})


class InterviewView(generics.ListCreateAPIView):  # как бы это не называлось
    permission_classes = [AllowAny]
    """Работа с сотрудниками"""
    serializer_class = InterviewSerializer
    queryset = Interview.objects.all()

    def post(self, request):
        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            interview = serializer.save()
            # interview.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city):
        centers = get_centers(city=city)
        logger.debug(centers)
        data = CenterSerializer(centers, many=True).data
        logger.debug(data)
        logger.debug(request.path)
        return Response(data, status=status.HTTP_200_OK)
