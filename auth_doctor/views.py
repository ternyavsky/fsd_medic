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
import hashlib
logger = logging.getLogger(__name__)


class DoctorDataPast(views.APIView):

    def post(self, request, *args, **kwargs):
        serializer = DoctorCreateSerializer(data=request.data)

        if serializer.is_valid():
            #user_data = f"{first_name}_{last_name}_{phone_number}"
            #cache_key = hashlib.sha256(user_data.encode()).hexdigest()
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            # Если данные не прошли валидацию, верните ошибки
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
