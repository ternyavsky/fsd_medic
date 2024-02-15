import logging
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
# REST IMPORTS
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from db.queries import *
from .serializers import *

logger = logging.getLogger(__name__)



class SubscribeViewSet(viewsets.ModelViewSet):
    queryset = Subscribe.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'clinic', 'main_doctor']
    


    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) 


class SaveViewSet(viewsets.ModelViewSet):
    queryset = Saved.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SavedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'news']


    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'news']

    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().prefetch_related('doctors')
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'online', 'problem', 'center', 'clinic', 'special_check', 'status']

    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(user=self.request.user)
        return self.queryset 


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all().prefetch_related('images', 'videos')
    permission_classes = [AllowAny]
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'text', 'center', 'clinic', 'disease']

    def get_queryset(self):
        news = self.queryset.order_by('-created_at')
        user = self.request.user
        if user.is_staff:
            return news 
        if user.is_authenticated:
            clinic_news = news.filter(clinic__in=user.clinic)
            center_news = news.filter(center__in=user.centers.all())
            disease_news = news.filter(disease__in=user.disease.all())
            disease_news = disease_news.annotate(
                    quant_likes=Count("like", distinct=True)
                ).order_by("-quant_likes")
            center_news = center_news.annotate(
                    quant_likes=Count("like", distinct=True)
                ).order_by("-quant_likes")
            clinic_news = clinic_news.annotate(
                quant_likes=Count("like", distinct=True)
                ).order_by("-quant_likes")
            
            news = center_news.union(disease_news, clinic_news)
            return news
        else:
            return news[:3]


class SearchView(APIView):
    serializer_class = SearchSerializer
    permission_classes = [AllowAny]

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
        serializer = self.serializer_class(search_results)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorsListView(APIView):
    queryset = Doctor.objects.all()
    permissions_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country', 'city', 'first_name', 'last_name', 'work_experience',
        'specialization', 'main_status'
    ]

    
    @swagger_auto_schema(operation_summary="Получение докторов")
    def get(self, request):
        doctors = self.queryset.filter(country=self.request.user.country)
        serializer = DoctorGetSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryListView(APIView):
    queryset = Country.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']


    @swagger_auto_schema(operation_summary="Получение стран")
    def get(self, request):
        serializer = CountrySerializer(self.queryset.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CityListView(APIView):
    queryset = City.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']


    @swagger_auto_schema(operation_summary="Получение городов")
    def get(self, request):
        serializer = CitySerializer(self.queryset.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
