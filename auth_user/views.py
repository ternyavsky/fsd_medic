from django.core.cache import cache
from django.db import transaction
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
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
from api.serializers import (
    UserSerializer,
    DiseaseSerializer,
    AccessSerializer,
    CenterSerializer,
    UserUpdateSerializer,
)
from auth_user.serializers import *
from auth_user.service import generate_verification_code, send_email
from auth_user.services.access_services import (
    add_access_service,
    accept_access_service,
    delete_access_service,
)
from auth_user.services.create_user_services import (
    verify_code_service,
    resend_sms_service,
    password_reset_service,
    verify_reset_code_service,
    set_new_password_service,
)
from auth_user.services.email_bind_services import (
    number_bind_service,
    verify_number_bind_service,
)
from db.queries import *

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class LoginView(APIView):
    def post(self, request):
        auth_kwargs = {}
        auth_kwargs["password"] = request.data["password"]
        if "number" in request.data:
            auth_kwargs["number"] = request.data["number"]
        elif "email" in request.data:
            auth_kwargs["email"] = request.data["email"]
        user = None
        try:
            if "number" in auth_kwargs:
                user = User.objects.get(number=auth_kwargs["number"])

            if "email" in auth_kwargs:
                user = get_users(email=auth_kwargs["email"]).first()
            auth = user_authenticate(**auth_kwargs)
            if auth is None:
                raise exceptions.AuthenticationFailed("Incorrect password")
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except:
            raise exceptions.AuthenticationFailed("No active users")


class UserView(generics.ListCreateAPIView):
    """Список пользователей"""

    queryset = get_users()
    # permission_classes = [OnlyCreate]
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sex", "clinic", "disease"]


    @swagger_auto_schema(
        operation_summary="Регистрация",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        code = generate_verification_code()
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()
        send_email.delay(user.email, code)
        user.verification_code = code
        user.save()
        return Response(
            self.serializer_class(user).data, status=status.HTTP_202_ACCEPTED
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, редактирование отдельного пользователя по id"""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        data = self.request.user
        logger.debug(data)
        logger.debug(self.request.path)
        return data

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = UserUpdateSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class GetDiseasesView(APIView):
    permission_classes = [AllowAny]
    """Получение всех заболеваний во время этапа регистрации"""

    @swagger_auto_schema(operation_summary="Получение всех заболеваний")
    def get(self, request):
        diseases = cache.get_or_set("diseases", get_disease())
        serializer = DiseaseSerializer(diseases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# sms-code block ##


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]
    """Проверка кода во время регистрации"""

    @swagger_auto_schema(
        operation_summary="Проверка кода во время регистрации (Пользователь)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "verification_code": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        return verify_code_service(request)


class ResendSmsView(APIView):
    permission_classes = [AllowAny]
    """Переотправка смс, в разделе 'получить смс снова'. Регистрация """

    @swagger_auto_schema(
        operation_summary="Переотправка смс (Пользователь)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"email": openapi.Schema(type=openapi.TYPE_STRING)},
        ),
    )
    def post(self, request):
        return resend_sms_service(request)


# password-reset block#
class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    """Сброс пароля. Этап отправки"""

    @swagger_auto_schema(
        operation_summary="Сброс пароля (Пользователь), отправка кода",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return password_reset_service(request.data)


class VerifyResetCodeView(APIView):
    permission_classes = [AllowAny]
    """Проверка кода для сброса пароля"""

    @swagger_auto_schema(
        operation_summary="Проверка кода для сброса пароля (Пользователь)",
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
        return verify_reset_code_service(request)


class SetNewPasswordView(APIView):
    """Установка нового пароля"""

    @swagger_auto_schema(
        operation_summary="Установка нового пароля (Пользователь)",
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
        return set_new_password_service(request)


# email block
class NumberBindingView(APIView):
    permission_classes = [IsAuthenticated]
    """Привязка номера к аккаунту. Шаг 1 - отправка cмс"""

    @swagger_auto_schema(
        operation_summary="Привязка номера к аккаунту",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["number"],
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request):
        return number_bind_service(request)


class VerifyNumberCodeView(APIView):
    permission_classes = [IsAuthenticated]
    """Проверка кода, для привязки номера"""

    @swagger_auto_schema(
        operation_summary="Проверка кода, для привязки номера",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["number", "number_verification_code"],
            properties={
                "number": openapi.Schema(type=openapi.TYPE_STRING),
                "number_verification_code": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        return verify_number_bind_service(request)


class CreateAdminView(generics.CreateAPIView):
    """Создание админа"""

    permission_classes = [AllowAny]
    queryset = cache.get_or_set("users", get_users())
    serializer_class = AdminSerializer

    @swagger_auto_schema(operation_summary="Создание администратора")
    def post(self, request, *args, **kwargs):
        serializer = AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.debug(serializer.data)
            logger.debug(request.path)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(serializer.errors)
        logger.warning(request.path)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessViewSet(APIView):
    serializer_class = AccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        users = get_users()
        queryset = get_access()
        if self.request.user.is_staff:
            return queryset
        else:
            user = users.filter(id=self.request.user.id).first()
            return queryset.filter(user=user)

    @swagger_auto_schema(operation_summary="Получение доступа пользователя")
    def get(self, request):
        return Response(
            self.serializer_class(self.get_queryset(), many=True).data,
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Добавление доступа пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id"],
            properties={"id": openapi.Schema(type=openapi.TYPE_INTEGER)},
        ),
    )
    def post(self, request):
        """JSON {"id": 22}"""
        add_access_service(request)
        return Response({"message": "created"}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Удаление/Отклонение доступа пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id", "access"],
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "access": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def delete(self, request):
        """JSON {"id": 22, "access": "accept/unaccept"}"""
        delete_access_service(request)
        return Response({"message": "deleted"}, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        operation_summary="Принять доступ пользователя",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id"],
            properties={"id": openapi.Schema(type=openapi.TYPE_INTEGER)},
        ),
    )
    def put(self, request):
        """JSON {"id": 22}"""

        accept_access_service(request)
        return Response({"message": "accepted"}, status=status.HTTP_200_OK)
