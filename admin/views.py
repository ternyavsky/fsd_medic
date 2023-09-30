from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from django.core.cache import cache
from .serializers import *
from db.queries import *
from django.db.models import Count, Q, OrderBy
from datetime import date
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
# Create your views here.




class UserProfileViewset(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        users = cache.get_or_set("users", get_users())
        users = users.annotate(
            curr_notes = Q()
        )

class ClinicProfileViewset(viewsets.ModelViewSet):
    serializer_class = ClinicProfileSerializer

    def get_queryset(self):
        clinics = cache.get_or_set("clinics", get_clinics())
        clinics = clinics.annotate(
            total_notes=Count("note"),
            reject_notes=Count("note", filter=Q(note__status="Отменена")),
            pass_notes=Count("note", filter=Q(note__status="Подтверждена")),
            visit_online=Count("note", filter=Q(note__online=True, note__time_start__day=date.today().day)),
            visit_offline=Count("note", filter=Q(note__online=False, note__time_start__day=date.today().day))
        )
        return clinics
    
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)

class CenterProfileViewset(viewsets.ModelViewSet):
    serializer_class = CenterProfileSerializer
    
    def get_queryset(self):
        centers = cache.get_or_set("centers", get_centers())
        centers = centers.annotate(
            total_notes=Count("note"),
            reject_notes=Count("note", filter=Q(note__status="Отменена")),
            pass_notes=Count("note", filter=Q(note__status="Подтверждена")),
            visit_online=Count("note", filter=Q(note__online=True, note__time_start__day=date.today().day)),
            visit_offline=Count("note", filter=Q(note__online=False, note__time_start__day=date.today().day))
        )
        return centers

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)



class MainPage(APIView):
    
    def get(self, request):
        diseases = cache.get_or_set("disease", get_disease())
        diseases = diseases.annotate(
            most_count = Count("user")
        )
        diseases = diseases.order_by("-most_count")

        data = {
            "diseases": diseases,
        }
        serializer = MainPageSerializer(data)
        return Response(serializer.data, status.HTTP_200_OK)
    

        

