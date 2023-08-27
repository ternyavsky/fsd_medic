
import logging

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import CenterSerializer, UserGetSerializer
from auth_doctor.serializers import InterviewSerializer
from auth_user.serializers import *
from auth_user.service import generate_verification_code, send_sms
from db.queries import *

logger = logging.getLogger(__name__) 


class DoctorView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    """Работа с сотрудниками"""
    serializer_class = UserGetSerializer
    queryset = get_users()

    def post(self, request):
        serializer = InterviewSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            interview = serializer.save()
            # interview.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CenterRegistrationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city):
        centers = get_centers().filter(city=city)
        logger.debug(centers)
        data = CenterSerializer(centers, many=True).data
        logger.debug(data)
        logger.debug(request.path) 
        return Response(data, status=status.HTTP_200_OK)
