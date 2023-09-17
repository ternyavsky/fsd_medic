import logging

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CenterSerializer, UserGetSerializer
from api.models import Interview
from auth_doctor.serializers import InterviewSerializer
from .serializers import DoctorCreateSerializer
from db.queries import *
from rest_framework import views
from .services.doctor_reg_services import doctor_data_passed
from .services.all_service import send_verification_code_msg, get_code_cache_name
from .serializers import VerificationCodeSerializer
logger = logging.getLogger(__name__)


class DoctorDataPast(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = DoctorCreateSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            user_hash = doctor_data_passed(validated_data)
            return Response(status=200,
                            data={"message": "Данные сохранены, ожидаем подтверждение", "user_hash": user_hash})
        else:
            # Если данные не прошли валидацию, верните ошибки
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorRegSmsCodeSend(views.APIView):
    def get(self, request, user_hash):
        user_data = cache.get(user_hash)
        if user_data:
            to_phone = user_data.get("phone_number")
            if to_phone is not None:
                send_verification_code_msg(user_hash, to_phone)
                return Response(status=200)
            else:
                return Response(status=400,
                                data={
                                    "message": "У нас нет вашего номера телефона, попробуйте начать регистрацию заново"})
            pass
        else:
            return Response(status=404,
                            data={"message": "Время проверки кодов вышло или такого пользователя вообще не было"})


class IsDoctorVerCodeRight(views.APIView):
    def post(self, request, user_hash):
        right_code = cache.get(get_code_cache_name(user_hash))
        if right_code:
            serializer = VerificationCodeSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                pass
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
