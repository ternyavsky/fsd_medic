import logging
from django.core.cache import cache
# REST IMPORTS
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from api.authentication import CustomAuthentication
from db.queries import *
from .serializers import *


logger = logging.getLogger(__name__)

class SaveViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedSerializer

    def get_queryset(self):
        data = cache.get_or_set("saved", get_saved())
        data = data.filter(user=self.request.user)
        logger.debug(self.request.path)
        return data


class LikeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer


    def get_queryset(self):
        logger.debug(self.request.path)
        data = cache.get_or_set("likes", get_likes())
        data =data.filter(user=self.request.user)
        return data
    

class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        notes = cache.get_or_set("notes", get_notes())
        if not self.request.user.is_staff:
            notes = notes.filter(user=self.request.user)
        logger.debug(self.request.path)
        return notes


class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        logger.debug(self.request)
        if self.action == 'list':
            news = cache.get_or_set("news", get_news())
            user = self.request.user
            if user.is_staff:
                logger.info("Admin request")
                return news
            if user.is_authenticated:
                center_news = news.filter(center__in=user.centers.all())
                disease_news = news.filter(disease__in=user.disease.all())
                disease_news = disease_news.annotate(
                    quant_likes=Count("like", distinct=True)
                ).order_by("-quant_likes")
                center_news = center_news.annotate(
                    quant_likes=Count("like", distinct=True)
                ).order_by("-quant_likes")
                news = center_news.union(disease_news)
                logger.debug(self.request.path)
                return news
            else:
                logger.warning("Not authorized")
                return news[:3]
        return get_news()


class SearchView(APIView):
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Получение данных для раздела 'Поиск'")
    def get(self, request, *args, **kwargs):
        clinics = cache.get_or_set("clinics", get_clinics())
        centers = cache.get_or_set("centers", get_centers())
        doctors = cache.get_or_set("doctors", get_doctors())
        search_results = {
            'clinics': clinics,
            'centers': centers,
            'doctors': doctors,
        }
        serializer = SearchSerializer(search_results)
        logger.debug(serializer.data)
        logger.debug(request.path)
        request.session["test"] = serializer.data
        request.session.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorsListView(APIView):
    permissions_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Получение докторов")
    def get(self, request):
        doc = cache.get_or_set("doctors", get_doctors())
        doctors = doc.filter(city=self.request.user.city)
        serializer = DoctorGetSerializer(doctors, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryListView(APIView):

    @swagger_auto_schema(operation_summary="Получение стран")
    def get(self, request):
        countries = cache.get_or_set("countries", get_countries())
        serializer = CountrySerializer(countries, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CityListView(APIView):
    authentication_classes = [CustomAuthentication]
    @swagger_auto_schema(operation_summary="Получение городов")
    def get(self, request):
        cities = cache.get_or_set("cities", get_cities())
        serializer = CitySerializer(cities, many=True)
        logger.debug(serializer.data)
        logger.debug(request.path)
        return Response(serializer.data, status=status.HTTP_200_OK)