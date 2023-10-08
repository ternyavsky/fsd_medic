from django.core.cache import cache
from django.db import transaction
import logging

from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from api.models import User
from api.permissions import OnlyCreate
from api.serializers import UserSerializer, CenterSerializer, DiseaseSerializer, AccessSerializer
from auth_user.serializers import *
from auth_user.service import generate_verification_code, send_sms, send_reset_sms, send_reset_email, set_new_password, \
    send_verification_email
from auth_user.services.access_services import add_access_service, accept_access_service, delete_access_service
from auth_user.services.create_user_services import create_user_service, verify_code_service, resend_sms_service, \
    password_reset_service, verify_reset_code_service, set_new_password_service
from auth_user.services.email_bind_services import email_bind_service, verify_email_bind_service
from db.queries import *

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class UserView(generics.ListCreateAPIView):
    """Список пользователей"""
    permission_classes = [OnlyCreate]
    serializer_class = UserSerializer

    def get_queryset(self):
        return cache.get_or_set("users", get_users())

    def post(self, request):
        return create_user_service(data=request.data, context={'request': request})


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, редактирование отдельного пользователя по id"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        data = cache.get_or_set("users", get_users())
        data = data.filter(id=self.request.user.id).first()
        logger.debug(data)
        logger.debug(self.request.path)
        return data


class GetDiseasesView(APIView):
    permission_classes = [AllowAny]
    """Получение всех заболеваний во время этапа регистрации"""

    def get(self, request):
        diseases = cache.get_or_set(get_disease())
        serializer = DiseaseSerializer(diseases, many=True)
        logger.debug(serializer.data)
        logger.debug(self.request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


# sms-code block ##

class VerifyCodeView(APIView):
    permission_classes = [AllowAny]
    """Проверка кода во время регистрации"""

    def post(self, request):
        return verify_code_service(request)


class ResendSmsView(APIView):
    permission_classes = [AllowAny]
    """Переотправка смс, в разделе 'получить смс снова'. Регистрация """

    def post(self, request):
        return resend_sms_service(request)


# password-reset block#
class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    """Сброс пароля. Этап отправки"""

    def post(self, request):
        return password_reset_service(request.data)


class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]
    """Проверка кода для сброса пароля"""

    def post(self, request):
        return verify_reset_code_service(request)


class SetNewPasswordView(APIView):
    """Установка нового пароля"""

    def post(self, request):
        return set_new_password_service(request)


# email block
class EmailBindingView(APIView):
    permission_classes = [IsAuthenticated]
    """Привязка почты к аккаунту. Шаг 1 - отправка письма"""

    def post(self, request):
        return email_bind_service(request)


class VerifyEmailCodeView(APIView):
    permission_classes = [IsAuthenticated]
    """Проверка кода из email , для привязки почты"""

    def post(self, request):
        return verify_email_bind_service(request)


class CreateAdminView(generics.CreateAPIView):
    """Создание админа"""
    permission_classes = [AllowAny]
    queryset = cache.get_or_set("users", get_users())
    serializer_class = AdminSerializer

    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.debug(serializer.data)
            logger.debug(request.path)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Получение центров(при регистрации)",
    )
    def get(self, request, city):
        centers = get_centers().filter(city=city)
        logger.debug(centers)
        data = CenterSerializer(centers, many=True).data
        logger.debug(data)
        logger.debug(request.path)
        return Response(data, status=status.HTTP_200_OK)


class AccessViewSet(APIView):
    serializer_class = AccessSerializer

    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        users = cache.get_or_set("users", get_users())
        queryset = cache.get_or_set("access", get_access())
        if self.request.user.is_staff:
            return queryset
        else:
            user = users.filter(id=self.request.user.id).first()
            return queryset.filter(user=user)

    @swagger_auto_schema(operation_summary="Получение доступа пользователя")
    def get(self, request):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Добавление доступа пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id"],
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER)
            }),
    )
    @transaction.atomic
    def post(self, request):
        """ JSON {"id": 22} """
        add_access_service(request)
        return Response({"message": "created"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Удаление/Отклонение доступа пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id", "access"],
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "access": openapi.Schema(type=openapi.TYPE_STRING)
            }),
    )
    @transaction.atomic
    def delete(self, request):
        """ JSON {"id": 22, "access": "accept/unaccept"} """
        delete_access_service(request)
        return Response({"message": "deleted"}, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        operation_summary="Принять доступ пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id"],
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER)
            }),
    )
    @transaction.atomic
    def put(self, request):
        """ JSON {"id": 22} """
        accept_access_service(request)
        return Response({"message": "accepted"}, status=status.HTTP_200_OK)



