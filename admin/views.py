from rest_framework.views import APIView
from datetime import date, datetime
from django.core.cache import cache
from django.db.models import Count, Q, Subquery, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .services.querysets import *

from api.serializers import CenterSerializer
from db.queries import *
from .serializers import *
# Create your views here.


class UserProfileViewset(viewsets.ViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self, pk=None):
        queryset = user_profile_data(pk)
        return queryset

    @swagger_auto_schema(
        operation_summary="Все пользователи/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Конкретный пользователь/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset(pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClinicProfileViewset(viewsets.ModelViewSet):
    serializer_class = ClinicUserProfileSerializer

    def get_queryset(self, pk=None):
        queryset = clinic_profile_data(pk)
        return queryset

    @swagger_auto_schema(
        operation_summary="Все клиники/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_summary="Конкретная клиники/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        queryset = self.get_queryset(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=200) 



class CenterProfileViewset(viewsets.ModelViewSet):
    serializer_class = CenterUserProfileSerializer

    def get_queryset(self, pk=None):
        queryset = center_profile_data(pk)
        return queryset

    @swagger_auto_schema(
        operation_summary="Все центры/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=200)
    
    @swagger_auto_schema(
        operation_summary="Конкретный центр/Админка"
    )
    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        queryset = self.get_queryset(pk=pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=200)


class MainPage(APIView):
    @swagger_auto_schema(
        operation_summary="Сайт и приложение"
    )
    # @method_decorator(cache_page(60 * 60))
    def get(self, request):
        queryset = main_page_data()
        serializer = MainPageSerializer(queryset)
        return Response(serializer.data, status.HTTP_200_OK)


class CityProfileViewset(viewsets.ModelViewSet):
    serializer_class = CityProfileSerializer
    lookup_field = "name"

    def get_queryset(self):
        queryset = city_profile_data()
        return queryset

    @method_decorator(cache_page(60 * 60))
    def list(self, request):
        return super().list(request)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, name):
        return super().retrieve(request, name)


class CountryProfileViewset(viewsets.ModelViewSet):
    serializer_class = CountryCitySerializer
    lookup_field = "name"

    def get_queryset(self, name=None):
        queryset = country_profile_data(name)
        return queryset

    @method_decorator(cache_page(60 * 60))
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, name):
        queryset = self.get_queryset(name)
        serialzier = self.serializer_class(queryset)
        return Response(serialzier.data, status=status.HTTP_200_OK)
