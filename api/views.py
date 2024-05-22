import abc
import logging
from django.core.cache import cache
from django.db.models import Subquery
from django_filters.rest_framework import DjangoFilterBackend

# REST IMPORTS
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permissions import IsClinicAuthenticated, IsDoctorAuthenticated
from db.queries import *
from .serializers import *

from drf_yasg.utils import swagger_auto_schema


logger = logging.getLogger(__name__)


class AbstractViewSetMeta(abc.ABCMeta, type(viewsets.ModelViewSet)):
    pass


class AbstractViewSet(viewsets.ModelViewSet, metaclass=AbstractViewSetMeta):
    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(user=self.request.user)
        return self.queryset


class SubscribeViewSet(AbstractViewSet):
    queryset = Subscribe.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SubscribeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "clinic", "main_doctor"]


class SaveViewSet(AbstractViewSet):
    queryset = Saved.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SavedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "news"]


class LikeViewSet(AbstractViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "news"]


class NoteViewSet(AbstractViewSet):
    queryset = Note.objects.all().prefetch_related("doctors")
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "user",
        "online",
        "problem",
        "center",
        "clinic",
        "special_check",
        "status",
    ]


class NewsViewSet(AbstractViewSet):
    queryset = News.objects.filter_by_user().prefetch_related(
        "news_images", "news_videos"
    )
    permission_classes = [AllowAny]
    serializer_class = NewsSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ["title", "text", "clinic", "disease"]
    ordering_fields = ["clinic", "disease"]
    filterset_fields = ["title", "text", "clinic", "disease"]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        news = self.queryset.order_by("-created_at")
        user = self.request.user
        if user.is_staff:
            return news
        elif user.is_authenticated:
            return news.filter_by_user(user)
        else:
            return news


class SearchView(APIView):
    serializer_class = SearchSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(operation_summary="Получение данных для раздела 'Поиск'")
    def get(self, request, *args, **kwargs):
        clinics = cache.get_or_set("clinics", get_clinics())
        centers = cache.get_or_set("centers", get_centers())
        doctors = cache.get_or_set("doctors", get_doctors())
        search_results = {
            "clinics": clinics,
            "centers": centers,
            "doctors": doctors,
        }
        serializer = self.serializer_class(search_results)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CountryListView(ListAPIView):
    """List all countries"""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]


class CityListView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["name"]
