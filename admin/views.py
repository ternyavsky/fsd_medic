from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from django.core.cache import cache
from .serializers import *
from db.queries import *
from django.db.models import Count, Q, OrderBy, Subquery, OuterRef, Sum, F
from datetime import date
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
# Create your views here.








class UserProfileViewset(viewsets.ViewSet):
    serializer_class = UserProfileSerializer

    def get_queryset(self, pk=None):
        users = cache.get_or_set("users", get_users())
        users = users.filter(pk=pk) if pk else users
        notes = cache.get_or_set("notes", get_notes())
        curr_notes = notes.filter(user_id__in=Subquery(users.values("id")), status="Passed")
        process_notes = notes.filter(user_id__in=Subquery(users.values("id")), status="In processing")
        result = {
            "users": users,
            "curr_notes": curr_notes,
            "process_notes": process_notes
        }
        return result

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset(pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ClinicProfileViewset(viewsets.ModelViewSet):
    serializer_class = ClinicProfileSerializer

    def get_queryset(self):
        clinics = cache.get_or_set("clinics", get_clinics())
        clinics = clinics.annotate(
            total_notes=Count("note"),
            reject_notes=Count("note", filter=Q(note__status="Rejected")),
            pass_notes=Count("note", filter=Q(note__status="Passed")),
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
            reject_notes=Count("note", distinct=True, filter=Q(note__status="Rejected")),
            pass_notes=Count("note", distinct=True, filter=Q(note__status="Passed")),
            visit_online=Count("note", distinct=True, filter=Q(note__online=True, note__time_start__day=date.today().day)),
            visit_offline=Count("note", distinct=True, filter=Q(note__online=False, note__time_start__day=date.today().day))
        )
        return centers

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))
    def retrieve(self, request, pk):
        return super().retrieve(request, pk)



class MainPage(APIView):
    
    #@method_decorator(cache_page(60 * 60))
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
    


class CityProfileViewset(viewsets.ModelViewSet):
    serializer_class = CityProfileSerializer
    lookup_field = "name"

    def get_queryset(self):
        cities = cache.get_or_set("cities", get_cities())
        cities = cities.annotate(
            quant_centers=Count("center", distinct=True),
            quant_centers_today=Count("center", distinct=True, filter=Q(center__created_at__date=date.today())),
            quant_clinics=Count("clinic", distinct=True),
            quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
            quant_users=Count("user", distinct=True),
            quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
        )
        return cities

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
        cities = cache.get_or_set("cities", get_cities())
        cities = cities.filter(country__name=name) if name else cities
        cities = cities.annotate(
            quant_centers=Count("center", distinct=True),
            quant_centers_today=Count("center", distinct=True, filter=Q(center__created_at__date=date.today())),
            quant_clinics=Count("clinic", distinct=True),
            quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
            quant_users=Count("user", distinct=True),
            quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
        )
        cities = cities.order_by(-(F("quant_centers") + F("quant_clinics") + F("quant_users")))
        countries = cache.get_or_set("countries", get_countries())
        countries = countries.filter(name=name) if name else countries
        countries = countries.annotate(
            quant_clinics=Count("clinic", distinct=True),
            quant_clinics_today=Count("clinic", distinct=True, filter=Q(clinic__created_at__date=date.today())),
            quant_users=Count("user", distinct=True),
            quant_users_today=Count("user", distinct=True, filter=Q(user__created_at__date=date.today())),
            quant_doctors=Count("doctor", distinct=True),
            quant_doctors_today=Count("doctor", distinct=True),
        )
        result = {
            "cities": cities,
            "country": countries
        }
        return result

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
